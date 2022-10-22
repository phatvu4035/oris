# -*- coding: utf-8 -*-
from werkzeug.exceptions import Forbidden, NotFound
import logging
import werkzeug
import base64
import re

from odoo.addons.portal.controllers.web import Home as PortalHome
from odoo.addons.website.controllers.main import Website
from odoo import http, _
from odoo.http import request, content_disposition
from odoo.osv import expression
from odoo.addons.http_routing.models.ir_http import slug
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.website_sale.controllers.main import TableCompute
from odoo.addons.website.controllers.main import QueryURL
from odoo.addons.auth_signup.controllers.main import AuthSignupHome
from odoo.exceptions import UserError
from odoo.addons.auth_signup.models.res_users import SignupError
from psycopg2 import IntegrityError, OperationalError, errorcodes

_logger = logging.getLogger(__name__)

class OristarHome(Website):
    @http.route(website=True, auth="public", sitemap=False)
    def web_login(self, *args, **kw):
        if request.httprequest.method == 'POST':
            ResUser = request.env['res.users']
            user = ResUser.sudo().search([('login', '=', request.params['login'])], limit=1)
            group_user = user.groups_id.filtered(lambda item: item.get_external_id().get(item.id) == 'base.group_user')
            if user.need_approval and not group_user:
                values = {'error': _('The account is waiting for confirmation!')}
                response = request.render('web.login', values)
                response.headers['X-Frame-Options'] = 'DENY'
                return response
        return super(OristarHome, self).web_login(*args, **kw)

