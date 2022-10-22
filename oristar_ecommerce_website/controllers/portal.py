# -*- coding: utf-8 -*-
from werkzeug.exceptions import Forbidden, NotFound
import json
import datetime
import logging
import uuid

from odoo import http
from odoo.http import request
from odoo import _
from odoo.addons.sale.controllers.portal import CustomerPortal
from odoo.http import content_disposition, Controller, request, route
from odoo.addons.portal.controllers.portal import pager as portal_pager, get_records_pager

_logger = logging.getLogger(__name__)

class CustomerPortal(CustomerPortal):
    MANDATORY_BILLING_FIELDS = ['name', 'phone', 'email', 'street', 'country_id']
    @route(['/my/account'], type='http', auth='user', website=True)
    def account(self, redirect=None, **post):
        if (not post.get('image_1920', None)
                and isinstance(post.get('image_1920', None), str)
                and len(post.get('image_1920')) == 0):
            post.pop('image_1920')
        if post.get('image_1920', None) and post.get('image_1920') == 'false':
            post.update({'image_1920': False})
        if not post.get('district_id', None):
            post.update({'district_id': False})
        if not post.get('township_id', None):
            post.update({'township_id': False})
        self.OPTIONAL_BILLING_FIELDS = self.OPTIONAL_BILLING_FIELDS + ['image_1920', 'district_id', 'township_id', 'city', 'zip', 'vat']
        return super(CustomerPortal, self).account(redirect=None, **post)

    @http.route(['/my/orders', '/my/orders/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_orders(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        SaleOrder = request.env['sale.order']

        domain = self._prepare_orders_domain(partner)

        searchbar_sortings = {
            'date': {'label': _('Order Date'), 'order': 'date_order desc'},
            'name': {'label': _('Reference'), 'order': 'name'},
            'stage': {'label': _('Stage'), 'order': 'state'},
        }
        # default sortby order
        if not sortby:
            sortby = 'date'
        sort_order = searchbar_sortings[sortby]['order']

        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        # count for pager
        order_count = SaleOrder.search_count(domain)
        # pager
        pager = portal_pager(
            url="/my/orders",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=order_count,
            page=page,
            step=self._items_per_page
        )
        # add search to domain
        if kw.get('order_date', None):
            try:
                domain.append(
                    (
                     'date_order',
                     '>=',
                     datetime.datetime.combine(datetime.datetime.strptime(kw.get('order_date'), "%m/%d/%Y"), datetime.time(0, 0, 0))
                     )
                )
                domain.append(
                    (
                        'date_order',
                        '<=',
                        datetime.datetime.combine(datetime.datetime.strptime(kw.get('order_date'), "%m/%d/%Y"),
                                                  datetime.time(23, 59, 59))
                    )
                )
            except ValueError:
                _logger.warning('Invalid date order to search')
        if kw.get('search', None):
            domain.append(('name', 'ilike', kw.get('search')))
        # content according to pager
        orders = SaleOrder.sudo().search(domain, order=sort_order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_orders_history'] = orders.ids[:100]

        # count the number of quotation, quotation sent ...
        quotes = SaleOrder.sudo().browse([])
        confirmed = SaleOrder.sudo().browse([])
        produces = SaleOrder.sudo().browse([])
        deliveries = SaleOrder.sudo().browse([])
        delivered = SaleOrder.sudo().browse([])
        cancel = SaleOrder.sudo().browse([])
        for o in orders.sudo():
            o.computed_erp_order_status
            if o.state == 'cancel':
                cancel |= o
            elif o.erp_order_status == 'quote':
                quotes |= o
            elif o.erp_order_status == 'confirm':
                confirmed |= o
            elif o.erp_order_status == 'produce':
                produces |= o
            elif o.erp_order_status == 'delivery':
                deliveries |= o
            elif o.erp_order_status == 'delivered':
                delivered |= o

        values.update({
            'date': date_begin,
            'page_name': 'order',
            'pager': pager,
            'default_url': '/my/orders',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
            'quotes': quotes,
            'confirmed': confirmed,
            'produces': produces,
            'deliveries': deliveries,
            'delivered': delivered,
            'cancel': cancel,
        })
        return request.render("oristar_ecommerce_website.my_orders", values)

    @http.route(['/shop/cart/update-custom-declaration'], type='json', auth="user", methods=['POST'], csrf=False)
    def update_custom_declaration(self, order_id, create_custom_declaration):
        SaleOrder = request.env['sale.order'].sudo()
        sale_order = SaleOrder.browse(int(order_id))
        current_partner = request.env.user.partner_id
        if current_partner and current_partner == sale_order.partner_id:
            sale_order.write({
                'create_custom_declaration': create_custom_declaration,
            })
            return {'status': True}
        return {'status': False}

    def _prepare_orders_domain(self, partner):
        return [
            ('partner_id', '=', partner.id),
            ('state', 'in', ['sale', 'done', 'sent', 'draft', 'cancel'])
        ]

    def _prepare_home_portal_values(self, counters):
        values = super(CustomerPortal, self)._prepare_home_portal_values(counters)
        if 'order_count' in counters:
            SaleOrder = request.env['sale.order'].sudo()
            order_count = SaleOrder.search_count([
                ('partner_id', '=', request.env.user.partner_id.id),
                ('state', 'in', ['draft', 'sent', 'sale', 'done', 'cancel'])
            ])
            values['order_count'] = order_count
        if 'address_count' in counters:
            values.update(address_count=len(self._partner_delivery_addresses))
        return values

    @property
    def _partner_delivery_addresses(self):
        deliveries = request.env.user.partner_id.child_ids.filtered(lambda c: c.type == 'delivery')
        return deliveries
