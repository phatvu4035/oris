from odoo import models, fields, _, api

class ResCurrencyRate(models.Model):
    _inherit = 'res.currency.rate'
    
    buy_rate = fields.Float(string='Buy Rate')
