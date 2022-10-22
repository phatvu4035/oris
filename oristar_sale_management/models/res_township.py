from odoo import models, fields, _, api

class ResTownship(models.Model):
    _name = 'res.township'
    _description = 'Township'
    
    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code')
    district_id = fields.Many2one('res.district', string='District')
    viettel_id = fields.Char(string='Viettel Post Code')
    