class OristarWebsite(PortalHome):
    @http.route()
    def index(self, **post):
        super(OristarWebsite, self).index()
        searches = [('is_published', '=', True)]
        page = post.get('page', 1)
        ppg = 12

        if post.get('search', ''):
            for srch in post.get('search').split(" "):
                subdomains = [
                    [('name', 'ilike', srch)],
                    [('product_variant_ids.default_code', 'ilike', srch)]
                ]
                subdomains.append([('description', 'ilike', srch)])
                subdomains.append([('description_sale', 'ilike', srch)])

                searches.append(expression.OR(subdomains))
        # Search by product attribute
        if post.get('material_category', None) and post.get('material_category').isnumeric():
            searches.append(('product_material_category_id', '=', int(post.get('material_category'))))
        if post.get('material', None) and post.get('material').isnumeric():
            searches.append(('product_material_id', '=', int(post.get('material'))))
        if post.get('basic_shape', None) and post.get('basic_shape').isnumeric():
            searches.append(('product_basic_shape_id', '=', int(post.get('basic_shape'))))
        if post.get('alloy', None) and post.get('alloy').isnumeric():
            searches.append(('product_alloy_id', '=', int(post.get('alloy'))))
        if post.get('stiffness', None) and post.get('stiffness').isnumeric():
            searches.append(('product_stiffness_id', '=', int(post.get('stiffness'))))
        if post.get('origin', None) and post.get('origin').isnumeric():
            searches.append(('product_origin', '=', int(post.get('origin'))))

        Product = request.env['product.template'].with_context(bin_size=True)
        search_product = Product.search(searches)
        # Build pager
        product_count = len(search_product)
        pager = request.website.pager(url='/', total=product_count, page=page, step=ppg, scope=7, url_args=post)
        offset = pager['offset']

        products = search_product[offset: offset + ppg]

        # Get all material category
        material_categories = http.request.env['product.material.category'].sudo().search([])

        return request.render('website.homepage', {
            'products': products,
            'pager': pager,
            'material_categories': material_categories,
            'slug': slug
        })

    @http.route('/web/select_account_type', type='http', auth='public', website=True, sitemap=False)
    def select_account_type(self):
        return request.render('oristar_ecommerce_website.select_account_type')

    @http.route(['/my/address-book/<string:type>'], type='http', auth='user', website=True)
    def address_book(self, type=None, **post):
        current_user = http.request.env.user
        partner = current_user.partner_id
        childs = http.request.env['res.partner'].browse()
        for c in partner.child_ids:
            if c.type == type:
                childs |= c
        countries = request.env['res.country'].sudo().search([])
        states = request.env['res.country.state'].sudo().search([])
        return request.render('oristar_ecommerce_website.address_book', {
            'childs': childs,
            'partner': partner,
            'countries': countries,
            'states': states,
            'type': type
        })

    @http.route(['/my/address-data'], type='json', auth='public', website=True)
    def my_address_data(self, address_id):
        current_user = http.request.env.user
        current_user_external_id = current_user.get_external_id().get(request.env.user.id, None)
        ResPartner = request.env['res.partner']
        address = ResPartner.sudo().browse(address_id)
        address_data = ResPartner.sudo().search_read([('id', '=', int(address_id))], fields=[
            'id', 'name', 'country_id', 'city', 'street', 'zip', 'phone', 'state_id', 'district_id', 'township_id', 'email', 'vat'])
        partner = current_user.partner_id
        if current_user_external_id == 'base.public_user':
            website_sale_order = request.website.sale_get_order()
            partner_shipping_order = website_sale_order.partner_shipping_id
            partner_invoice_order = website_sale_order.partner_invoice_id
            if partner_shipping_order.id != int(address_id) and partner_invoice_order.id != int(address_id):
                raise UserError(_('The address is invalid!'))
            if address.get_external_id().get(address.id, None) == 'base.public_partner':
                raise UserError(_('The address is invalid!'))
            return address_data
        if int(address_id) not in partner.child_ids.ids:
            raise UserError(_('The address is invalid!'))
        return address_data

    @http.route(['/my/address-book/data/<string:type>'], type='json', auth='public', website=True)
    def address_book_data(self, type=None, order_id=None, **post):
        current_user = http.request.env.user
        partner = current_user.partner_id
        current_user_external_id = current_user.get_external_id().get(request.env.user.id, None)

        if current_user_external_id == 'base.public_user':
            values = self._prepare_address_boook_values(type, post)
            website_sale_order = request.website.sale_get_order()
            partner_shipping_order = website_sale_order.partner_shipping_id
            partner_invoice_order = website_sale_order.partner_invoice_id
            if post.get('id', None) and partner_shipping_order.id == int(post.get('id')):
                partner_shipping_order.write(values)
                # calculate shipping price
                self.order_shipping_price(website_sale_order.id, partner_shipping_order.id)
                return {'status': True}
            if post.get('id', None) and partner_invoice_order.id == int(post.get('id')):
                partner_invoice_order.write(values)
                return {'status': True}
            elif not post.get('id', None):
                partner_shipping_order = website_sale_order.partner_shipping_id
                partner_invoice_order = website_sale_order.partner_invoice_id
                # unlogged in user are allowed to have maximum 2 address (delivery and invoice)
                if (
                        partner_shipping_order.get_external_id().get(partner_shipping_order.id,
                                                                     None) != 'base.public_partner'
                        and partner_invoice_order.id != partner_shipping_order.id
                        and partner_invoice_order.get_external_id().get(partner_invoice_order.id,
                                                                        None) != 'base.public_partner'
                ):
                    return {
                        'status': False,
                        'message': _('For un-logged in user, customer is allowed to add only one address')
                    }
                if type == 'delivery':
                    address = http.request.env['res.partner'].sudo().create(values)
                    website_sale_order.write({
                        'partner_shipping_id': address.id,
                    })
                    self.order_shipping_price(website_sale_order.id, address.id)
                    return {'status': True}
                elif type == 'invoice':
                    address = http.request.env['res.partner'].sudo().create(values)
                    website_sale_order.write({
                        'partner_invoice_id': address.id,
                    })
                    return {'status': True}
        order = None
        if order_id:
            SaleOrder = request.env['sale.order']
            order = SaleOrder.sudo().browse(int(order_id))
        # Edit existing address
        if post.get('id', None) and request.httprequest.method == 'POST':
            values = self._prepare_address_boook_values(type, post)
            for child in partner.child_ids:
                if int(post.get('id')) == child.id:
                    child.sudo().write(values)
        # Add new address
        if not post.get('id', None) and request.httprequest.method == 'POST':
            values = self._prepare_address_boook_values(type, post)
            if bool(values):
                values.update({
                    'parent_id': partner.id,
                })
                http.request.env['res.partner'].sudo().create(values)
        # calculate shipping price every time change address
        if order and order.partner_shipping_id and type == 'delivery':
            self.order_shipping_price(order.id, order.partner_shipping_id.id)
        return {'status': True}

    @http.route('/my/address-book/default', type='json', auth='user')
    def address_book_default(self, type, child_id):
        current_user = http.request.env.user
        partner = current_user.partner_id
        if str(child_id).isdigit():
            childs = partner.child_ids
            childs.filtered(lambda c: c.type == type).write({
                'default_delivery_address': False
            })
            for child in childs.filtered(lambda c: c.type == type):
                if int(child_id) == child.id:
                    child.write({
                        'default_delivery_address': True
                    })
                    return {'status': True}
        return {'status': False}

    @http.route(['/my/address-book/delete'], type='json', auth='public', website=True)
    def address_book_delete(self, child_id):
        if str(child_id).isnumeric():
            current_partner = request.env.user.partner_id
            child = http.request.env['res.partner'].browse(child_id).sudo()
            if current_partner != child.parent_id:
                return {'status': False}
            child.sudo().action_archive()
            return {'status': True}
        return {'status': False}

    def _prepare_address_boook_values(self, type, post):
        if not post.get('name', None):
            raise UserError(_('The name is required.'))
        if not post.get('country_id', None):
            raise UserError(_('The country value is required.'))
        if not post.get('state_id', None):
            raise UserError(_('The state value is required.'))
        if not post.get('district_id', None):
            raise UserError(_('The district value is required.'))
        if not post.get('phone', None) and type== 'delivery':
            raise UserError(_('The phone value is required.'))

        if type not in ['contact', 'invoice', 'delivery', 'other', 'private']:
            return {}
        values =  {
            'type': type,
            'name': post.get('name'),
            'country_id': int(post.get('country_id')),
            'state_id': int(post.get('state_id')),
            'city': post.get('city'),
            'street': post.get('street'),
            'phone': post.get('phone'),
            'email': post.get('email'),
            'zip': post.get('zip'),
            'vat': post.get('vat'),
        }
        if post.get('district_id'):
            values.update({'district_id': int(post.get('district_id'))})
        if post.get('township_id'):
            values.update({'township_id': int(post.get('township_id'))})
        return values

    @http.route(['/order/shipping-price'], type='json', auth='public', website=True)
    def order_shipping_price(self, order_id, address_id):
        current_user = http.request.env.user
        partner = current_user.partner_id
        SaleOrder = request.env['sale.order']
        order = SaleOrder.sudo().browse(int(order_id))
        current_user_external_id = current_user.get_external_id().get(request.env.user.id, None)
        if current_user_external_id == 'base.public_user':
            website_sale_order = request.website.sale_get_order()
            order.write({
                'district_id': website_sale_order.partner_shipping_id.district_id.id if website_sale_order.partner_shipping_id.district_id else False,
                'township_id': website_sale_order.partner_shipping_id.township_id.id if website_sale_order.partner_shipping_id.district_id else False,
                'delivery_type': 'receive_at_customer_warehosue',  # TODO
            })
            if website_sale_order.order_line:
                website_sale_order._compute_customer_address_info()
                website_sale_order.action_calculate_shipping_price()
            return {'status': True}
        if order.partner_id.id != partner.id:
            return {'status': False}
        for child in partner.child_ids:
            if child.id == int(address_id):
                order.write({
                    'partner_shipping_id': child.id,
                    'district_id': child.district_id.id if child.district_id else False,
                    'township_id': child.township_id.id if child.district_id else False,
                    'delivery_type': 'receive_at_customer_warehosue',  # TODO
                })
        if order.order_line:
            order._compute_customer_address_info()
            order.action_calculate_shipping_price()

        return {'status': True}

    @http.route(['/order/select-invoice-address'], type='json', auth='user', website=True)
    def select_invoice_address(self, order_id, address_id):
        current_user = http.request.env.user
        partner = current_user.partner_id
        SaleOrder = request.env['sale.order']
        order = SaleOrder.sudo().browse(int(order_id))
        if order.partner_id.id != partner.id:
            return {'status': False}
        for child in partner.child_ids:
            if child.id == int(address_id):
                order.write({
                    'partner_invoice_id': child.id,
                })
        return {'status': True}

    @http.route(['/oristar/policy'], type='http', auth='public', website=True)
    def oristar_policy(self):
        return request.render('oristar_ecommerce_website.waiting_content', {'page_title': "Chính sách"})

    @http.route(['/oristar/faq'], type='http', auth='public', website=True)
    def oristar_faq(self):
        return request.render('oristar_ecommerce_website.waiting_content', {'page_title': "FAQ"})

    @http.route(['/oristar/help'], type='http', auth='public', website=True)
    def oristar_help(self):
        return request.render('oristar_ecommerce_website.waiting_content', {'page_title': "Trợ giúp"})

    @http.route(['/oristar/shipping-method'], type='http', auth='public', website=True)
    def oristar_sipping_method(self):
        return request.render('oristar_ecommerce_website.waiting_content', {'page_title': "Giao hàng"})

    @http.route(['/oristar/customer-service'], type='http', auth='public', website=True)
    def oristar_customer_service(self):
        return request.render('oristar_ecommerce_website.waiting_content', {'page_title': "Dịch vụ"})

    @http.route(['/oristar/machining'], type='http', auth='public', website=True)
    def oristar_machining(self):
        return request.render('oristar_ecommerce_website.waiting_content', {'page_title': "Gia công"})

    @http.route(['/oristar/export'], type='http', auth='public', website=True)
    def oristar_export(self):
        return request.render('oristar_ecommerce_website.waiting_content', {'page_title': "Xuất khẩu"})

    @http.route(['/oristar/steel-and-copper-machining'], type='http', auth='public', website=True)
    def oristar_steel_and_copper_machining(self):
        return request.render('oristar_ecommerce_website.waiting_content', {'page_title': "Gia công đồng"})

    @http.route(['/about-us'], type='http', auth='public', website=True)
    def about_us(self):
        return request.render('oristar_ecommerce_website.waiting_content', {'page_title': "Về chúng tôi"})

    @http.route(['/recruitment'], type='http', auth='public', website=True)
    def recruitment(self):
        return request.render('oristar_ecommerce_website.waiting_content', {'page_title': "Tuyển dụng"})

    @http.route(['/security-payment'], type='http', auth='public', website=True)
    def security_payment(self):
        return request.render('oristar_ecommerce_website.waiting_content', {'page_title': "Chính sách bảo mật thanh toán"})

    @http.route(['/report-policy'], type='http', auth='public', website=True)
    def report_policy(self):
        return request.render('oristar_ecommerce_website.waiting_content', {'page_title': "Chính sách giải quyết khiếu nại"})

    @http.route(['/term-of-use'], type='http', auth='public', website=True)
    def term_of_use(self):
        return request.render('oristar_ecommerce_website.waiting_content', {'page_title': "Điều khoản sử dụng"})

    @http.route(['/shop/order/data'], type='json', auth='public', website=True)
    def shop_order_data(self, order_id):
        current_user = http.request.env.user
        partner = current_user.partner_id
        SaleOrder = request.env['sale.order']
        order = SaleOrder.sudo().browse(int(order_id))
        current_user_external_id = current_user.get_external_id().get(request.env.user.id, None)
        res ={}
        if order.partner_id.id != partner.id and current_user_external_id != 'base.public_user':
            return res
        if current_user_external_id == 'base.public_user':
            order = request.website.sale_get_order()
        website_sale_order = {}
        order_fields = ['id', 'name', 'total_custom_declaration_amount', 'date_order', 'amount_untaxed', 'amount_tax', 'amount_total', 'state', 'create_custom_declaration',
                    'no_of_custom_declaration']
        for f in order_fields:
            website_sale_order.update({f: order[f]})
        res.update({'website_sale_order': website_sale_order})

        partner_shipping = {}
        partner_shipping_fields = ['id', 'name', 'phone', 'city', 'email', 'street']
        if order.partner_shipping_id and order.partner_shipping_id.active:
            for f in partner_shipping_fields:
                partner_shipping.update({f: order.partner_shipping_id[f]})
            partner_shipping.update({
                'partner_shipping_id': order.partner_shipping_id.id,
                'partner_shipping_name': order.partner_shipping_id.name,
                'partner_shipping_phone': order.partner_shipping_id.phone,
            })
            if order.partner_shipping_id.state_id:
                partner_shipping.update({
                    'state_id': order.partner_shipping_id.state_id.id,
                    'state_name': order.partner_shipping_id.state_id.name,
                })
            if order.partner_shipping_id.district_id:
                partner_shipping.update({
                    'district_id': order.district_id.id,
                    'district_name': order.district_id.name,
                })
            if order.partner_shipping_id.township_id:
                partner_shipping.update({
                    'township_id': order.township_id.id,
                    'township_name': order.township_id.name,
                })
            if order.partner_shipping_id.country_id:
                partner_shipping.update({
                    'country_id': order.township_id.id,
                    'country_name': order.partner_shipping_id.country_id.name,
                })
        full_address = [partner_shipping.get('street', ''),
                        partner_shipping.get('township_name', ''),
                        partner_shipping.get('district_name', ''),
                        partner_shipping.get('state_name', ''),
                        partner_shipping.get('country_name', ''),
                        ]
        full_address = list(filter(None, full_address))
        split = ', '
        partner_shipping.update({'full_address': split.join(full_address)})
        res.update({'partner_shipping': partner_shipping})

        order_lines = []
        if order.order_line:
            for line in order.order_line:
                order_line_data = {}
                product = line.product_id
                line_fields = [
                    'id', 'notes', 'product_thickness', 'product_long', 'product_width', 'product_weight', 'product_uom_qty',
                    'price_unit', 'price_unit_with_shipping', 'price_subtotal', 'name_short', 'milling_faces'
                ]
                for f in line_fields:
                    if f == 'milling_faces':
                        milling_faces_selection = line._fields.get('milling_faces').selection
                        mfv = ''
                        for mf in milling_faces_selection:
                            if mf[0] == line[f]:
                                mfv = mf[1]
                        order_line_data.update({f: mfv})
                        continue
                    order_line_data.update({f: line[f]})
                product_fields = ['name', 'default_code']
                order_line_data.update({'product_id': line.product_id.id})
                for f in product_fields:
                    order_line_data.update({f: product[f]})
                if product.product_alloy_id:
                    order_line_data.update({'product_alloy': product.product_alloy_id.name})
                if product.product_stiffness_id:
                    order_line_data.update({'product_stiffness': product.product_stiffness_id.name})
                if product.product_basic_shape_id:
                    order_line_data.update({'basic_shape': product.product_basic_shape_id.name})
                if product.product_origin:
                    order_line_data.update({'product_origin': product.product_origin.name})
                order_line_data.update({'product_website_url': product.website_url})
                order_lines.append(order_line_data)
        res.update({'order_lines': order_lines})

        # get credit info
        CustomerCredit = request.env['customer.credit.limit']
        customer_credit = CustomerCredit.sudo().search([('partner_id', '=', partner.id)], limit=1)
        credit_data = {}
        if len(customer_credit) > 0:
            current_credit = customer_credit.credit
            credit_limit = customer_credit.credit_limit
            credit_data.update({
                'current_credit': current_credit,
                'credit_limit': credit_limit,
            })
        res.update({'credit_data': credit_data})
        return res

    @http.route(['/shop/order/cancel'], type='json', auth='public', website=True)
    def shop_cancel_order(self, order_id):
        current_user = http.request.env.user
        partner = current_user.partner_id
        SaleOrder = request.env['sale.order']
        order = SaleOrder.sudo().browse(int(order_id))
        current_user_external_id = current_user.get_external_id().get(request.env.user.id, None)
        if order.partner_id.id != partner.id and current_user_external_id != 'base.public_user':
            return {'status': False, 'message': _('Order belongs to another user.')}
        if order.state == 'done':
            return {'status': False, 'message': _('Can not cancel order since it has been done.')}
        order.with_context({'disable_cancel_warning': True}).action_cancel()
        return {'status': True}

    @http.route(['''/quotation_file/download/<int:order_id>'''], type='http', auth='public')
    def quotation_file_download(self, order_id=0):
        current_user = http.request.env.user
        current_user_external_id = current_user.get_external_id().get(request.env.user.id, None)
        partner = current_user.partner_id
        SaleOrder = request.env['sale.order'].sudo()
        order = SaleOrder.browse(order_id)
        if current_user_external_id == 'base.public_user' and order.partner_id.get_external_id().get(order.partner_id.id, None) == 'base.public_partner':
            filename = 'Quotation - - %s.pdf' % (order.name)
            pdf = request.env.ref('oristar_ecommerce_website.quotation_so_report').sudo()._render_qweb_pdf(order.id)[0]
            pdfhttpheaders = [('Content-Type', 'application/pdf'), ('Content-Length', len(pdf)), ('Content-Disposition', content_disposition(filename))]
            return request.make_response(pdf, headers=pdfhttpheaders)

        elif order.partner_id.id == partner.id:
            filename = 'Quotation - - %s.pdf' % (order.name)
            pdf = request.env.ref('oristar_ecommerce_website.quotation_so_report').sudo()._render_qweb_pdf(order.id)[0]
            pdfhttpheaders = [('Content-Type', 'application/pdf'), ('Content-Length', len(pdf)), ('Content-Disposition', content_disposition(filename))]
            return request.make_response(pdf, headers=pdfhttpheaders)
        else:
            return request.redirect('/shop/cart')


    @http.route(['/get_countries'], type='json', auth='public')
    def get_countries(self):
        countries = request.env['res.country'].sudo().search([])
        res = []
        for country in countries:
            res.append({'id': country.id, 'name': country.name, 'external_id': country.get_external_id().get(country.id, '')})
        return res

    @http.route(['/get_res_states'], type='json', auth='public')
    def get_res_states(self):
        states = request.env['res.country.state'].sudo().search([])
        res = []
        for state in states:
            res.append({'id': state.id, 'country_id': state.country_id.id, 'name': state.name})
        return res

    @http.route('/web/reset_password', type='http', auth='public', website=True, sitemap=False)
    def web_auth_reset_password(self, *args, **kw):
        qcontext = self.get_auth_signup_qcontext()

        if not qcontext.get('token') and not qcontext.get('reset_password_enabled'):
            raise werkzeug.exceptions.NotFound()

        if 'error' not in qcontext and request.httprequest.method == 'POST':
            try:
                if qcontext.get('token'):
                    self.do_signup(qcontext)
                    return self.web_login(*args, **kw)
                else:
                    login = qcontext.get('login')
                    assert login, _("No login provided.")
                    _logger.info(
                        "Password reset attempt for <%s> by user <%s> from %s",
                        login, request.env.user.login, request.httprequest.remote_addr)
                    request.env['res.users'].sudo().reset_password(login)
                    qcontext['message'] = _("An email has been sent with credentials to reset your password")
            except UserError as e:
                qcontext['error'] = e.args[0]
            except SignupError:
                qcontext['error'] = _("Could not reset your password")
                _logger.exception('error when resetting password')
            except Exception as e:
                qcontext['error'] = str(e)

        if qcontext.get('error') and 'SMTP' in qcontext['error']:
            qcontext.update({
                'error': _('Failed to send email. Please try again later!')
            })

        response = request.render('auth_signup.reset_password', qcontext)
        response.headers['X-Frame-Options'] = 'DENY'
        return response

