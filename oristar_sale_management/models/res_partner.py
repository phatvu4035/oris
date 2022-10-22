import uuid

from odoo import models, fields, _, api
from odoo.exceptions import ValidationError

class ResPartner(models.Model):
    _inherit = 'res.partner'

    credit_time_days = fields.Float(string='Credit Time Days')
    customer_type = fields.Selection([('epe', 'EPE'), ('non-epe', 'Non-EPE')], string='Customer Type')
    fax = fields.Char(string='Fax')
    address_type = fields.Selection([('home', 'Home'), ('apartment', 'Apartment'), ('office', 'Office'), ('company', 'Company')],
                                    string='Location Address Type')
    customer_credit_limit_ids = fields.One2many('customer.credit.limit', 'partner_id', string='Customer Credit Limits')
    district_id = fields.Many2one('res.district', string='District')
    township_id = fields.Many2one('res.township', string='Township')
    erp_id = fields.Char(string='ERP ID', readonly=True, default=lambda self: uuid.uuid4())
    default_delivery_address = fields.Boolean(string='Default Delivery Address')
    can_pay_by_cod = fields.Boolean(string='Can Pay By COD')
    seller_in_charge = fields.Many2one('res.partner', string='Seller in Charge')

    @api.constrains('erp_id')
    def _check_erp_id(self):
        for r in self:
            existing_record = self.search([('erp_id', '=', r.erp_id), ('id', '!=', r.id)])
            if existing_record:
                raise ValidationError(_("ERP ID must be unique."))

    def get_credit_info(self):
        self.ensure_one()
        credit = self.env['customer.credit.limit'].browse()
        for r in self:
            credit = self.env['customer.credit.limit'].sudo().search([('partner_id', '=', r.id)])
        return credit
