from odoo import models, fields, _, api
from odoo.exceptions import ValidationError

class ProductStiffness(models.Model):
    _name = 'product.stiffness'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Product Temper'
    
    name = fields.Char(string='Name', index=True, required=True)
    product_material_id = fields.Many2one('product.material', string='Product Material', required=True)
    product_alloy_id = fields.Many2one('product.alloy', string='Product Grades', required=True,
                                       domain="[('id', 'in', available_product_alloy_ids)]")
    description = fields.Text(string='Description')
    available_product_alloy_ids = fields.Many2many('product.alloy', compute='_compute_available_product_alloy_ids',
                                                   help="Technical field to filter product grades based on selected material.")
    
    @api.depends('product_material_id')
    def _compute_available_product_alloy_ids(self):
        for r in self:
            r.available_product_alloy_ids = r.product_material_id.product_alloy_ids
    
    @api.constrains('product_material_id', 'product_alloy_id')
    def _check_product_alloy_id_and_product_material_id(self):
        for r in self:
            if r.product_alloy_id not in r.product_material_id.product_alloy_ids:
                raise ValidationError(_("The alloy %s is not in alloy's list of material %s", 
                                        r.product_alloy_id.name,
                                        r.product_material_id.name))
