from odoo import fields, models, _, api
from odoo.exceptions import UserError

class ProductTemplate(models.Model):
    _inherit = 'product.product'
    
    available_product_stiffness_ids = fields.Many2many('product.stiffness', 
                                                       compute='_compute_available_product_stiffness_ids',
                                                       help="Technical field to filter temper based on selected"
                                                       "grades and material")
    
    product_thickness = fields.Float(string='Size 1')
    product_long = fields.Float(string='Size 3')
    product_width = fields.Float(string='Size 2')
    product_weight = fields.Float(string='Product Weight')

    @api.depends('product_material_id', 'product_alloy_id')
    def _compute_available_product_stiffness_ids(self):
        """ Override computed field here because product.product can't receive both depended values at changing time.
        """
        for r in self:
            r.available_product_stiffness_ids = self.env['product.stiffness'].search([('product_material_id', '=', r.product_material_id.id),
                                                                                      ('product_alloy_id', '=', r.product_alloy_id.id)])

    def get_list_price_product_tmpl_by_pricelist(self, partner, pricelist):
        self.ensure_one()
        """
        1. if product is attached to specific user then return list price right away
        2. if else find pricelist with pp1 and get profit margin to calculate list price
        """
        closest_item = None
        if self.specific_customer_id.id == partner.id:
            return self.list_price

        categ_id = self.categ_id.id if self.categ_id else False
        for item in pricelist.item_ids.filtered(
                lambda item: item.price_method_code == 'pp1' and item.compute_price == 'api'):
            if item.product_tmpl_id and item.product_tmpl_id.id == self.id and item.applied_on == '1_product':
                closest_item = item
                break
            elif item.categ_id and item.categ_id.id == categ_id and item.applied_on == '2_product_category':
                closest_item = item
            elif not closest_item and item.applied_on == '3_global':
                closest_item = item

        if not closest_item:
            raise UserError(_('Pricelist for current user is invalid.'))

        tsln = closest_item.tsln
        list_price = self.list_price
        list_price = list_price * (1 + tsln / 100)

        return list_price
