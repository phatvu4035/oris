from datetime import datetime, timedelta
from odoo import models, fields, _, api
from odoo.exceptions import ValidationError

class LMEPrice(models.Model):
    _name = 'lme.price'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'LME Price'
    
    record_datetime = fields.Datetime(string='Recorded At', required=True)
    lme_market_id = fields.Many2one('lme.market', string='LME Market', required=True)
    product_material_id = fields.Many2one('product.material', string='Product Material', required=True)
    close_price = fields.Float(string='Close Price', required=True)
    
    @api.constrains('record_datetime', 'lme_market_id', 'product_material_id')
    def _check_unique_price_per_day(self):
        for r in self:
            current_date = r.record_datetime.replace(hour=0, minute=0, second=0, microsecond=0)
            next_date = current_date + timedelta(days=1)
            existing_record = self.search([('lme_market_id', '=', r.lme_market_id.id),
                                           ('product_material_id', '=', r.product_material_id.id),
                                           ('record_datetime', '>=', current_date),
                                           ('record_datetime', '<=', next_date),
                                           ('id', '!=', r.id)])
            if existing_record:
                raise ValidationError(_("Alread had price for material %s of market %s on %s", 
                                        r.product_material_id.name, 
                                        r.lme_market_id.name,
                                        current_date))
