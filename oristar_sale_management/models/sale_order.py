import requests
import logging
import urllib.parse
import uuid
import math
from datetime import datetime, timedelta

from odoo import fields, models, _, api
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)
 
class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    def _default_currency_sell_rate(self):
        vnd_currency = self.env.ref('base.VND').exists()
        today_currency_rate = self.env['res.currency.rate'].sudo().search([('name', '=', fields.Date.today()), 
                                                                           ('currency_id', '=', vnd_currency.id)], limit=1)
        if today_currency_rate:
            return today_currency_rate.rate
        else:
            return 0.0
        
    def _default_currency_buy_rate(self):
        vnd_currency = self.env.ref('base.VND').exists()
        today_currency_rate = self.env['res.currency.rate'].sudo().search([('name', '=', fields.Date.today()), 
                                                                           ('currency_id', '=', vnd_currency.id)], limit=1)
        if today_currency_rate:
            return today_currency_rate.buy_rate
        else:
            return 0.0
        
    def _default_delivery_type(self):
        return 'receive_at_customer_warehosue'
    
    district_id = fields.Many2one('res.district', string='Customer District', 
                                  compute='_compute_customer_address_info', readonly=False, store=True)
    township_id = fields.Many2one('res.township', string='Customer Township',
                                  compute='_compute_customer_address_info', readonly=False, store=True)
    state_id = fields.Many2one('res.country.state', string='Customer State',
                               compute='_compute_customer_address_info', readonly=False, store=True)
    customer_email = fields.Char(string='Customer Email', 
                                 compute='_compute_customer_address_info', readonly=False, store=True)
    customer_phone_number = fields.Char(string='Customer Phone Number', 
                                        compute='_compute_customer_address_info', readonly=False, store=True)
    delivery_type = fields.Selection([('receive_at_manufactory', 'Receive at Manufactory'), 
                                      ('receive_at_customer_warehosue' ,'Receive at Customer Warehouse')], 
                                     string='Delivery Type',
                                     default=_default_delivery_type)
    shipping_method_id = fields.Many2one('shipping.method', string='Shipping Method',
                                         compute='_compute_customer_address_info', readonly=False, store=True)
    delivered_date = fields.Date(string='Delivered Date')
    vnd_usd_currency_rate = fields.Float(string='VND-USD Currency Sell Rate', default=_default_currency_sell_rate)
    vnd_usd_currency_rate_buy = fields.Float(string='VND-USD Currency Buy Rate', default=_default_currency_buy_rate)
    shipping_amount = fields.Float(string='Shipping Amount')
    so_erp = fields.Char(string='SO ERP')
    oristar_warehouse_id = fields.Many2one('oristar.warehouse', string='Warehouse',
                                           compute='_compute_customer_address_info', readonly=False, store=True)
    erp_id = fields.Char(string='ERP ID', readonly=True, default=lambda self: uuid.uuid4())
    payment_method = fields.Selection([('debt', 'Debt'),
                                       ('pay', 'Pay'),
                                       ('advan', 'Advance')], string='Payment method')
    
    erp_order_status = fields.Selection([('quote', 'Quote'), ('confirm', 'Confirmed'), ('produce', 'Produce'),
                                         ('delivery', 'Delivery'), ('delivered', 'Delivered'), ('cancel', 'Canceled')], readonly=False,
                                         string='ERP Order Status')
    computed_erp_order_status = fields.Char(string='Computed ERP Order Status', compute='_compute_computed_erp_order_status')
    create_custom_declaration = fields.Boolean(string='Create Custom Declaration')
    custom_declaration_unit_price = fields.Float(string='Custom Declaration Unit Price', default=800000)
    no_of_custom_declaration = fields.Integer(string='Number of Custom Declaration', compute='_compute_custom_declaration_info')
    total_custom_declaration_amount = fields.Float(string='Custom Declaration Amount', compute='_compute_custom_declaration_info')
    customer_type = fields.Selection(string='Customer Type', related='partner_id.customer_type')
    
    @api.constrains('erp_id')
    def _check_erp_id(self):
        for r in self:
            existing_record = self.search([('erp_id', '=', r.erp_id), ('id', '!=', r.id)])
            if existing_record:
                raise ValidationError(_("ERP ID must be unique."))
    
    @api.depends('order_line.price_total')
    def _amount_all(self):
        for order in self:
            amount_untaxed = amount_tax = 0.0
            for line in order.order_line:
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax
            order.update({
                'amount_untaxed': amount_untaxed,
                'amount_tax': amount_tax,
                'amount_total': amount_untaxed + amount_tax + order.total_custom_declaration_amount,
            })
        
    @api.depends('custom_declaration_unit_price', 'order_line', 'create_custom_declaration')
    def _compute_custom_declaration_info(self):
        for r in self:
            if r.create_custom_declaration:
                r.no_of_custom_declaration = math.ceil(len(r.order_line.filtered(lambda line: not line.display_type)) / 50)
            else:
                r.no_of_custom_declaration = 0
            r.total_custom_declaration_amount = r.no_of_custom_declaration * r.custom_declaration_unit_price
            r._amount_all()
            
    def _compute_computed_erp_order_status(self):
        erp_order_status = self.env['order.processing.status'].sudo().search([('erp_id', 'in', self.mapped('erp_id'))], order='updated_time desc')
        for r in self:
            found_erp_status = erp_order_status.filtered(lambda os: os.erp_id == r.erp_id).sorted(lambda x: x.updated_time, reverse=True)
            if found_erp_status and r.state not in ['draft', 'sent']:
                lastest_status = found_erp_status[0].status_code
                if lastest_status == 5:
                    r.computed_erp_order_status = 'delivered'
                    r.erp_order_status = 'delivered'
                elif lastest_status == 4:
                    r.computed_erp_order_status = 'delivery'
                    r.erp_order_status = 'delivery'
                elif lastest_status == 3:
                    r.computed_erp_order_status = 'produce'
                    r.erp_order_status = 'produce'
                elif lastest_status == 2:
                    r.computed_erp_order_status = 'confirm'
                    r.erp_order_status = 'confirm'
                elif lastest_status == 1:
                    r.computed_erp_order_status = 'quote'
                    r.erp_order_status = 'quote'
                else:
                    r.computed_erp_order_status = ''
                    r.erp_order_status = 'quote'
            else:
                r.erp_order_status = 'quote'
                r.computed_erp_order_status = ''
    
    @api.depends('partner_shipping_id')
    def _compute_customer_address_info(self):
        for r in self:
            r.district_id = r.partner_shipping_id.district_id
            r.township_id = r.partner_shipping_id.township_id
            r.state_id = r.partner_shipping_id.state_id
            r.customer_email = r.partner_shipping_id.email
            r.customer_phone_number = r.partner_shipping_id.mobile if r.partner_shipping_id.mobile else r.partner_shipping_id.phone
            r.oristar_warehouse_id = self.env['oristar.warehouse'].search([('supplied_state_ids', 'in', [r.state_id.id])], limit=1)
            r.shipping_method_id = self.env['shipping.method'].search([('state_ids', 'in', [r.state_id.id])], limit=1)
            

    def update_prices(self):
        """ Override this method to set price unit to 0.0, we will calculate it later
        """
        self.ensure_one()
        result = super(SaleOrder, self).update_prices()
        lines_to_update = []
        for line in self.order_line.filtered(lambda line: not line.display_type):
            lines_to_update.append((1, line.id, {'price_unit': 0.0}))
        self.update({'order_line': lines_to_update})
        return result

    @api.model
    def _parse_unicode_to_urlencode(self, uni_str):
        return urllib.parse.quote(uni_str)
    
    def _build_vietstar_request_params(self, from_code, to_code, total_weight):
        price_method_folder = self.env.company.price_method_folder
        params = {
            'date': price_method_folder,
            'file': 'vietstar.xlsx',
            'from': from_code,
            'b': to_code,
            'c': total_weight
        }
        return params
    
    def _get_shipping_amount_based_on_vietstar(self, from_code, to_code, total_weight):
        pricing_url = self.env.company.price_service_url
        req_params = self._build_vietstar_request_params(from_code, to_code, total_weight)
        urban_zone_price = 0.0
        countryside_zone_price = 0.0
        try:
            price_res = requests.get(pricing_url, params=req_params)
            api_link= price_res.url
            _logger.info("Calling API: %s" % api_link)
            price_res_data = price_res.json()
            
            res_message = price_res_data.get('Message', False)
            if res_message and res_message == 'OK':
                urban_zone_price = float(price_res_data.get('ChiPhiVanChuyenThiXa'))
                countryside_zone_price = float(price_res_data.get('ChiPhiVanChuyenNgoaiThanh'))
                
            else:
                _logger.error("Error when calling to shipping API. Detail error: %s" % res_message)
                raise Exception(_("Error when calling to shipping API."))
        except Exception as e:
            _logger.error("Error when calling to shipping API. Detail error: %s" % e)
            raise Exception(_("Error when calling to shipping API."))
        return (urban_zone_price, countryside_zone_price)
    
    def _split_shipping_amount_to_order_line(self, total_weight):
        self.ensure_one()
        lines_to_update = []
        for line in self.order_line.filtered(lambda line: not line.display_type):
            if line.product_weight > 0:
                line_shipping_amount = (line.product_weight/total_weight) * self.shipping_amount
                lines_to_update.append((1, line.id, {'shipping_amount': line_shipping_amount}))
        
        if lines_to_update:
            self.update({'order_line': lines_to_update})
    
    def action_calculate_shipping_price(self):
        self.ensure_one()
        if self.delivery_type == 'receive_at_customer_warehosue' and self.shipping_method_id:
            shipping_amount = 0.0
            # call API to get shipping amount
            if self.shipping_method_id.shipping_api == 'vietstar':
                # HungYen has code is VN-66
                # Hanoi has code is VN-HN
                # HCM has code is VN-SG
                from_code = ''
                to_code = ''
                if self.oristar_warehouse_id.located_state_id.code == 'VN-66':
                    from_code = 'hy'
                    to_code = self.state_id.vietstar_id
                elif self.oristar_warehouse_id.located_state_id.code == 'VN-HN':
                    from_code = 'hn'
                    to_code = self.state_id.vietstar_id
                elif self.oristar_warehouse_id.located_state_id.code == 'VN-SG':
                    from_code = 'hcm'
                    to_code = self.state_id.vietstar_id_sg
                else:
                    raise ValidationError(_("Warehouse located in state, which is not supported by system."))
                
                total_weight = sum(self.order_line.filtered(lambda line: not line.display_type).mapped('product_weight'))
                if total_weight <= 0:
                    raise ValidationError(_("SO doesn't have valid total weight."))
                
                if not to_code:
                    raise ValidationError(_("Delivery address doesn't have Vietstar state code."))
                
                int_total_weight = math.ceil(total_weight)
                (urban_zone_price, countryside_zone_price) = self._get_shipping_amount_based_on_vietstar(from_code, to_code, int_total_weight)
                if self.district_id.urban_zone:
                    shipping_amount = urban_zone_price
                else:
                    shipping_amount = countryside_zone_price
                    
                self.update({'shipping_amount': shipping_amount})
                
                self._split_shipping_amount_to_order_line(total_weight)
                
            elif self.shipping_method_id.shipping_api == 'viettel':
                total_weight = sum(self.order_line.filtered(lambda line: not line.display_type).mapped('product_weight'))
                if total_weight <= 0:
                    raise ValidationError(_("SO doesn't have valid total weight.")) 
                int_total_weight = math.ceil(total_weight * 1000)
                
                # find sender and receiver province and district id
                sender_province_id = self.env['viettelpost.province'].search([('mapped_state_id', '=', self.oristar_warehouse_id.located_state_id.id)], limit=1)
                sender_district_id = self.env['viettelpost.district'].search([('mapped_district_id', '=', self.oristar_warehouse_id.located_district_id.id)], limit=1)
                
                receiver_province_id = self.env['viettelpost.province'].search([('mapped_state_id', '=', self.state_id.id)], limit=1)
                receiver_district_id = self.env['viettelpost.district'].search([('mapped_district_id', '=', self.district_id.id)], limit=1)
                
                if not sender_province_id:
                    raise ValidationError(_("Could not find Viettel Post province for sender."))
                
                if not sender_district_id:
                    raise ValidationError(_("Could not find Viettel Post district for sender."))
                
                if not receiver_province_id:
                    raise ValidationError(_("Could not find Viettel Post province for receiver."))
                
                if not receiver_district_id:
                    raise ValidationError(_("Could not find Viettel Post district for receiver."))
                
                base_url = self.env.company.viettelpost_api_url
                user_name = self.env.company.viettelpost_user_name
                password = self.env.company.viettelpost_password
                
                if not base_url:
                    raise ValidationError(_("Viettel Post API URL is not set."))
                
                if not user_name or not password:
                    raise ValidationError(_("Viettel Post API username/password is not set."))
                
                base_url = base_url if base_url.endswith("/") else f"{base_url}/"
                # login_url = 'https://partner.viettelpost.vn/v2/user/Login'
                login_url = urllib.parse.urljoin(base_url, 'user/Login')
                login_data = {
                    "USERNAME": user_name,
                    "PASSWORD": password
                }
                login_response = requests.post(login_url, json=login_data)
                login_api_link = login_response.url
                _logger.info("Calling API: %s" % login_api_link)
                login_res_data = login_response.json()
                if login_res_data and login_res_data.get('status') == 200:
                    access_token = login_res_data.get('data').get('token')
                    
                    if access_token:
                        # price_url = 'https://partner.viettelpost.vn/v2/order/getPrice'
                        price_url = urllib.parse.urljoin(base_url, 'order/getPrice')
                        price_data = {
                              "PRODUCT_WEIGHT":int_total_weight,
                              "PRODUCT_PRICE":"",
                              "MONEY_COLLECTION":"",
                              "ORDER_SERVICE_ADD":"",
                              "ORDER_SERVICE":"VCN",
                              "SENDER_PROVINCE":str(sender_province_id.province_id),
                              "SENDER_DISTRICT":str(sender_district_id.district_id),
                              "RECEIVER_PROVINCE":str(receiver_province_id.province_id),
                              "RECEIVER_DISTRICT":str(receiver_district_id.district_id),
                              "PRODUCT_TYPE":"HH",
                              "NATIONAL_TYPE":1
                        }
                        hed = {'Authorization': 'Bearer ' + access_token}
                        price_response = requests.post(price_url, json=price_data, headers=hed)
                        price_res_data = price_response.json()
                        if price_res_data and price_res_data.get('status') == 200:
                            shipping_amount = price_res_data.get('data').get('MONEY_TOTAL')
                            if shipping_amount and shipping_amount > 0:
                                self.update({'shipping_amount': shipping_amount})
                    
                                self._split_shipping_amount_to_order_line(total_weight)
                            else:
                                raise ValidationError(_("Shipping amount from Viettel Post API is invalid"))
                        else:
                            raise ValidationError(_("Get shipping price from Viettel Post API failed. Detail error: %s", price_res_data.get('message')))
                else:
                    raise ValidationError(_("Viettel Post API authentication failed."))
            else:
                shipping_amount = 0.0
    
    def action_calculate_price(self):
        self.ensure_one()
        lines_to_update = []
        for line in self.order_line.filtered(lambda line: not line.display_type):
            if line.product_id.price_method_group == 'base':
                lines_to_update.append((1, line.id, {'price_unit': line.product_id.list_price,
                                                     'product_weight': line.product_id.product_weight * line.product_uom_qty,
                                                     'api_link': ''}))
            else:
                options = {}
                options['long'] = line.product_long
                options['width'] = line.product_width
                options['thickness'] = line.product_thickness
                options['qty'] = line.product_uom_qty
                options['weight'] = line.product_weight
                options['buy_rate'] = self.vnd_usd_currency_rate_buy
                options['sell_rate'] = self.vnd_usd_currency_rate
                options['milling_method'] = line.milling_method
                options['milling_faces'] = line.milling_faces
            
                (price_unit, weight, api_link, milling_fee) = self.calculate_price_info_from_pricing_engine(line.product_id, self.pricelist_id, options,
                                                                                               line.order_partner_id)
                if line.product_id.price_method_group != 'roll':
                    if milling_fee > 0:
                        lines_to_update.append((1, line.id, {'price_unit': price_unit,
                                                             'product_weight': weight,
                                                             'api_link': api_link,
                                                             'milling_fee': milling_fee}))
                    else:
                        lines_to_update.append((1, line.id, {'price_unit': price_unit,
                                                             'product_weight': weight,
                                                             'api_link': api_link}))
                else:
                    lines_to_update.append((1, line.id, {'price_unit': price_unit,
                                                         'api_link': api_link}))
                
        self.update({'order_line': lines_to_update})
        
    @api.model
    def _get_closest_pricelist_item(self, product, pricelist_items):
        closest_item = None
        has_product_tmpl_item = False
        has_product_categ_item = False
        
        for item in pricelist_items:
            if item.applied_on == '0_product_variant':
                if item.product_id == product:
                    closest_item = item
                    break
            elif item.applied_on == '1_product':
                if item.product_tmpl_id == product.product_tmpl_id:
                    if not has_product_tmpl_item:
                        has_product_tmpl_item = True
                        closest_item = item
            elif item.applied_on == '2_product_category':
                if item.categ_id == product.categ_id:
                    if not has_product_tmpl_item and not has_product_categ_item:
                        closest_item = item
                        has_product_categ_item = True
            else:
                if not has_product_tmpl_item and not has_product_categ_item:
                    closest_item = item
        
        return closest_item
    
    @api.model
    def _get_last_update_lme_spot_price(self, product, market):
        # we will use market later after confirm logic to set market for spot price
        # last_update_record = self.env['lme.spot.price'].search([('lme_market_id', '=', market.id),
        #                                                         ('product_material_category_id', '=', product.product_material_category_id.id)],
        #                                                         order="record_datetime DESC", limit=1)
        last_update_record = self.env['lme.spot.price'].search([('product_material_category_id', '=', product.product_material_category_id.id)],
                                                                order="record_datetime DESC", limit=1)
        if last_update_record and last_update_record.record_datetime:
            if fields.Datetime.now() - last_update_record.record_datetime <= timedelta(minutes=40):
                return last_update_record
        
        return None
    
    def _get_n_number_of_lme_price(self, product, market, n_avg):
        n_lme_price = self.env['lme.price'].sudo().search([('product_material_id', '=', product.product_material_id.id),
                                                            ('lme_market_id', '=', market.id)],
                                                            order='record_datetime DESC', limit=n_avg)
        return n_lme_price
    
    @api.model
    def _build_pp3_request_params_based_on_product(self, product, options, pricelist_item):
        price_method_folder = self.env.company.price_method_folder
        if not product.default_code:
            raise UserError(_("The product %s missing internal reference", product.name))
        
        if not pricelist_item.lme_market_id:
            raise UserError(_("The pricelist item %s for pp3 missing LME market", pricelist_item.display_name))
        
        if not pricelist_item.n_average or pricelist_item.n_average <= 0:
            raise UserError(_("The pricelist item %s for pp3 missing N average", pricelist_item.display_name))
        
        # lme_spot_price = 0.0
        lme_n_avg_price = 0.0
        
        # last_update_lme_spot_price = self._get_last_update_lme_spot_price(product, pricelist_item.lme_market_id)
        # if not last_update_lme_spot_price:
        #     raise OutOfServiceException(_("LME spot price is out of service. We need to have latest LME spot price in 40 minutes."))
        # else:
        #     lme_spot_price = last_update_lme_spot_price.price
            
        n_number_of_lme_price = self._get_n_number_of_lme_price(product, pricelist_item.lme_market_id, pricelist_item.n_average)
        if not n_number_of_lme_price:
            raise UserError(_("There is not setting for LME price"))
        else:
            lme_n_avg_price = sum(n_number_of_lme_price.mapped('close_price'))/pricelist_item.n_average
        
        params = {
            'date': price_method_folder,
            'file': pricelist_item.price_file_id.name,
            'sheet': product.default_code,
            # 'l': lme_spot_price,
            'm': lme_n_avg_price,
            'r': options.get('buy_rate'),
            's': options.get('sell_rate')
        }
        return params
    
    @api.model
    def _build_pp2_request_params_based_on_product(self, product, options, file):
        price_method_folder = self.env.company.price_method_folder
        if not product.default_code:
            raise UserError(_("The product %s missing internal reference", product.name))
        
        long = options.get('long')
        width = options.get('width')
        if not long or not width:
            raise UserError(_("Size 2 and Size 3 are required."))
        
        square = long * width / 10**2
        shape = 'bar' if long > width * 4 else 'plate'
        params = {
            'date': price_method_folder,
            'file': file.name,
            'k': product.default_code,
            'l': square,
            # 'n': shape,
            'o': options.get('qty')
        }
        return params

    @api.model
    def _build_pp1_request_params_based_on_product(self, product, options, file):
        price_method_folder = self.env.company.price_method_folder
        price_method_group = product.price_method_group
        if not price_method_group:
            raise UserError(_("The price method type of product %s is invalid", product.name))
            
        params = {
            # 'date': self._parse_unicode_to_urlencode(price_method_folder),
            # 'file': self._parse_unicode_to_urlencode(file.name),
            # 'sheet': self._parse_unicode_to_urlencode(product.price_method_type)
            'date': price_method_folder,
            'file': file.name,
            'sheet': product.price_method_type
        }
        if price_method_group == 'bar':
            # for bar product
            params['d'] = options.get('cost')
            if options.get('thickness'):
                params['e'] = options.get('thickness')
            if options.get('width'):
                params['f'] = options.get('width')
            if options.get('long'):
                params['g'] = options.get('long')
            params['h'] = options.get('qty')
            params['s'] = options.get('tsln')
            params['i'] = options.get('balance')
            if product.product_detailed_shape_id.shape_category == 'circle':
                params['c'] = 'circle'
            elif product.product_detailed_shape_id.shape_category == 'cnvcv':
                params['c'] = 'cnvcv'
            elif product.product_detailed_shape_id.shape_category == 'cnvct':
                params['c'] = 'cnvct'
            elif product.product_detailed_shape_id.shape_category == 'lg':
                params['c'] = 'lg'
            elif product.product_detailed_shape_id.shape_category == 'ot':
                params['c'] = 'ot'
            elif product.product_detailed_shape_id.shape_category == 'ov':
                params['c'] = 'ov'
            else:
                raise UserError(_("There is not shape category for detailed shape %s.", product.product_detailed_shape_id.name))
            if options.get('milling_method') and options.get('milling_method') != 'no':
                params['a'] = options.get('milling_method')
                if options.get('milling_method') == 'PHAY2F' and options.get('milling_faces') not in ('KT1', 'KT2', 'KT3'):
                    raise ValidationError(_("PHAY2F doesn't allow %s faces", options.get('milling_faces')))
                if options.get('milling_method') == 'PHAY4F' and options.get('milling_faces') not in ('KT2andKT3', 'KT1andKT3', 'KT1andKT2'):
                    raise ValidationError(_("PHAY4F doesn't allow %s faces", options.get('milling_faces')))
                if options.get('milling_method') != 'PHAY6F':
                    params['ai'] = options.get('milling_faces')
            else:
                params['a'] = 'No'
            if options.get('size_change'):
                params['ak'] = 'G'
            else:
                params['ak'] = 'N'
        
        elif price_method_group == 'plate':
            # for plate product
            params['d'] = options.get('cost')
            if options.get('thickness'):
                params['e'] = options.get('thickness')
            if options.get('width'):
                params['f'] = options.get('width')
            if options.get('long'):
                params['g'] = options.get('long')
            params['h'] = options.get('qty')
            params['s'] = options.get('tsln')
            params['i'] = options.get('balance')
            if options.get('milling_method') and options.get('milling_method') != 'no':
                params['a'] = options.get('milling_method')
                if options.get('milling_method') == 'PHAY2F' and options.get('milling_faces') not in ('KT1', 'KT2', 'KT3'):
                    raise ValidationError(_("PHAY2F doesn't allow %s faces", options.get('milling_faces')))
                if options.get('milling_method') == 'PHAY4F' and options.get('milling_faces') not in ('KT2andKT3', 'KT1andKT3', 'KT1andKT2'):
                    raise ValidationError(_("PHAY4F doesn't allow %s faces", options.get('milling_faces')))
                if options.get('milling_method') != 'PHAY6F':
                    params['ac'] = options.get('milling_faces')
            else:
                params['a'] = 'No'
            
            if options.get('size_change'):
                params['ae'] = 'G'
            else:
                params['ae'] = 'N'
        
        else:
            # for roll product
            params['c'] = options.get('cost')
            if options.get('thickness'):
                params['d'] = options.get('thickness')
            if options.get('width'):
                params['e'] = options.get('width')
            params['f'] = options.get('weight')
            params['n'] = options.get('tsln')
            params['g'] = options.get('balance')
        
        return params
    
    @api.model
    def _get_price_info_based_on_pp1(self, product, options, pricelist_item, pricing_url):
        price_unit = 0.0
        weight = 0.0
        milling_fee = 0.0
        api_link = ''
        
        req_params = self._build_pp1_request_params_based_on_product(product, options, pricelist_item.price_file_id)
        try:
            price_res = requests.get(pricing_url, params=req_params)
            api_link= price_res.url
            _logger.info("Calling API: %s" % api_link)
            price_res_data = price_res.json()
            
            
            res_message = price_res_data.get('Message', False)
            if res_message and res_message == 'OK':
                if price_res_data.get('DonGiaTheoTSLN'):
                    price_unit = float(price_res_data.get('DonGiaTheoTSLN'))
                    if price_unit < 0:
                        raise ValidationError(_("Calculated price is not valid. Please contact to administrator."))
                    
                if price_res_data.get('SoKg'):
                    weight = float(price_res_data.get('SoKg'))
                    if weight < 0:
                        raise ValidationError(_("Calculated price is not valid. Please contact to administrator."))
                    
                if price_res_data.get('PHAY') and price_res_data.get('PHAY') != 'No' and price_res_data.get('PHAY') in ('PHAY2F', 'PHAY4F', 'PHAY6F'):
                    if price_res_data.get('PhayStatus') == 'OK' and price_res_data.get('PhiPhay') and price_res_data.get('PhiPhay') != '-':
                        milling_fee = float(price_res_data.get('PhiPhay'))
                        if milling_fee < 0:
                            raise ValidationError(_("Calculated price is not valid. Please contact to administrator."))
                    else:
                        raise ValidationError(_("Can't apply milling on this product."))
                    
            else:
                _logger.error("Error when calling to pricing API. Detail error: %s" % res_message)
                raise ValidationError(_("Error when calling to pricing API."))
        except Exception as e:
            _logger.error("Error when calling to pricing API. Detail error: %s" % e)
            raise

        return (price_unit, weight, api_link, milling_fee)
    
    @api.model
    def _get_price_info_based_on_pp2(self, product, options, pricelist_item, pricing_url):
        frame_price = 0.0
        api_link = ''
        
        req_params = self._build_pp2_request_params_based_on_product(product, options, pricelist_item.price_file_id)
        try:
            price_res = requests.get(pricing_url, params=req_params)
            api_link= price_res.url
            _logger.info("Calling API: %s" % api_link)
            price_res_data = price_res.json()
            
            res_message = price_res_data.get('Message', False)
            if res_message and res_message == 'OK':
                if price_res_data.get('FramePrice'):
                    frame_price = float(price_res_data.get('FramePrice'))
                    if frame_price < 0:
                        raise ValidationError(_("Calculated price is not valid. Please contact to administrator."))
                else:
                    raise ValidationError(_("Calculated price is not valid. Please contact to administrator."))
            else:
                _logger.error("Error when calling to pricing API. Detail error: %s" % res_message)
                raise ValidationError(_("Error when calling to pricing API."))
        except Exception as e:
            _logger.error("Error when calling to pricing API. Detail error: %s" % e)
            raise
        
        return (frame_price, api_link)
    
    def _get_price_info_based_on_pp3(self, product, options, pricelist_item, pricing_url):
        used_price = 0.0
        api_link = ''
        
        req_params = self._build_pp3_request_params_based_on_product(product, options, pricelist_item)
        try:
            price_res = requests.get(pricing_url, params=req_params)
            api_link= price_res.url
            _logger.info("Calling API: %s" % api_link)
            price_res_data = price_res.json()
            
            res_message = price_res_data.get('Message', False)
            if res_message and res_message == 'OK':
                if price_res_data.get('DonGia'):
                    used_price = float(price_res_data.get('DonGia'))
                    if used_price < 0:
                        raise ValidationError(_("Calculated price is not valid. Please contact to administrator."))
                else:
                    raise ValidationError(_("Calculated price is not valid. Please contact to administrator."))
            else:
                _logger.error("Error when calling to pricing API. Detail error: %s" % res_message)
                raise ValidationError(_("Error when calling to pricing API."))
        except Exception as e:
            _logger.error("Error when calling to pricing API. Detail error: %s" % e)
            raise
        
        return (used_price, api_link)
    
    def check_customer_credit_limit(self):
        self.ensure_one()
        customer_credit_limit = self.partner_id.customer_credit_limit_ids.filtered(lambda cl: cl.currency_id == self.currency_id)
        if customer_credit_limit and len(customer_credit_limit) >= 1:
            if len(customer_credit_limit) == 1:
                not_confirmed_so = self.search([('partner_id', '=', self.partner_id.id),
                                                ('state', 'in', ['draft', 'sent']),
                                                ('id', '!=', self.id)])
                total_amount_unchecked = sum(not_confirmed_so.mapped('amount_total'))
                if self.amount_total + customer_credit_limit.credit + total_amount_unchecked > customer_credit_limit.credit_limit:
                    return False
                else:
                    return True
            else:
                raise ValidationError(_("Customer has more than 1 credit limit for currency %s." % self.currency_id))
        else:
            return True
        
    
    def action_confirm(self):
        return super(SaleOrder, self).action_confirm()
        # # check customer credit limit
        # if self.check_customer_credit_limit():
        #     return super(SaleOrder, self).action_confirm()
        # else:
        #     raise ValidationError(_("Customer credit limit exceed threshold"))
        
    def action_cancel(self):
        if self.erp_order_status in ['produce', 'delivery', 'delivered']:
            raise ValidationError(_("Can not cancel order which already in processed."))
        return super(SaleOrder, self).action_cancel()

    @api.model
    def calculate_price_info_from_pricing_engine(self, product, pricelist, options, partner):
        """ Calculate price unit, sub-total and weight of product based on pass parameters
            
            @param product: selected product
            @param pricelist: selected pricelist
            @param options: dictionary which provides customized index requested by user
                            example: {'width':10, 'long':10, 'qty':20, 'thickness': 1.2, 'milling_method': 'PHAY2F', 'milling_faces': 'KT1'}
            @param partner: partner who oder this product
            @return: tuple of price unit, weight and api_link
        """
        price_unit = 0.0
        weight = 0.0
        api_link = ''
        milling_fee = 0.0
        pricing_url = self.env.company.price_service_url
        
        # handle for new price method, where we calculate price of product based on its price unit and weight only
        if product.price_method_group == 'base':
            weight = product.product_weight * options.get('qty')
            price_unit = product.list_price
            return (price_unit, weight, api_link, milling_fee)
        
        # support client calculate price for product while product size is not changed
        size_changed = False
        if product.product_basic_shape_id.has_size1:
            if product.product_thickness != options.get('thickness'):
                size_changed = True
                
        if product.product_basic_shape_id.has_size3:
            if product.product_long != options.get('long'):
                size_changed = True
                
        if product.product_basic_shape_id.has_size2:
            if product.product_width != options.get('width'):
                size_changed = True
        
        if not size_changed:
            options.update({
                'size_change': False
            })
        else:
            options.update({
                'size_change': True
            })
        
        customer_balance_date_number = 0
        if partner.credit_time_days:
            customer_balance_date_number = partner.credit_time_days
        options.update({
            'balance': customer_balance_date_number,
            'cost': product.list_price
        })
        
        # if product is not in pricelist, raise UserError
        pp1_pricelist_items = pricelist.item_ids.filtered(lambda item: item.price_method_code == 'pp1')
        pp2_pricelist_items = pricelist.item_ids.filtered(lambda item: item.price_method_code == 'pp2')
        pp3_pricelist_items = pricelist.item_ids.filtered(lambda item: item.price_method_code == 'pp3')
        
        pp1_pricelist_item = self._get_closest_pricelist_item(product, pp1_pricelist_items)
        pp2_pricelist_item = self._get_closest_pricelist_item(product, pp2_pricelist_items)
        pp3_pricelist_item = self._get_closest_pricelist_item(product, pp3_pricelist_items)
        
        if not pp1_pricelist_item:
            raise UserError(_("There is not default pricelist item defined for product %s", product.name))
        
        found_profit_margin = 0
        size1_val = options.get('thickness')
        if pp1_pricelist_item.profit_margin_ids and size1_val:
            for margin in pp1_pricelist_item.profit_margin_ids:
                if size1_val <= margin.size1_max and size1_val >= margin.size1_min and margin.profit_margin:
                    if found_profit_margin < margin.profit_margin:
                        found_profit_margin = margin.profit_margin
                        
        if found_profit_margin == 0:
            selected_profit_margin = pp1_pricelist_item.tsln
        else:
            selected_profit_margin = found_profit_margin
                        
        
        if pp3_pricelist_item:
            # call API to get unit price
            (price_unit, api_link_pp3) = self._get_price_info_based_on_pp3(product, options, pp3_pricelist_item, pricing_url)
                
            # use frame price as cost to call pp1 API
            options.update({
                'tsln': selected_profit_margin/100
            })
            (price_unit_unused, weight, api_link_pp1, milling_fee) = self._get_price_info_based_on_pp1(product, options, pp1_pricelist_item, pricing_url)
            api_link = api_link_pp3 + ';' + api_link_pp1
            if milling_fee and milling_fee > 0:
                price_unit += milling_fee
            return (price_unit, weight, api_link, milling_fee)
        
        if pp2_pricelist_item:
            # call API to get frame price
            (price_unit, api_link_pp2) = self._get_price_info_based_on_pp2(product, options, pp2_pricelist_item, pricing_url)
                
            # use frame price as cost to call pp1 API
            options.update({
                'tsln': selected_profit_margin/100
            })
            (price_unit_unused, weight, api_link_pp1, milling_fee) = self._get_price_info_based_on_pp1(product, options, pp1_pricelist_item, pricing_url)
            api_link = api_link_pp2 + ';' + api_link_pp1
            if milling_fee and milling_fee > 0:
                price_unit += milling_fee
            return (price_unit, weight, api_link, milling_fee)
        
        if pp1_pricelist_item:
            options.update({
                'tsln': selected_profit_margin/100
            })
            (price_unit, weight, api_link, milling_fee) = self._get_price_info_based_on_pp1(product, options, pp1_pricelist_item, pricing_url)
            return (price_unit, weight, api_link, milling_fee)
        
class OutOfServiceException(Exception):
    pass
