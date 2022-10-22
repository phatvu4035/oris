# -*- coding: utf-8 -*-
from werkzeug.exceptions import Forbidden, NotFound
import json

from odoo import http, fields
from odoo.http import request
from odoo import _
from odoo.addons.website_sale.controllers.main import WebsiteSale
import odoo.tools
import threading
from odoo.exceptions import AccessDenied

class ProductCategories(http.Controller):

    @http.route('/get_search_filter_value', type='json', auth='public', website=True)
    def get_search_filter_value(self, **kw):
        material_domains = []
        shape_type_domains = []
        detailed_shape_domain = []
        alloy_domain = []
        stiffness_domain = []
        origin_domain = []
        if kw.get('material_category', None):
            domain = ('product_material_category_id', '=', kw.get('material_category'))
            material_domains.append(domain)
            shape_type_domains.append(domain)
            detailed_shape_domain.append(domain)
            alloy_domain.append(domain)
            origin_domain.append(domain)
        if kw.get('material', None):
            domain = ('product_material_id', '=', kw.get('material'))
            shape_type_domains.append(domain)
            detailed_shape_domain.append(domain)
            alloy_domain.append(domain)
            origin_domain.append(domain)
        if kw.get('shape_type', None):
            basic_shapes = request.env['product.basic.shape'].search([
                ('product_shape_type_id', '=', kw.get('shape_type'))
            ])
            domain = (('product_basic_shape_id', 'in', tuple(basic_shapes.ids)))
            detailed_shape_domain.append(domain)
        if kw.get('alloy', None):
            domain = ('product_alloy_id', '=', kw.get('alloy'))
            stiffness_domain.append(domain)
            origin_domain.append(domain)
        if kw.get('stiffness', None):
            domain = ('product_stiffness_id', '=', kw.get('stiffness'))
            origin_domain.append(domain)
        # get products
        materials = request.env['product.template'].search(material_domains).product_material_id
        shape_types = request.env['product.shape.type'].browse()
        if shape_type_domains:
            shape_types = request.env['product.template'].search(shape_type_domains).product_basic_shape_id.product_shape_type_id
        detail_shapes = request.env['product.detailed.shape'].browse()
        if detailed_shape_domain:
            detail_shapes = request.env['product.template'].search(detailed_shape_domain).product_detailed_shape_id
        alloys = request.env['product.alloy'].browse()
        if alloy_domain:
            alloys = request.env['product.template'].search(alloy_domain).product_alloy_id
        stiffness = request.env['product.stiffness'].browse()
        if stiffness_domain:
            stiffness = request.env['product.template'].search(stiffness_domain).product_stiffness_id
        origins = request.env['res.country'].browse()
        if origin_domain:
            origins = request.env['product.template'].search(origin_domain).product_origin
        res = {}
        res.update({
            'materials': [{'id': it.id, 'name': it.name} for it in materials],
            'shape_types': [{'id': it.id, 'name': it.name} for it in shape_types],
            'detail_shapes': [{'id': it.id, 'name': it.name} for it in detail_shapes],
            'alloys': [{'id': it.id, 'name': it.name} for it in alloys],
            'stiffness': [{'id': it.id, 'name': it.name} for it in stiffness],
            'origins': [{'id': it.id, 'name': it.name} for it in origins],
        })
        return res

    @http.route('/product_material_category', type='json', auth='public', website=True)
    def material_category(self, **kw):
        material_categories = http.request.env['product.material.category'].sudo().search([])
        res = []
        for r in material_categories:
            res.append({'id': r.id, 'name': r.name})
        return res

