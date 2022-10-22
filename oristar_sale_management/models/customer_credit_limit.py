import uuid

from odoo import models, fields, _, api
from odoo.exceptions import ValidationError

class CustomerCreditLimit(models.Model):
    _name = 'customer.credit.limit'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Customer Credit Limit'
    
    partner_id = fields.Many2one('res.partner', string='Customer', required=True, index=True)
    credit_limit = fields.Float(string='Credit Limit')
    credit = fields.Float(string='Current Credit')
    currency_id = fields.Many2one('res.currency', string='Currency', required=True)
    erp_id = fields.Char(string='ERP ID', readonly=True, default=lambda self: uuid.uuid4())
    
    @api.constrains('erp_id')
    def _check_erp_id(self):
        for r in self:
            existing_record = self.search([('erp_id', '=', r.erp_id), ('id', '!=', r.id)])
            if existing_record:
                raise ValidationError(_("ERP ID must be unique."))
    
