from odoo import models, fields, _, api

class ProductAlloy(models.Model):
    _name = 'product.alloy'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Product Alloy'
    
    name = fields.Char(string='Name', index=True, required=True)
    product_material_id = fields.Many2one('product.material', string='Product Material', required=True)
    description = fields.Text(string='Description')
