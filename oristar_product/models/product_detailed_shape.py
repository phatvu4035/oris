from odoo import models, fields, _, api

class ProductDetailedShape(models.Model):
    _name = 'product.detailed.shape'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Product Detailed Shape'
    
    name = fields.Char(string='Name', index=True, required=True, translate=True)
    product_basic_shape_ids = fields.Many2many('product.basic.shape', string='Basic Shapes', required=True)
    shape_category = fields.Selection([('circle', 'Circle'), ('cnvcv', 'Rectangle Square Edge'),
                                       ('cnvct', 'Rectangle Round Edge'), ('lg', 'Hexagon'), 
                                       ('ot', 'Round Pipe'), ('ov', 'Square Pipe')],
                                       string='Shape Category')
    description = fields.Text(string='Description')
