import requests
import logging
import urllib.parse
from odoo import models, fields, _, api
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

class ShippingMethod(models.Model):
    _name = 'shipping.method'
    _description = 'Shipping Method'
    
    name = fields.Char(string='Name', required=True)
    shipping_api = fields.Selection([('vietstar', 'Vietstar'), ('viettel', 'Viettel Post')], string='API', required=True)
    state_ids = fields.Many2many('res.country.state', string='Supplied State',
                                 domain="[('id', 'in', available_state_ids)]")
    available_state_ids = fields.Many2many('res.country.state', compute='_compute_available_state_ids')
    
    @api.depends('state_ids')
    def _compute_available_state_ids(self):
        for r in self:
            r.available_state_ids = self.env['res.country.state'].search([('country_id', '=', self.env.user.company_id.country_id.id)]) - r.state_ids

    def action_sync_masterdata(self):
        self.ensure_one()
        if self.shipping_api == 'viettel':
            try:
                base_url = self.env.company.viettelpost_api_url
                if not base_url:
                    raise ValidationError(_("Viettel Post API URL is not set."))
                
                base_url = base_url if base_url.endswith("/") else f"{base_url}/"
                #provinces_url = 'https://partner.viettelpost.vn/v2/categories/listProvinceById'
                provinces_url = urllib.parse.urljoin(base_url, 'categories/listProvinceById')
                provinces_params = {'provinceId': -1}
                provinces_res = requests.get(provinces_url, params=provinces_params)
                province_api_link = provinces_res.url
                _logger.info("Calling API: %s" % province_api_link)
                provinces_res_data = provinces_res.json()
                if provinces_res_data and provinces_res_data.get('status') == 200:
                    province_list = provinces_res_data.get('data')
                    # loop over province list to insert or update data if needed
                    if province_list and len(province_list) > 0:
                        for province in province_list:
                            exists_province = self.env['viettelpost.province'].search([('province_id', '=', province.get('PROVINCE_ID'))])
                            if not exists_province:
                                self.env['viettelpost.province'].create({
                                        'province_id':province.get('PROVINCE_ID'),
                                        'name': province.get('PROVINCE_NAME'),
                                        'code': province.get('PROVINCE_CODE')
                                    })
                            else:
                                exists_province.write({
                                        'province_id':province.get('PROVINCE_ID'),
                                        'name': province.get('PROVINCE_NAME'),
                                        'code': province.get('PROVINCE_CODE')
                                    })
                        # call API to get all districts and then mapping them to provinces
                        #districts_url = 'https://partner.viettelpost.vn/v2/categories/listDistrict'
                        districts_url = urllib.parse.urljoin(base_url, 'categories/listDistrict')
                        districts_params = {'provinceId': -1}
                        districts_res = requests.get(districts_url, params=districts_params)
                        districts_api_link = districts_res.url
                        _logger.info("Calling API: %s" % districts_api_link)
                        districts_res_data = districts_res.json()
                        if districts_res_data and districts_res_data.get('status') == 200:
                            district_list = districts_res_data.get('data')
                            # loop over province list to insert or update data if needed
                            if district_list and len(district_list) > 0:
                                for district in district_list:
                                    exists_district = self.env['viettelpost.district'].search([('district_id', '=', district.get('DISTRICT_ID'))])
                                    if not exists_district:
                                        self.env['viettelpost.district'].create({
                                                'province_id':district.get('PROVINCE_ID'),
                                                'district_id':district.get('DISTRICT_ID'),
                                                'name': district.get('DISTRICT_NAME'),
                                                'value': district.get('DISTRICT_VALUE')
                                            })
                                    else:
                                        exists_district.write({
                                                'province_id':district.get('PROVINCE_ID'),
                                                'district_id':district.get('DISTRICT_ID'),
                                                'name': district.get('DISTRICT_NAME'),
                                                'value': district.get('DISTRICT_VALUE')
                                            })
                        else:
                            raise ValidationError(_("Error when calling to Viettel Post API."))
                        
                else:
                    raise ValidationError(_("Error when calling to Viettel Post API."))
                        
                _logger.info("Complete calling Viettel Post API for master data.")
            except Exception as e:
                _logger.error("Error when calling to sync master data API. Detail error: %s" % e)
                raise
        else:
            _logger.info("Shipping method is not Viettel Post. Skip calling API")
