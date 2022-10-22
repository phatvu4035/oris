from odoo import models, fields, _, api

class LMEMarket(models.Model):
    _name = 'lme.market'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'LME Market'
    
    name = fields.Char(string='Name', index=True, required=True)
    description = fields.Text(string='Description')
