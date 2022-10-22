from odoo import models, fields, _, api 

class OristarWarehouse(models.Model):
    _name = 'oristar.warehouse'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Oristar Warehouse'
    
    name = fields.Char(string='Name', required=True, index=True)
    code = fields.Char(string='Code', required=True, index=True)
    street = fields.Char(string='Street', required=True)
    located_state_id = fields.Many2one('res.country.state', string='Located State', required=True, domain="[('country_id', '=?', country_id)]")
    located_district_id = fields.Many2one('res.district', string='Located District', required=True, 
                                          domain="[('state_id', '=?', located_state_id)]")
    supplied_state_ids = fields.Many2many('res.country.state', string='Supplied States', domain="[('country_id', '=?', country_id)]")
    country_id = fields.Many2one('res.country', string='Country')
