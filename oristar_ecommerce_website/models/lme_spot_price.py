import requests
import logging
from lxml import etree
from datetime import datetime, timedelta

from odoo import models, fields, _, api

_logger = logging.getLogger(__name__)

class LMESpotPrice(models.Model):
    _inherit = 'lme.spot.price'
    
    @api.model
    def _get_last_update_of_oriental_copper_price(self):
        oriental_copper_markert = self.env.ref('oristar_ecommerce_website.lme_market_oriental').exists()
        copper_material = self.env.ref('oristar_product.product_material_category_00').exists()
        last_update_record = self.search([('lme_market_id', '=', oriental_copper_markert.id), 
                                   ('product_material_category_id', '=', copper_material.id)], order="record_datetime DESC", limit=1)
        return last_update_record
    
    @api.model
    def _convert_string_to_numer_format(self, float_string):
        if ',' in float_string:
            return float_string.replace(',', '')
        else:
            return float_string
        
    @api.model
    def _prepare_oriental_copper_spot_price_data(self, price_data):
        oriental_copper_markert = self.env.ref('oristar_ecommerce_website.lme_market_oriental').exists()
        copper_material = self.env.ref('oristar_product.product_material_category_00').exists()
        currency = self.env.ref('base.USD')
        
        return {
            'record_datetime': price_data[0],
            'price': price_data[1],
            'lme_market_id': oriental_copper_markert.id,
            'product_material_category_id': copper_material.id,
            'currency_id': currency.id
        }
    
    @api.model
    def _cron_get_oriental_copper_price(self):
        try:
            html_res = requests.get("https://www.orientalcopper.com/home.php", verify=False)
            if html_res.status_code == 200:
                parser = etree.HTMLParser(recover=True)
                html_content = etree.HTML(html_res.content , parser)
                time_div = html_content.xpath("//div[@id='leftpanel']/div[2]")
                date_str = ""
                if time_div:
                    time_div_bytes = etree.tostring(time_div[0], encoding='UTF-8', method='text')
                    time_div_text = time_div_bytes.decode('UTF-8')
                    time_content = time_div_text.split('\n')[0].split(' ')[-1:]
                    if time_content:
                        date_str = time_content[0]
                
                data_div = html_content.xpath("//div[@id='leftpanel']/div[3]")
                if data_div and date_str:
                    price_data = []
                    if len(data_div[0].getchildren()) > 2:
                        # process data
                        price_divs = data_div[0].getchildren()[2:]
                        for price_div in price_divs:
                            time_div = price_div.getchildren()[0]
                            value_div = price_div.getchildren()[1]
                            
                            time = time_div.text
                            value = self._convert_string_to_numer_format(value_div.text)
                            date_time_str = "%s %s" % (date_str, time)
                            date_time_value = datetime.strptime(date_time_str, '%d-%b-%Y %H:%M') - timedelta(hours=7)
                            
                            price_data.append((date_time_value, value))
                        
                    if price_data:
                        
                        last_update_record = self._get_last_update_of_oriental_copper_price()
                        
                        data_to_update = []
                        if last_update_record:
                            # only insert price data which has time greater than last update time
                            new_data = list(filter(lambda item: item[0] > last_update_record.record_datetime, price_data))
                            
                            if new_data:
                                for data in new_data:
                                    data_to_update.append(self._prepare_oriental_copper_spot_price_data(data))
                                    
                        else:
                            # insert all price data
                            for data in price_data:
                                data_to_update.append(self._prepare_oriental_copper_spot_price_data(data))
                        
                        if data_to_update:
                            self.create(data_to_update)
                
        except Exception as e:
            _logger.error("Error when get oriental copper price. Detail error: %s" % e)
