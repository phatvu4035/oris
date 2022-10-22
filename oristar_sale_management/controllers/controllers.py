# -*- coding: utf-8 -*-

from werkzeug.exceptions import Forbidden, NotFound
import json

from odoo import http, fields


class SaleManagementController(http.Controller):
    @http.route('/get_users_notification', type='json', auth='user', website=True)
    def get_users_notification(self):
        ResUser = http.request.env['res.users']
        need_approval_users = ResUser.search([('need_approval', '=', True)], limit=5, order='id desc')
        res = []
        for u in need_approval_users:
            partner = u.partner_id
            res.append({
                'id': u.id,
                'name': u.name,
                'email': partner.email,
                'phone': partner.phone,
                'res_model': 'res.users',
                'model_name': 'User'
            })
        return res

    @http.route('/get_so_notification', type='json', auth='user', website=True)
    def get_so_notification(self):
        SaleOrder = http.request.env['sale.order'].sudo()
        # get all partner belong to current seller
        current_partner = http.request.env.user.partner_id
        partners = http.request.env['res.partner'].sudo().search([('seller_in_charge', '=', current_partner.id)])
        quotations = SaleOrder.browse()
        if current_partner not in http.request.env.company.sale_notification_reception_partner_ids:
            quotations = SaleOrder.search([('state', '=', 'sent'), ('partner_id', 'in', partners.ids)], limit=5, order='id desc')
        else:
            quotations = SaleOrder.search([('state', '=', 'sent')], limit=5,
                                          order='id desc')
        res = []
        for so in quotations:
            partner = so.partner_id
            res.append({
                'id': so.id,
                'name': so.name,
                'date_order': so.date_order,
                'partner_name': partner.name,
                'res_model': 'sale.order',
                'model_name': 'User'
            })
        return res
