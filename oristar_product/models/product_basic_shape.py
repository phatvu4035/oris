from odoo import models, fields, _, api

class ProductBasicShape(models.Model):
    _name = 'product.basic.shape'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Product Basic Shape'
    
    name = fields.Char(string='Name', index=True, required=True, translate=True)
    description = fields.Text(string='Description')
    product_detailed_shape_ids = fields.Many2many('product.detailed.shape', string='Detailed Shapes')
    has_size1 = fields.Boolean(string='Has Size 1')
    has_size2 = fields.Boolean(string='Has Size 2')
    has_size3 = fields.Boolean(string='Has Size 3')
    has_weight = fields.Boolean(string='Has Weight')
    is_compact = fields.Boolean(string='Is Compact')
    machinable_size1 = fields.Boolean(string='Machinable Size 1')
    machinable_size2 = fields.Boolean(string='Machinable Size 2')
    machinable_size3 = fields.Boolean(string='Machinable Size 3')
    product_shape_type_id = fields.Many2one('product.shape.type', string='Product Shape Type', required=True)
