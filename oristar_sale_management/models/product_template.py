import uuid

from odoo import models, fields, _, api
from odoo.exceptions import ValidationError

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    inventory_available = fields.Boolean(string='Inventory Available', compute='_compute_inventory_available')
    erp_id = fields.Char(string='ERP ID', readonly=True, default=lambda self: uuid.uuid4())
    
    @api.constrains('erp_id')
    def _check_erp_id(self):
        for r in self:
            existing_record = self.search([('erp_id', '=', r.erp_id), ('id', '!=', r.id)])
            if existing_record:
                raise ValidationError(_("ERP ID must be unique."))
    
    def _compute_inventory_available(self):
        for r in self:
            r.inventory_available = False
            if r.product_variant_ids:
                r.inventory_available = any(r.product_variant_ids.mapped('inventory_available'))