class ProductController(WebsiteSale):

    @http.route('/product_calc_price', type='json', auth='public', website=True)
    def product_calc_price(self, product_id, options, **kw):
        uid = request.session.uid
        pricelist_context, pricelist = self._get_pricelist_context()
        res = {}
        if not product_id.isnumeric():
            return {}
        product = request.env['product.product'].sudo().search([('id', '=', int(product_id))])
        if len(product) == 0:
            res.update({
                'status': False,
                'message': _('No product exist!')
            })
            return res

        # Search partner for current user
        # Check whether pricelist is attached to partner and otherwise it will use default pricelist
        # of website
        partner = request.env['res.partner'].sudo().search([('user_ids', '=', uid)])
        options.update({
           'buy_rate': self.get_currency_buy_rate(),
           'sell_rate': self.get_currency_sell_rate(),
        })
        if uid and len(partner) > 0 and partner.property_product_pricelist:
            pricelist = partner.property_product_pricelist
        price_calculated = request.env['sale.order'].sudo().calculate_price_info_from_pricing_engine(product, pricelist, options, partner)
        res.update({
            'status': True,
            'data': {
                'price_unit': price_calculated[0],
                'weight': price_calculated[1],
                'subtotal': price_calculated[2],
            }
        })
        return res

    @http.route(['/oristar_shop/cart/update'], type='json', auth="public", methods=['POST'], website=True)
    def oristar_cart_update(self, product_id, line_id=None, add_qty=1, set_qty=0, **kw):
        """This route is called when adding a product to cart (no options)."""
        sale_order = request.website.sale_get_order(force_create=True)
        if sale_order.state != 'draft':
            request.session['sale_order_id'] = None
            sale_order = request.website.sale_get_order(force_create=True)

        if kw.get('order_is_new'):
            current_user = http.request.env.user
            partner = current_user.partner_id
            sale_order.set_default_addresss_to_order(partner)
            sale_order.set_default_inv_addresss_to_order(partner)

        product_custom_attribute_values = None
        if kw.get('product_custom_attribute_values'):
            product_custom_attribute_values = json.loads(kw.get('product_custom_attribute_values'))

        no_variant_attribute_values = None
        if kw.get('no_variant_attribute_values'):
            no_variant_attribute_values = json.loads(kw.get('no_variant_attribute_values'))

        """
            find line id of product with dimension is the same to product add to cart,
            if not add new order line
        """
        matched_line_id = None
        matched_line = None
        milling_faces = kw.get('milling_faces') or False
        milling_method = kw.get('milling_method') or False
        for line in sale_order.sudo().order_line:
            if not line_id and (line.notes or kw.get('notes')):
                continue
            if not line_id and (line.milling_faces != milling_faces or line.milling_method != milling_method):
                continue
            if line_id and line.id == int(line_id):
                matched_line_id = line.id
                matched_line = line
                break
            elif (float(kw.get('long', 0)) == line.sudo().product_long and float(kw.get('width', 0)) == line.sudo().product_width
                    and float(kw.get('weight_per_roll', 0)) == line.sudo().weight_per_roll
                  and float(
                        kw.get('thickness', 0)) == line.sudo().product_thickness and line.sudo().product_id.id == int(
                        product_id)
            ):
                matched_line_id = line.id
                matched_line = line

        options = {}
        thickness = kw.get('thickness', None)
        long = kw.get('long', None)
        width = kw.get('width', None)
        price_unit = kw.get('price_unit', None)
        weight_per_roll = kw.get('weight_per_roll', None)
        weight = kw.get('weight', None)
        subtotal = kw.get('subtotal', None)
        if thickness:
            thickness = float(thickness)
        if long:
            long = float(long)
        if width:
            width = float(width)
        if price_unit:
            price_unit = float(price_unit)
        options.update({
            'thickness': thickness,
            'long': long,
            'width': width,
            'price_unit': price_unit,
            'weight': weight,
            'weight_per_roll': weight_per_roll,
            'subtotal': subtotal,
            'notes': kw.get('notes'),
            'milling_method': kw.get('milling_method'),
            'milling_faces': kw.get('milling_faces'),
        })

        if matched_line_id:
            sale_order._cart_update(
                product_id=int(product_id),
                add_qty=add_qty,
                set_qty=set_qty,
                line_id=matched_line_id,
                product_custom_attribute_values=product_custom_attribute_values,
                no_variant_attribute_values=no_variant_attribute_values
            )
            if matched_line.exists():
                matched_line.product_uom_change()
            if matched_line.exists() and kw.get('notes'):
                matched_line.write({
                    'notes': kw.get('notes')
                })
        else:
            sale_order.manually_create_order_line(
                product_id = int(product_id),
                add_qty = add_qty,
                set_qty = set_qty,
                options=options,
                product_custom_attribute_values = product_custom_attribute_values,
                no_variant_attribute_values = no_variant_attribute_values
            )

        sale_order.write({
            'delivery_type': 'receive_at_customer_warehosue',  # TODO
        })
        if not kw.get('calc_price_later'):
            sale_order.action_calculate_price()
            if sale_order.sudo().order_line:
                sale_order._compute_customer_address_info()
                sale_order.action_calculate_shipping_price()
        cart_quantity = 0
        for line in sale_order.order_line:
            cart_quantity += line.product_uom_qty or 0

        return {'status': True, 'cart_quantity': cart_quantity}

    @http.route(['/oristar_shop/confirm-order'], type='json', auth="public", methods=['POST'], website=True)
    def confirm_order(self, order_id, address_id):
        current_user = http.request.env.user
        partner = current_user.partner_id
        order = request.env['sale.order'].sudo().browse(order_id)
        current_user_external_id = current_user.get_external_id().get(request.env.user.id, None)
        # if user is not logged in it must provide the shipping address
        if len(order.partner_shipping_id.state_id) == 0:
            return {
                'status': False,
                'message': _('You have to provide the shipping address'),
            }
        if current_user_external_id == 'base.public_user':
            order = request.website.sale_get_order()
            order.sudo().write({
                'state': 'sent'
            })
            partner = order.partner_id
            order.write({
                'partner_shipping_id': partner.id,
                'district_id': partner.district_id.id,
                'township_id': partner.township_id.id,
            })
            # notify to new order
            chanel = (request.env.cr.dbname, 'new_so')
            message = {
                'name': order.name
            }
            request.env['bus.bus'].sudo().sendmany([(chanel, message)])
            return {'status': True}

        if order and order.partner_id.id == partner.id:
            order.sudo().write({
                'state': 'sent'
            })

        # attach delivery address to order
        for child in partner.child_ids:
            if child.id == int(address_id):
                order.write({
                    'partner_shipping_id': child.id,
                    'district_id': child.district_id.id,
                    'township_id': child.township_id.id,
                })
        # List of user to get notification
        order_partner = order.partner_id.sudo()
        notif_users = request.env.company.sudo().sale_notification_reception_partner_ids | order_partner.seller_in_charge
        # List of users to get email
        email_users = request.env['res.partner'].browse()
        if order_partner.seller_in_charge:
            email_users |= order_partner.seller_in_charge
        else:
            email_users |= request.env.company.sudo().sale_notification_reception_partner_ids

        mail_template = request.env.ref('oristar_ecommerce_website.new_order_notification',
                                           raise_if_not_found=False)
        emails_to = []
        for eu in email_users.sudo():
            if eu.email:
                emails_to.append(eu.email)
        if emails_to:
            email_values = {}
            joined_emails_to = ','.join(emails_to)
            email_values = {'email_to': joined_emails_to}
            mail_template.sudo().send_mail(order.id, email_values=email_values, force_send=True)
        # notify to new order
        chanel = (request.env.cr.dbname, 'new_so')
        message = {
            'name': order.name,
            'notif_users': notif_users.sudo().user_ids.ids
        }
        request.env['bus.bus'].sudo().sendmany([(chanel, message)])
        return {'status': True}

    @http.route(['/shop/cart/update_json'], type='json', auth="public", methods=['POST'], website=True, csrf=False)
    def cart_update_json(self, product_id, line_id=None, add_qty=None, set_qty=None, display=True):
        self.oristar_cart_update(product_id, line_id, add_qty, set_qty)
        order = request.website.sale_get_order()
        cart_quantity = 0
        for line in order.order_line:
            cart_quantity += line.product_uom_qty if line.product_uom_qty else 0

        return {'status': True, 'cart_quantity': cart_quantity}

    @http.route(['/my/orders/clone'], type='json', auth="user", website=True)
    def portal_my_orders_clone(self, order_id):
        """
        This method should be in portal type route but to call oristar_cart_update, i must place it here. It is
        kind of bad practice. Fix me if you can!
        """
        SaleOrder = request.env['sale.order'].sudo()
        current_partner = request.env.user.partner_id
        sale_order = SaleOrder.browse(order_id)
        if sale_order.partner_id == current_partner:
            # copy data of order line in sale order and move to sale order in cart
            for so_line in sale_order.order_line:
                add_qty = so_line.product_uom_qty
                product_id = so_line.product_id.id
                options = {
                    'product_id': product_id,
                    'add_qty': add_qty,
                    'set_qty': 0,
                    'price_unit': so_line.price_unit,
                    'thickness': so_line.product_thickness,
                    'long': so_line.product_long,
                    'width': so_line.product_width,
                    'weight_per_roll': so_line.weight_per_roll,
                    'weight': so_line.product_weight,
                    'notes': so_line.notes,
                    'milling_method': so_line.milling_method,
                    'milling_faces': so_line.milling_faces,
                    'product_custom_attribute_values': '[]',
                    'no_variant_attribute_values': '[]',
                    'variant_values': [],
                    'order_is_new': True,
                    'subtotal': so_line.price_subtotal,
                    'calc_price_later': True
                }
                self.oristar_cart_update(**options)
            cart_sale_order = request.website.sale_get_order(force_create=True)
            cart_sale_order.action_calculate_price()
            if cart_sale_order.sudo().order_line:
                cart_sale_order._compute_customer_address_info()
                cart_sale_order.action_calculate_shipping_price()
            return {'status': True}
        return {'statue': False}

    def get_currency_sell_rate(self):
        vnd_currency = request.env.ref('base.VND').exists()
        today_currency_rate = request.env['res.currency.rate'].sudo().search([('name', '=', fields.Date.today()),
                                                                           ('currency_id', '=', vnd_currency.id)],
                                                                          limit=1)
        if today_currency_rate:
            return today_currency_rate.rate
        else:
            return 0.0

    def get_currency_buy_rate(self):
        vnd_currency = request.env.ref('base.VND').exists()
        today_currency_rate = request.env['res.currency.rate'].sudo().search([('name', '=', fields.Date.today()),
                                                                           ('currency_id', '=', vnd_currency.id)],
                                                                          limit=1)
        if today_currency_rate:
            return today_currency_rate.buy_rate
        else:
            return 0.0

    @http.route(['/oristar_shop/add_to_cart'], type='json', auth="public", methods=['POST'], website=True)
    def or_shop_add_to_cart(self, product_template_id):
        if not str(product_template_id).isnumeric():
            return
        product_template = request.env['product.template'].browse(int(product_template_id))
        if len(product_template) == 0:
            return
        combination = product_template._get_first_possible_combination()
        pricelist = request.website.get_current_pricelist()
        combination_info = product_template._get_combination_info(combination, add_qty=1, pricelist=pricelist)
        product_variant = product_template.env['product.product'].browse(combination_info['product_id'])[0]
        product_id = product_variant.id
        return self.oristar_cart_update(product_id, add_qty=1, set_qty=0, quantity=1, product_custom_attribute_values='[]',
                                 variant_values='', thickness=product_template.product_thickness,
                                 long=product_template.product_long, width=product_template.product_width,
                                 price_unit=product_template.list_price, weight=product_template.product_weight,
                                 subtotal=0)
        
    @http.route("/api/calculate_product_price", auth='public', type='json', csrf=False, methods=["POST"])
    def api_calculate_product_price(self, user_info, product_id, options):
        """ Calculate price unit, weight of product based on pass parameters, which provided in JSON format of HTTP POST request
            
            @param user_info: username and password for authenticated, if not use public user for calculating price
                            example: {"username": "c01user@example.com", "password": "123456"}
            @param product_id: selected product
            @param options: dictionary which provides customized index requested by user
                            example: {"width": 300, "long": 200, "thickness": 100, "qty": 20, "weight": 0, 
                                        "milling_method": "PHAY2F", "milling_faces": "KT1"}
            @return: data of price unit, weight and api link and milling fee
            Example of request body in JSON format:
                {
                    "jsonrpc":"2.0",
                    "method":"call",
                    "params":{
                        "user_info": {
                            "username": "c01user@example.com",
                            "password": "123456"
                        },
                        "product_id":8,
                        "options":{
                            "long": 200,
                            "width": 300,
                            "thickness": 100,
                            "qty": 2,
                            "weight": 0,
                            "milling_method": "PHAY4F",
                            "milling_faces": "KT2andKT3"
                        }
                    }
                }
            Example of response format:
                {
                    "jsonrpc": "2.0",
                    "id": null,
                    "result": {
                        "status": 200,
                        "data": {
                            "price_unit": 40630.69090909091,
                            "weight": 33.0,
                            "api_link": "http://118.70.215.54:8080/pricing/pricing?date=2022-01-15&file=pp3_cmc.xlsx&sheet=17012022&m=43800000.0&r=23220.0&s=23500.0;http://118.70.215.54:8080/pricing/pricing?date=2022-01-15&file=_pp1_sale2.xlsx&sheet=nhom_hop_kim_day&d=0.0&e=100&f=300&g=200&h=2&s=0.1&i=0&a=PHAY4F&ac=KT2andKT3",
                            "milling_fee": 10909.09090909091
                        }
                    }
                }
                
        """
        partner = request.env.ref('base.public_partner').exists()
        if user_info and user_info.get('username') and user_info.get('password'):
            # find user and corresponding partner
            db = self.get_db_name()
            try:
                uid = request.registry['res.users'].authenticate(db, user_info.get('username'), user_info.get('password'), {'interactive': False})
                if uid:
                    partner = request.env['res.users'].sudo().browse(uid).exists().partner_id
            except AccessDenied as ex:
                return {
                    'status': 401,
                    'message': _('User credential is invalid.')
                }
            
        product = request.env['product.product'].sudo().search([('id', '=', product_id)], limit=1)
        if not product:
            return {
                'status': 400,
                'message': _('Product not found')
            }

        options.update({
           'buy_rate': self.get_currency_buy_rate(),
           'sell_rate': self.get_currency_sell_rate(),
        })
        
        pricelist = partner.property_product_pricelist
        price_calculated = request.env['sale.order'].sudo().calculate_price_info_from_pricing_engine(product, pricelist, options, partner)
        return {
            'status': 200,
            'data': {
                'price_unit': price_calculated[0],
                'weight': price_calculated[1],
                'api_link': price_calculated[2],
                'milling_fee': price_calculated[3]
            }
        }

    @http.route("/api/kt1_product_variant_sync", auth='none', csrf=False, methods=["POST"])
    def kt1_product_variant_sync(self, user_info, product_tmpl_id, vals):
        """
        Sync product variant with product template
        @param user_info: username and password for authenticated, if not use public user for calculating price
                            example: {"username": "c01user@example.com", "password": "123456"}
        @param product_tmpl_id: product template id
        :param vals: List of dictionary to sync to product variant
                example: [{'product_thickness': 14, 'erp_id': 'abcdef'}]
        :return: status
        """
        user_info = json.loads(user_info)
        product_tmpl_id = int(product_tmpl_id)
        vals = json.loads(vals)
        partner = request.env.ref('base.public_partner').exists()
        if user_info and user_info.get('username') and user_info.get('password'):
            # find user and corresponding partner
            db = self.get_db_name()
            try:
                uid = request.registry['res.users'].authenticate(db, user_info.get('username'),
                                                                 user_info.get('password'), {'interactive': False})
                if uid:
                    partner = request.env['res.users'].sudo().browse(uid).exists().partner_id
            except AccessDenied as ex:
                return http.Response(status=503)

        result = request.env['product.template'].sudo().sync_kt1_variant(product_tmpl_id, vals)
        if result:
            return http.Response(status=200)
        else:
            return http.Response(status=503)
            
    def get_db_name(self):
        db = odoo.tools.config['db_name']
        # If the database name is not provided on the command-line,
        # use the one on the thread (which means if it is provided on
        # the command-line, this will break when installing another
        # database from XML-RPC).
        if not db and hasattr(threading.current_thread(), 'dbname'):
            return threading.current_thread().dbname
        return db
            
            
        

class Address(http.Controller):
    @http.route('/address_district', type='json', auth='public', website=True)
    def address_district(self, state_id=None):
        res = []
        if state_id and state_id.isnumeric():
            state_id = int(state_id)
            districts = http.request.env['res.district'].sudo().search([('state_id', '=', state_id)])
            for d in districts:
                res.append({'id': d.id, 'name': d.name})
        return res

    @http.route('/address_township', type='json', auth='public', website=True)
    def address_township(self, state_id=None, district_id=None):
        res = []
        searches = []
        if district_id and district_id.isnumeric():
            district_id = int(district_id)
            searches.append(('district_id', '=', district_id))
            townships = http.request.env['res.township'].sudo().search([('district_id', '=', district_id)])
            for t in townships:
                res.append({'id': t.id, 'name': t.name})
        elif state_id and state_id.isnumeric():
            state_id = int(state_id)
            districts = http.request.env['res.district'].sudo().search([('state_id', '=', state_id)])
            district_ids = tuple(districts.ids)
            if len(district_ids) > 0:
                townships = http.request.env['res.township'].sudo().search([('district_id', 'in', district_ids)])
                for t in townships:
                    res.append({'id': t.id, 'name': t.name})
        return res

