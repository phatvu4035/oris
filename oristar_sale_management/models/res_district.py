from odoo import models, fields, _, api

class ResDistrict(models.Model):
    _name = 'res.district'
    _description = 'District'
    
    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code')
    state_id = fields.Many2one('res.country.state', string='State')
    urban_zone = fields.Boolean(string='Urban Zone')
    viettel_id = fields.Char(string='Viettel Post Code')
