from odoo import models, fields, _, api

class ProductMaterial(models.Model):
    _name = 'product.material'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Product Material'
    
    name = fields.Char(string='Name', index=True, required=True, translate=True)
    product_material_category_id = fields.Many2one('product.material.category', string='Material Category', required=True)
    description = fields.Text(string='Description')
    product_alloy_ids = fields.One2many('product.alloy', 'product_material_id', string='Product Grades')
    show_on_website = fields.Boolean(string='Show On Website')
