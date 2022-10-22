from odoo import models, fields, _, api
    
class ProductPricelistItem(models.Model):
    _inherit = "product.pricelist.item"
    
    tsln = fields.Float(string='Profit Margin', required=True, default=0.0)
    price_file_id = fields.Many2one('price.file', string='Price Method')
    compute_price = fields.Selection(selection_add=[('api', 'API')], ondelete={'api': 'set default'})
    price_method_code = fields.Char(string='Price Method Code', compute='_compute_price_method_code')
    n_average = fields.Integer(string='N Average', help='Apply for Price method 3.')
    lme_market_id = fields.Many2one('lme.market', string='LME Market', help='Apply for Price method 3.')
    profit_margin_ids = fields.Many2many('profit.margin.range', string='Profit Margin Ranges')
    
    @api.depends('price_file_id')
    def _compute_price_method_code(self):
        for r in self:
            if r.price_file_id:
                if 'pp1' in r.price_file_id.name:
                    r.price_method_code = 'pp1'
                elif 'pp2' in r.price_file_id.name:
                    r.price_method_code = 'pp2'
                elif 'pp3' in r.price_file_id.name:
                    r.price_method_code = 'pp3'
                else:
                    r.price_method_code = ''
            else:
                r.price_method_code = ''
