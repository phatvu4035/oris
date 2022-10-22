import requests
import logging
from lxml import etree
from datetime import datetime
from odoo import models, fields, _, api, tools

_logger = logging.getLogger(__name__)

class ResCurrencyRate(models.Model):
    _inherit = 'res.currency.rate'
    
    @api.model
    def _get_last_update_of_currency_rate(self):
        vnd_currency = self.env.ref('base.VND').exists()
        last_update_record = self.search([('currency_id', '=', vnd_currency.id)], order="name DESC", limit=1)
        return last_update_record
    
    @api.model
    def _convert_string_to_numer_format(self, float_string):
        if ',' in float_string:
            return float_string.replace(',', '')
        else:
            return float_string
        
    @api.model
    def _prepare_vnd_usd_currency_rate_data(self, date, buy_rate, rate):
        vnd_currency = self.env.ref('base.VND').exists()
        
        return {
            'name': date,
            'rate': rate,
            'buy_rate': buy_rate,
            'currency_id': vnd_currency.id
        }

    @api.model
    def _cron_get_vietcombank_currency_rate(self):
        try:
            html_res = requests.get("https://portal.vietcombank.com.vn/Personal/TG/Pages/ty-gia.aspx?devicechannel=default")
            if html_res.status_code == 200:
                parser = etree.HTMLParser(recover=True)
                html_content = etree.HTML(html_res.content , parser)
                time_input = html_content.xpath("//input[@id='txttungay']")
                if time_input:
                    date_str = time_input[0].attrib.get('value')
                    current_date = datetime.strptime(date_str, '%d/%m/%Y').date()
                    last_update_record = self._get_last_update_of_currency_rate()
                    if not last_update_record or current_date > last_update_record.name:
                        rate_html_url = 'https://portal.vietcombank.com.vn/UserControls/TVPortal.TyGia/pListTyGia.aspx'
                        params = {
                            'txttungay': date_str,
                            'BacrhID': 1,
                            'isEn': False
                        }
                        rate_html_res = requests.get(rate_html_url, params)
                        if rate_html_res.status_code == 200:
                            html_content = etree.HTML(rate_html_res.content , parser)
                            table_body = html_content.xpath("//table[@id='ctl00_Content_ExrateView']/tbody")
                            if table_body:
                                tds = table_body[0].getchildren()
                                for td in tds:
                                    if td.getchildren()[1].text == 'USD':
                                        buy_rate = self._convert_string_to_numer_format(td.getchildren()[3].text)
                                        rate = self._convert_string_to_numer_format(td.getchildren()[4].text)
                                        break
    
                            if buy_rate and rate:
                                currency_rate_data = self._prepare_vnd_usd_currency_rate_data(current_date, buy_rate, rate)
                                self.create(currency_rate_data)
        except Exception as e:
            _logger.error("Error when get vietcombank currency rate. Detail error: %s" % e)
            