class OristarEcommerceWebsite(WebsiteSale):
    @http.route([
        '''/shop''',
        '''/shop/page/<int:page>''',
        '''/shop/category/<model("product.public.category"):category>''',
        '''/shop/category/<model("product.public.category"):category>/page/<int:page>'''
    ], type='http', auth="public", website=True, sitemap=WebsiteSale.sitemap_shop)
    def shop(self, page=0, category=None, search='', ppg=False, **post):
        add_qty = int(post.get('add_qty', 1))
        Category = request.env['product.public.category']
        if category:
            category = Category.search([('id', '=', int(category))], limit=1)
            if not category or not category.can_access_from_current_website():
                raise NotFound()
        else:
            category = Category

        if ppg:
            try:
                ppg = int(ppg)
                post['ppg'] = ppg
            except ValueError:
                ppg = False
        if not ppg:
            ppg = request.env['website'].get_current_website().shop_ppg or 20

        ppr = request.env['website'].get_current_website().shop_ppr or 4

        attrib_list = request.httprequest.args.getlist('attrib')
        attrib_values = [[int(x) for x in v.split("-")] for v in attrib_list if v]
        attributes_ids = {v[0] for v in attrib_values}
        attrib_set = {v[1] for v in attrib_values}

        searches = []
        if post.get('material_category', None) and post.get('material_category').isnumeric():
            searches.append(('product_material_category_id', '=', int(post.get('material_category'))))
        if post.get('material', None) and post.get('material').isnumeric():
            searches.append(('product_material_id', '=', int(post.get('material'))))
        if post.get('shape_type', None) and post.get('shape_type').isnumeric():
            basic_shapes = request.env['product.basic.shape'].search([
                ('product_shape_type_id', '=', int(post.get('shape_type')))
            ])
            searches.append(('product_basic_shape_id', 'in', tuple(basic_shapes.ids)))
        if post.get('alloy', None) and post.get('alloy').isnumeric():
            searches.append(('product_alloy_id', '=', int(post.get('alloy'))))
        if post.get('stiffness', None) and post.get('stiffness').isnumeric():
            searches.append(('product_stiffness_id', '=', int(post.get('stiffness'))))
        if post.get('detail_shape', None) and post.get('detail_shape').isnumeric():
            searches.append(('product_detailed_shape_id', '=', int(post.get('detail_shape'))))
        if post.get('origin', None) and post.get('origin').isnumeric():
            searches.append(('product_origin', '=', int(post.get('origin'))))

        domain = self._get_search_domain(search, category, attrib_values)
        domain = searches + domain

        keep = QueryURL('/shop', category=category and int(category), search=search, attrib=attrib_list, order=post.get('order'))

        pricelist_context, pricelist = self._get_pricelist_context()

        request.context = dict(request.context, pricelist=pricelist.id, partner=request.env.user.partner_id)

        url = "/shop"
        if search:
            post["search"] = search
        if attrib_list:
            post['attrib'] = attrib_list

        Product = request.env['product.template'].with_context(bin_size=True)

        order = self._get_search_order(post)
        if post.get('product_name', None):
            order = 'name %s' % post.get('product_name') + ', ' + order
        search_product = Product.search(domain, order=order)
        search_product = search_product.sudo().sorted('inventory_available', reverse=True)
        website_domain = request.website.website_domain()
        categs_domain = [('parent_id', '=', False)] + website_domain
        if search:
            search_categories = Category.search([('product_tmpl_ids', 'in', search_product.ids)] + website_domain).parents_and_self
            categs_domain.append(('id', 'in', search_categories.ids))
        else:
            search_categories = Category
        categs = Category.search(categs_domain)

        if category:
            url = "/shop/category/%s" % slug(category)

        product_count = len(search_product)
        pager = request.website.pager(url=url, total=product_count, page=page, step=ppg, scope=7, url_args=post)
        offset = pager['offset']
        products = search_product[offset: offset + ppg]

        # Get optional product
        optional_products = Product.sudo().browse([])
        product_fields = Product.sudo()._fields
        if 'optional_product_ids' in product_fields:
            for p in products:
                optional_products |= p.optional_product_ids

        ProductAttribute = request.env['product.attribute']
        if products:
            # get all products without limit
            attributes = ProductAttribute.search([('product_tmpl_ids', 'in', search_product.ids)])
        else:
            attributes = ProductAttribute.browse(attributes_ids)

        layout_mode = request.session.get('website_sale_shop_layout_mode')
        if not layout_mode:
            if request.website.viewref('website_sale.products_list_view').active:
                layout_mode = 'list'
            else:
                layout_mode = 'grid'

        material_categories = request.env['product.material.category'].sudo().search([])
        featured_products = Product.sudo().search([('featured_product', '=', 1)])

        values = {
            'search': search,
            'category': category,
            'attrib_values': attrib_values,
            'attrib_set': attrib_set,
            'pager': pager,
            'pricelist': pricelist,
            'add_qty': add_qty,
            'products': products,
            'featured_products': featured_products,
            'search_count': product_count,  # common for all searchbox
            'bins': TableCompute().process(products, ppg, ppr),
            'ppg': ppg,
            'ppr': ppr,
            'categories': categs,
            'attributes': attributes,
            'keep': keep,
            'search_categories_ids': search_categories.ids,
            'layout_mode': layout_mode,
            'material_categories': material_categories,
            'optional_products': optional_products
        }
        if category:
            values['main_object'] = category
        return request.render("oristar_ecommerce_website.products", values)

    @http.route(['/shop/0'], type='http', auth="public", website=True, sitemap=True)
    def non_product(self):
        raise NotFound()

    @http.route(['/shop/<model("product.template"):product>'], type='http', auth="public", website=True, sitemap=True)
    def product(self, product, category='', search='', **kwargs):
        if not product.can_access_from_current_website():
            raise NotFound()
        Product = request.env['product.template'].with_context(bin_size=True)
        values = self._prepare_product_values(product, category, search, **kwargs)
        detail_shapes = request.env['product.detailed.shape'].search([])
        current_shape = request.env['product.detailed.shape'].browse([])
        if product.product_detailed_shape_id:
            current_shape = product.product_detailed_shape_id
        # Get optional product
        optional_products = Product.sudo().browse([])
        product_fields = Product.sudo()._fields
        if 'optional_product_ids' in product_fields:
            if product.optional_product_ids:
                optional_products |= product.optional_product_ids
        values.update({
            'detail_shapes': detail_shapes,
            'current_shape': current_shape,
            'optional_products': optional_products
        })
        return request.render("website_sale.product", values)

