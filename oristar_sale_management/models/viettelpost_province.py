from odoo import models, fields, _, api

class ViettelPostProvince(models.Model):
    _name = 'viettelpost.province'
    _description = 'Viettel Post Province'
    
    def _default_country_id(self):
        return self.env.user.company_id.country_id
        
    province_id = fields.Integer(string='Province ID', required=True)
    name = fields.Char(string='Province Name', required=True)
    code = fields.Char(string='Province Code', required=True)
    country_id = fields.Many2one('res.country', string='Country', default=_default_country_id)
    mapped_state_id = fields.Many2one('res.country.state', string='Mapped Province', domain="[('country_id', '=?', country_id)]")
