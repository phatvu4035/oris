import uuid

from odoo import models, fields, _, api, tools
from odoo.exceptions import ValidationError

class InventoryManagement(models.Model):
    _name = 'inventory.management'
    _description = 'Inventory Management'
    
    @tools.ormcache()
    def _get_default_uom_id(self):
        # Deletion forbidden (at least through unlink)
        return self.env.ref('uom.product_uom_unit')
    
    product_id = fields.Many2one('product.product', string='Product', required=True, index=True)
    uom_id = fields.Many2one('uom.uom', 'Unit of Measure', default=_get_default_uom_id, required=True, 
                             help="Default unit of measure used for all stock operations.")
    product_material_category_id = fields.Many2one(related='product_id.product_material_category_id', store=True)
    product_material_id = fields.Many2one(related='product_id.product_material_id', store=True)
    product_alloy_id = fields.Many2one(related='product_id.product_alloy_id', store=True)
    product_stiffness_id = fields.Many2one(related='product_id.product_stiffness_id', store=True)
    product_long = fields.Float(string='Size 3')
    product_width = fields.Float(string='Size 2')
    product_thickness = fields.Float(string='Size 1')
    quantity = fields.Float(string='Quantity')
    quantity_kg = fields.Float(string='Quantity Kg')
    lot = fields.Char(string='Lot')
    warehouse_id = fields.Many2one('oristar.warehouse', string='Warehouse')
    last_update_time = fields.Datetime(string='Last Update')
    erp_id = fields.Char(string='ERP ID', readonly=True, default=lambda self: uuid.uuid4())
    
    @api.constrains('erp_id')
    def _check_erp_id(self):
        for r in self:
            existing_record = self.search([('erp_id', '=', r.erp_id), ('id', '!=', r.id)])
            if existing_record:
                raise ValidationError(_("ERP ID must be unique."))
