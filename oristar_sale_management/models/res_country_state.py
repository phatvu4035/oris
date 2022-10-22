from odoo import models, fields, _, api

class CountryState(models.Model):
    _inherit = 'res.country.state'

    viettel_id = fields.Char(string='Viettel Post Code')
    vietstar_id = fields.Char(string='Vietstar Code Hanoi')
    vietstar_id_sg = fields.Char(string='Vietstar Code HCM')
