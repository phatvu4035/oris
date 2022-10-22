from odoo import models, fields, _, api

class ProfitMarginRange(models.Model):
    _name = 'profit.margin.range'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Profit Margin Range Based Size 1'
    
    name = fields.Char(string='Name', index=True, required=True)
    description = fields.Text(string='Description')
    profit_margin = fields.Float(string='Profit Margin', required=True, default=0.0)
    size1_min = fields.Float(string='Min Value of Size 1', required=True)
    size1_max = fields.Float(string='Max Value of Size 1', required=True)
