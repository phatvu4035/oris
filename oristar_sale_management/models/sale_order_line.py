from odoo import fields, models, _, api
from odoo.exceptions import ValidationError, UserError
from odoo.tools.float_utils import float_round

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    
    product_long = fields.Float(string='Size 3')
    product_width = fields.Float(string='Size 2')
    product_thickness = fields.Float(string='Size 1')
    product_weight = fields.Float(string='Weight (kg)', help="This will be calculated by pricing engine")
    price_method_group = fields.Char(related='product_id.price_method_group')
    api_link = fields.Char(string='API Link', readonly=True)
    specfic_for_customer = fields.Boolean(compute='_compute_specfic_for_customer')
    shipping_amount = fields.Float(string='Shipping Amount')
    price_unit_with_shipping = fields.Float(string='Unit Price With Shipping', compute='_compute_price_unit_with_shipping', store=True)
    notes = fields.Text(string='Detailed Notes')
    order_pricelist_id = fields.Many2one(related='order_id.pricelist_id')
    weight_per_roll = fields.Float(string='Weight per Roll')
    milling_method = fields.Selection([('no', 'None'), ('PHAY2F', '2 Faces'), ('PHAY4F', '4 Faces'), ('PHAY6F', '6 Faces')],
                                      string='Milling Method')
    milling_faces = fields.Selection([('KT1', 'KT1'), ('KT2', 'KT2'), ('KT3', 'KT3'), 
                                      ('KT2andKT3','KT2 and KT3'), ('KT1andKT3', 'KT1 and KT3'), ('KT1andKT2', 'KT1 and KT2')],
                                     string='Milling Faces')
    milling_fee = fields.Float(string='Milling Fee', readonly=True)
    
    @api.constrains('product_thickness', 'product_width', 'product_long')
    def _check_product_thickness(self):
        for r in self:
            if ((r.product_id.product_thickness and r.product_thickness > r.product_id.product_thickness)
                or (r.product_id.product_width and r.product_width > r.product_id.product_width)
                or (r.product_id.product_long and r.product_long > r.product_id.product_long)):
                raise ValidationError(_("Customized size of %s must be smaller or equals to configured size in product", r.product_id.display_name))
                
    def _compute_specfic_for_customer(self):
        for r in self:
            r.specfic_for_customer = False
            if r.product_id.specific_customer_id:
                r.specfic_for_customer = True
    
    @api.depends('shipping_amount', 'price_unit', 'product_weight')
    def _compute_price_unit_with_shipping(self):
        for r in self:
            if r.shipping_amount <= 0 or r.product_weight <= 0:
                r.price_unit_with_shipping = r.price_unit
            else:
                r.price_unit_with_shipping = r.price_unit + float_round((r.shipping_amount/r.product_weight), precision_digits=2)
                
    @api.onchange('product_id')
    def product_id_change(self):
        """ Override this method to set price unit, we will calculate price unit later
        """
        result = super(SaleOrderLine, self).product_id_change()
        
        if self.price_method_group != 'roll':
            self.product_weight = self.product_id.product_weight * self.product_uom_qty
        else:
            self.product_weight = self.weight_per_roll * self.product_uom_qty
        self.price_unit = self.product_id.list_price
        self.product_thickness = self.product_id.product_thickness
        self.product_long = self.product_id.product_long
        self.product_width = self.product_id.product_width
        
        return result
    
    @api.onchange('weight_per_roll')
    def weight_per_roll_change(self):
        if self.price_method_group == 'roll':
            self.product_weight = self.weight_per_roll * self.product_uom_qty
    
    @api.onchange('milling_method', 'milling_faces')      
    def milling_method_change(self):
        if self.milling_method == 'PHAY2F' and self.milling_faces:
            if self.milling_faces not in ('KT1', 'KT2', 'KT3'):
                raise ValidationError(_("PHAY2F doesn't allow %s faces", self.milling_faces))
        if self.milling_method == 'PHAY4F' and self.milling_faces:
            if self.milling_faces not in ('KT2andKT3', 'KT1andKT3', 'KT1andKT2'):
                raise ValidationError(_("PHAY4F doesn't allow %s faces", self.milling_faces))
        if self.milling_method == 'no' or self.milling_method == 'PHAy6F':
            if self.milling_faces:
                raise ValidationError(_("You don't need to select %s face", self.milling_faces))
    
    @api.onchange('product_uom', 'product_uom_qty')
    def product_uom_change(self):
        """ Override this method to set price unit, we will calculate price unit later
        """
        result = super(SaleOrderLine, self).product_uom_change()
        if self.price_method_group != 'roll':
            self.product_weight = self.product_id.product_weight * self.product_uom_qty
        else:
            self.product_weight = self.weight_per_roll * self.product_uom_qty
        return result
    
    def _is_standard_size(self):
        self.ensure_one()
        
        if self.product_id.product_basic_shape_id.has_size1:
            if self.product_thickness != self.product_id.product_thickness:
                return False
        
        if self.product_id.product_basic_shape_id.has_size3:
            if self.product_long != self.product_id.product_long:
                return False
            
        if self.product_id.product_basic_shape_id.has_size2:
            if self.product_width != self.product_id.product_width:
                return False
            
        return True
            
            
    
    @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id', 'shipping_amount', 'product_weight')
    def _compute_amount(self):
        """ Override compute the amounts of the SO line to calculate price_subtotal by weight
        """
        for r in self:
            if r.shipping_amount <= 0 or r.product_weight <= 0:
                price_unit_with_shipping = r.price_unit
            else:
                price_unit_with_shipping = r.price_unit + float_round((r.shipping_amount/r.product_weight), precision_digits=2)
                
            price = price_unit_with_shipping * (1 - (r.discount or 0.0) / 100.0)
            # if r._is_standard_size():
            #     if r.price_method_group != 'roll':
            #         taxes = r.tax_id.compute_all(price, r.order_id.currency_id, r.product_id.product_weight * r.product_uom_qty, 
            #                                      product=r.product_id)
            #     else:
            #         taxes = r.tax_id.compute_all(price, r.order_id.currency_id, r.weight_per_roll * r.product_uom_qty, 
            #                                      product=r.product_id)
            # else:
            #     taxes = r.tax_id.compute_all(price, r.order_id.currency_id, r.product_weight, product=r.product_id)
            
            taxes = r.tax_id.compute_all(price, r.order_id.currency_id, r.product_weight, product=r.product_id)
            
            r.update({
                'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })
