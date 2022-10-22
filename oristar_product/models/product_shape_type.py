from odoo import models, fields, _, api

class ProductShapeType(models.Model):
    _name = 'product.shape.type'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Product Shape Type'
    
    name = fields.Char(string='Name', index=True, required=True, translate=True)
    description = fields.Text(string='Description')
