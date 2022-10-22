from odoo import models, fields, _, api

class ProductMaterialCategory(models.Model):
    _name = 'product.material.category'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'image.mixin']
    _description = 'Product Material Category'
    
    name = fields.Char(string='Name', index=True, required=True, translate=True)
    description = fields.Text(string='Description')
    product_material_ids = fields.One2many('product.material', 'product_material_category_id',
                                           string='Product Materials')
