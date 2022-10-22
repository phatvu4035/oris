from odoo import models, fields, _, api

class ViettelPostDistrict(models.Model):
    _name = 'viettelpost.district'
    _description = 'Viettel Post District'
    
    district_id = fields.Integer(string='District ID', required=True)
    name = fields.Char(string='District Name', required=True)
    value = fields.Char(string='District Value', required=True)
    province_id = fields.Integer(string='Viettel Post Province', required=True)
    mapped_district_id = fields.Many2one('res.district', string='Mapped District',
                                         domain="[('id', 'in', available_district_ids)]")
    state_id = fields.Many2one('res.country.state', compute='_compute_available_district_ids')

    available_district_ids = fields.Many2many('res.district', compute='_compute_available_district_ids')
    
    @api.depends('province_id')
    def _compute_available_district_ids(self):
        for r in self:
            if r.province_id:
                viettel_province = self.env['viettelpost.province'].search([('province_id', '=', r.province_id)])
                if viettel_province:
                    r.available_district_ids = self.env['res.district'].search([('state_id', '=', viettel_province.mapped_state_id.id)])
                    r.state_id = viettel_province.mapped_state_id
                else:
                    r.available_district_ids = self.env['res.district']
                    r.state_id = self.env['res.country.state']
            else:
                r.available_district_ids = self.env['res.district']
                r.state_id = self.env['res.country.state']
