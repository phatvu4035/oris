from odoo import models, fields, _, api
from odoo.exceptions import ValidationError

class PriceFile(models.Model):
    _name = 'price.file'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Price File'
    
    name = fields.Char(string='File Name', index=True, required=True)
    description = fields.Text(string='Description')
    
    @api.constrains('name')
    def _check_name(self):
        for r in self:
            if 'pp1' not in r.name and 'pp2' not in r.name and 'pp3' not in r.name:
                raise ValidationError(_("File name must contain 'pp1' or 'pp2' or 'pp3'."))
            
            if not r.name.endswith('.xlsx'):
                raise ValidationError(_("File extension must be '.xlsx'."))
