import uuid

from odoo import models, fields, _, api
from odoo.exceptions import ValidationError

class ProductProduct(models.Model):
    _inherit = 'product.product'
    
    inventory_available = fields.Boolean(string='Inventory Available', compute='_compute_inventory_available')
    erp_id = fields.Char(string='ERP ID', readonly=True, default=lambda self: uuid.uuid4())
    
    @api.constrains('erp_id')
    def _check_erp_id(self):
        for r in self:
            existing_record = self.search([('erp_id', '=', r.erp_id), ('id', '!=', r.id)])
            if existing_record:
                raise ValidationError(_("ERP ID must be unique."))

    def _compute_inventory_available(self):
        inventory_res = dict((item['product_id'][0], (item['quantity'])) for item in self.env['inventory.management'].read_group([('product_id', 'in', self.ids)], ['product_id', 'quantity'], ['product_id'], orderby='id'))
        for r in self:
            r.inventory_available = True if inventory_res.get(r.id) else False
        