class AuthSignupHome(AuthSignupHome):
    @http.route('/web/signup', type='http', auth='public', website=True, sitemap=False)
    def web_auth_signup(self, *args, **kw):
        qcontext = self.get_auth_signup_qcontext()

        if not qcontext.get('token') and not qcontext.get('signup_enabled'):
            raise werkzeug.exceptions.NotFound()
        qcontext.update({'account_type': kw.get('account_type')})
        qcontext.update({'vat': kw.get('vat', False)})
        qcontext.update({'phone': kw.get('phone', False)})
        if kw.get('phone', None) and request.httprequest.method == 'POST':
            if not self._validate_phone_number(kw.get('phone')):
                qcontext['error'] = _("Phone number is invalid.")
        if kw.get('login', None) and request.httprequest.method == 'POST':
            if not self._validate_email(kw.get('login')):
                qcontext['error'] = _("Email is invalid.")
        if request.httprequest.method == 'POST':
            Partner = request.env['res.partner'].sudo()
            # Check if duplicate phone
            if kw.get('phone') and Partner.search([('phone', '=', kw.get('phone'))]):
                qcontext.update({'account_type': kw.get('account_type')})
                qcontext.update({'vat': kw.get('vat', False)})
                qcontext.update({'phone': kw.get('phone', False)})
                qcontext['error'] = _('Another user is already registered using this phone number.')

        if 'error' not in qcontext and request.httprequest.method == 'POST':
            try:
                self.do_signup(qcontext)
                User = request.env['res.users']
                user_sudo = User.sudo().search(
                    User._get_login_domain(qcontext.get('login')), order=User._get_login_order(), limit=1
                )
                partner_values = {'email': kw.get('login')}
                # Update values for partner related to user
                if kw.get('phone', None):
                    partner_values.update({'phone': kw.get('phone')})
                if kw.get('vat', None):
                    partner_values.update({'company_type': 'company'})
                    partner_values.update({'vat': kw.get('vat')})
                if user_sudo:
                    partner = user_sudo.sudo().partner_id
                    partner.write(partner_values)
                    user_sudo.write({'need_approval': True})

                # Send an account creation confirmation email
                template = request.env.ref('oristar_ecommerce_website.mail_template_user_signup_account_created_wait_for_approve',
                                           raise_if_not_found=False)
                if user_sudo and template:
                    template.sudo().send_mail(user_sudo.id, force_send=False)

                # Notify when new user has been registered
                chanel = (request.env.cr.dbname, 'new_user')
                message = {
                    'name': user_sudo.login
                }
                request.env['bus.bus'].sudo().sendmany([(chanel, message)])

                qcontext.update({'message': _('Congratulations on your successful registration. Please wait for confirmation!')})
                response = request.render('auth_signup.signup', qcontext)
                response.headers['X-Frame-Options'] = 'DENY'
                return response
            except UserError as e:
                qcontext['error'] = e.args[0]
            except (SignupError, AssertionError) as e:
                if request.env["res.users"].sudo().search([("login", "=", qcontext.get("login"))]):
                    qcontext["error"] = _("Another user is already registered using this email address.")
                else:
                    _logger.error("%s", e)
                    qcontext['error'] = _("Could not create a new account.")
        if kw.get('account_type', None):
            qcontext.update({'account_type': kw.get('account_type')})
        response = request.render('auth_signup.signup', qcontext)
        response.headers['X-Frame-Options'] = 'DENY'
        return response

    def _signup_with_values(self, token, values):
        db, login, password = request.env['res.users'].sudo().signup(values, token)
        request.env.cr.commit()    # as authenticate will use its own cursor we need to commit the current transaction

    def _validate_phone_number(self, phone):
        validate_phone_number_pattern = "^\\+?\d{1,4}?[-.\s]?\(?\d{1,3}?\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}$"
        m = re.match(validate_phone_number_pattern, phone)
        if m:
            return True
        return False

    def _validate_email(self, email):
        validate_email_pattern = "^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$"
        m = re.match(validate_email_pattern, email)
        if m:
            return True
        return False
