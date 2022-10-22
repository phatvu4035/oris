from odoo import models, fields, _, api

class LMESpotPrice(models.Model):
    _name = 'lme.spot.price'
    _description = 'LME Spot Price'
    
    record_datetime = fields.Datetime(string='Recorded At', required=True)
    lme_market_id = fields.Many2one('lme.market', string='LME Market', required=True)
    product_material_category_id = fields.Many2one('product.material.category', string='Product Material Category', required=True)
    price = fields.Float(string='Close Price', required=True)
    currency_id = fields.Many2one('res.currency', string='Currency')
