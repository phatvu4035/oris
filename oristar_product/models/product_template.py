import logging

from odoo import fields, models, _, api

_logger = logging.getLogger(__name__)

METHOD_TYPE_SELECTION = [
    ('thep_tam_day', 'Thép tấm dày'),
    ('thep_tam_la', 'Thép tấm lá'),
    ('thep_tam', 'Thép tấm'),
    ('dong_bery', 'Đồng bery'),
    ('thep_dung_cu', 'Thép dụng cụ'),
    ('dong_tam_la', 'Đồng tấm lá'),
    ('dong_hop_kim_tam_day', 'Đồng hợp kim tấm dày'),
    ('dong_tam_day', 'Đồng tấm dày'),
    ('nhom_hop_kim_day', 'Nhôm hợp kim dày'),
    ('nhom_hop_kim_mong', 'Nhôm hợp kim mỏng'),
    ('dong_hop_kim', 'Đồng hợp kim'),
    ('dong_tinh_che', 'Đồng tinh chế'),
    ('nhom_hop_kim', 'Nhôm hợp kim'),
    ('nhom_khong_hop_kim', 'Nhôm không hợp kim'),
    ('dong_thanh', 'Đồng thanh'),
    ('dong_hop_kim_thanh', 'Đồng hợp kim thanh'),
    ('nhom_thanh', 'Nhôm thanh'),
    ('thep_thanh', 'Thép thanh'),
    ('dong_bery_thanh', 'Đồng bery thanh'),
    ('nhom_khong_hop_kim_cuon', 'Nhôm không hợp kim cuộn'),
    ('nhom_hop_kim_cuon', 'Nhôm hợp kim cuộn'),
    ('dong_tinh_che_tam_la', 'Đồng tinh chế tấm lá'),
    ('dong_hop_kim_tam_la', 'Đồng hợp kim tấm lá'),
    ('thep_la_cuon', 'Thép lá cuộn'),
    ('by_priceunit_and_weight', 'Theo đơn giá và khối lượng')
]

PLATE_PRICE_METHOD = ['thep_tam_day', 'thep_tam_la', 'thep_tam', 'dong_bery', 'thep_dung_cu', 'dong_tam_la',
    'dong_hop_kim_tam_day', 'dong_tam_day', 'nhom_hop_kim_day', 'nhom_hop_kim_mong', 'dong_hop_kim', 'dong_tinh_che',
    'nhom_hop_kim', 'nhom_khong_hop_kim']

BAR_PRICE_METHOD = ['dong_thanh', 'dong_hop_kim_thanh', 'nhom_thanh', 'thep_thanh', 'dong_bery_thanh']

ROLL_PRICE_METHOD = ['nhom_khong_hop_kim_cuon', 'nhom_hop_kim_cuon', 'dong_tinh_che_tam_la',
    'dong_hop_kim_tam_la', 'thep_la_cuon']

BY_PRICE_UNIT_AND_WEIGHT = ['by_priceunit_and_weight']

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    # TODO add default value for some required fields by adding loaded data and default method
    featured_product = fields.Boolean(string='Featured Product')
    product_origin = fields.Many2one('res.country', string='Origin', index=True)
    short_description = fields.Text(string='Short Description')
    product_material_category_id = fields.Many2one('product.material.category', string='Material Category', 
                                                   index=True, required=True)
    product_material_id = fields.Many2one('product.material', string='Material', index=True, required=True,
                                          domain="[('id', 'in', available_product_material_ids)]")
    product_basic_shape_id = fields.Many2one('product.basic.shape', string='Basic Shape', index=True,
                                             required=True)
    product_detailed_shape_id = fields.Many2one('product.detailed.shape', string='Detailed Shape', index=True,
                                                domain="[('id', 'in', available_product_detailed_shape_ids)]")
    product_alloy_id = fields.Many2one('product.alloy', string='Grades', index=True, required=True,
                                       domain="[('id', 'in', available_product_alloy_ids)]")
    product_stiffness_id = fields.Many2one('product.stiffness', string='Temper', index=True, required=True,
                                           domain="[('id', 'in', available_product_stiffness_ids)]")
    product_surface = fields.Selection([('2b', '2B'), ('ba', 'BA')], string='Surface')
    
    price_method_type = fields.Selection(selection=METHOD_TYPE_SELECTION, string='Price Method Type')
    price_method_group = fields.Char(string='Price Method Group', compute='_compute_price_method_group')
    specific_customer_id = fields.Many2one('res.partner', string='Specific Customer')
    
    
    # == compute fields to filter above product attributes
    available_product_material_ids = fields.Many2many('product.material', 
                                                      compute='_compute_available_product_material_ids',
                                                      help="Technical field to filter material based on "
                                                      "selected material category.")
    available_product_detailed_shape_ids = fields.Many2many('product.detailed.shape', 
                                                            compute='_compute_available_product_detailed_shape_ids',
                                                            help="Technical field to filter detailed shape based on "
                                                            "selected basic shape")
    available_product_alloy_ids = fields.Many2many('product.alloy', 
                                                   compute='_compute_available_product_alloy_ids',
                                                   help="Technical field to filter alloy based on selected material")
    available_product_stiffness_ids = fields.Many2many('product.stiffness', 
                                                       compute='_compute_available_product_stiffness_ids',
                                                       help="Technical field to filter temper based on selected grades and material")
    
    @api.depends('product_material_category_id')
    def _compute_available_product_material_ids(self):
        for r in self:
            r.available_product_material_ids = r.product_material_category_id.product_material_ids
    
    @api.depends('product_basic_shape_id')
    def _compute_available_product_detailed_shape_ids(self):
        for r in self:
            r.available_product_detailed_shape_ids = r.product_basic_shape_id.product_detailed_shape_ids
    
    @api.depends('product_material_id')
    def _compute_available_product_alloy_ids(self):
        for r in self:
            r.available_product_alloy_ids = r.product_material_id.product_alloy_ids
            
    @api.depends('product_material_id', 'product_alloy_id')
    def _compute_available_product_stiffness_ids(self):
        for r in self:
            r.available_product_stiffness_ids = self.env['product.stiffness'].search([('product_material_id', '=', r.product_material_id.id),
                                                                                      ('product_alloy_id', '=', r.product_alloy_id.id)])
        
    @api.depends('price_method_type')
    def _compute_price_method_group(self):
        for r in self:
            if r.price_method_type in PLATE_PRICE_METHOD:
                r.price_method_group = 'plate'
            elif r.price_method_type in BAR_PRICE_METHOD:
                r.price_method_group = 'bar'
            elif r.price_method_type in ROLL_PRICE_METHOD:
                r.price_method_group = 'roll'
            elif r.price_method_type in BY_PRICE_UNIT_AND_WEIGHT:
                r.price_method_group = 'base'
            else:
                r.price_method_group = ''


    def parse_size_variants(self):
        size_variants = self.attribute_line_ids
        res = {
            'kt1_product_ids': {},
            'kt1_sizes': {},
            'inventory_availables': {}
        }
        kt1_product_ids = res.get('kt1_product_ids')
        kt1_sizes = res.get('kt1_sizes')
        inventory_availables = res.get('inventory_availables')
        for product in self.product_variant_ids:
            product = product.sudo()
            value_ids = product.product_template_attribute_value_ids
            for val in value_ids:
                product_attribute = val.attribute_id
                pattr_external_id = product_attribute.get_external_id().get(product_attribute.id, '')
                if pattr_external_id == 'oristar_ecommerce_website.kt1_variant_attr':
                    kt1 = product.product_thickness
                    kt2 = product.product_width
                    kt3 = product.product_long
                    name = str(kt1)
                    if product.product_basic_shape_id and product.product_basic_shape_id.has_size2 and kt2:
                        name += 'x' + str(kt2)
                    if product.product_basic_shape_id and product.product_basic_shape_id.has_size3 and kt3:
                        name += 'x' + str(kt3)
                    p = kt1_product_ids.get(kt1) or []
                    s = kt1_sizes.get(kt1) or []
                    p.append(product.id)
                    s.append(name)
                    kt1_product_ids.update({kt1: p})
                    kt1_sizes.update({kt1: s})
                    inv = 1 if product.inventory_available else 0
                    inventory_availables.update({product.id: inv})
        return res

    def _get_data_variants(self, partner, pricelist):
        self.ensure_one()
        res = {}
        for product in self.product_variant_ids:
            res.update({product.id: {
                'product_thickness': product.product_thickness,
                'product_long': product.product_long,
                'product_width': product.product_width,
                'list_price': product.get_list_price_product_tmpl_by_pricelist(partner, pricelist),
                'product_weight': product.product_weight,
            }})
        return res

    def should_display_surf2(self):
        self.ensure_one()
        tam = 'oristar_product.product_basic_shape_01'
        thanh_dac = 'oristar_product.product_basic_shape_02'
        thanh_rong = 'oristar_product.product_basic_shape_03'
        thanh_dinhhinh = 'oristar_product.product_basic_shape_04'
        surf2 = [tam, thanh_dac, thanh_rong, thanh_dinhhinh]
        shape_exid = ''
        if self.product_basic_shape_id:
            shape_exid = self.product_basic_shape_id.get_external_id().get(self.product_basic_shape_id.id)
        if shape_exid in surf2:
            return True
        return False

    def should_display_surf46(self):
        tam = 'oristar_product.product_basic_shape_01'
        thanh_dac = 'oristar_product.product_basic_shape_02'
        chu_nhat = 'oristar_product.product_detailed_shape_00'
        shape_exid = ''
        if self.product_basic_shape_id:
            shape_exid = self.product_basic_shape_id.get_external_id().get(self.product_basic_shape_id.id)
        detailed_shape_exid = ''
        if self.product_detailed_shape_id:
            detailed_shape_exid = self.product_detailed_shape_id.get_external_id().get(self.product_detailed_shape_id.id)
        if (shape_exid == thanh_dac and detailed_shape_exid == chu_nhat) or shape_exid == tam:
            return True
        return False

    def should_display_annealing(self):
        thep_dungcu_1 = 'oristar_product.product_material_14'
        thep_dungcu_2 = 'oristar_product.product_material_15'
        thep_dac_biet = 'oristar_product.product_material_category_03'

        tam = 'oristar_product.product_basic_shape_01'
        thanh_dac = 'oristar_product.product_basic_shape_02'
        thanh_rong = 'oristar_product.product_basic_shape_03'
        thanh_dinhhinh = 'oristar_product.product_basic_shape_04'
        shapes = [tam, thanh_dac, thanh_rong, thanh_dinhhinh]

        thepdc = [thep_dungcu_1, thep_dungcu_2]
        shape_exid = ''
        if self.product_basic_shape_id:
            shape_exid = self.product_basic_shape_id.get_external_id().get(self.product_basic_shape_id.id)

        mat_exid = ''
        if self.product_material_id:
            mat_exid = self.product_material_id.get_external_id().get(self.product_material_id.id)

        cat_mat_exid = ''
        if self.product_material_category_id:
             cat_mat_exid = self.product_material_category_id.get_external_id().get(self.product_material_category_id.id)

        if (mat_exid in thepdc or cat_mat_exid == thep_dac_biet) and shape_exid in shapes:
            return True
        return False

    def sync_kt1_variant(self, tmp_id, vals):
        product_template = self.browse(tmp_id)
        if len(vals) <= 0 or not product_template:
            return False
        attribute_kt1 = self.env.ref('oristar_ecommerce_website.kt1_variant_attr')

        # =====================================================================================================
        # STEP 1:
        # Remove product variant have erp id not in vals
        # -----------------------------------------------------------------------------------------------------
        for product in product_template.product_variant_ids:
            should_remove = True
            for val in vals:
                if val.get('erp_id') == product.erp_id:
                    should_remove = False
            if should_remove:
                ptav_value_ids = product.product_template_attribute_value_ids
                ptav_value_ids.filtered(lambda ptav_value: ptav_value.product_tmpl_id == product_template).unlink()

        # =====================================================================================================
        # STEP 2:
        # add new product attribute value it it does not exist
        # -----------------------------------------------------------------------------------------------------
        new_attribute_values = self.env['product.attribute.value'].browse()
        all_attribute_values = self.env['product.attribute.value'].browse()
        for val in vals:
            searched_attr_value = self.env['product.attribute.value'].search([
                ('name', '=', str(val['product_thickness'])),
                ('attribute_id', '=', attribute_kt1.id)
            ])
            if not searched_attr_value:
                newly_created_attr_val = self.env['product.attribute.value'].create({
                    'name': str(val['product_thickness']),
                    'attribute_id': attribute_kt1.id
                })
                all_attribute_values |= newly_created_attr_val
            else:
                all_attribute_values |= searched_attr_value

        # =====================================================================================================
        # STEP 3:
        # Find the compatible line to match to newly product attribute value, if attribute line does not exist
        # add all product attribute value
        # -----------------------------------------------------------------------------------------------------
        tmp_line_kt1s = product_template.attribute_line_ids.filtered(lambda line: line.attribute_id == attribute_kt1)
        current_kt1_attr_values = tmp_line_kt1s.value_ids
        if not tmp_line_kt1s:
            tmp_line_kt1 = self.env['product.template.attribute.line'].create({
                'product_tmpl_id': tmp_id,
                'attribute_id': attribute_kt1.id,
                'value_ids': [(6, 0, all_attribute_values.ids)]
            })
            product_template.write({
                'attribute_line_ids': [(4, tmp_line_kt1.id)]
            })
        else:
            tmp_line_kt1 = tmp_line_kt1s[:1]
            value_id_args = []
            for av in all_attribute_values.filtered(lambda v: v not in current_kt1_attr_values):
                value_id_args.append((4, av.id))
            if value_id_args:
                tmp_line_kt1.write({
                    'value_ids': value_id_args
                })

        # =====================================================================================================
        # STEP 4.1:
        # Update values for product
        # -----------------------------------------------------------------------------------------------------
        products = self.env['product.product'].search([('product_tmpl_id', '=', tmp_id), '|', ('active', '=', True), ('active', '=', False)])
        for product in products:
            for val in vals:
                if val.get('erp_id') == product.erp_id:
                    product.action_unarchive()
                    product.write(val)

        # =====================================================================================================
        # STEP 4.2:
        # update product variant for newly create attribute value
        # -----------------------------------------------------------------------------------------------------
        for nav in all_attribute_values.filtered(lambda v: v not in current_kt1_attr_values):
            newly_ptav = self.env['product.template.attribute.value'].search([
                ('product_attribute_value_id', '=', nav.id),
                ('product_tmpl_id', '=', tmp_id),
                ('attribute_line_id', '=', tmp_line_kt1.id)
            ])
            newly_product = newly_ptav.ptav_product_variant_ids[:1]
            for val in vals:
                should_remove_newly = False
                if float(val.get('product_thickness')) == float(nav.name):
                    for product in products:
                            if product.erp_id == val.get('erp_id'):
                                newly_product.unlink()
                                product.write({
                                    'product_template_attribute_value_ids': [(6, 0, newly_ptav.ids)]
                                })
                                should_remove_newly = True
                                break
                if not should_remove_newly:
                    if float(val.get('product_thickness')) == float(nav.name):
                        newly_product.write(val)

        # =====================================================================================================
        # STEP 5:
        # rematch product variant to product attribute value
        # -----------------------------------------------------------------------------------------------------
        products = self.env['product.product'].search(
            [('product_tmpl_id', '=', tmp_id), '|', ('active', '=', True), ('active', '=', False)])
        for product in products:
            for tmp_attribute_line in product_template.attribute_line_ids:
                product_attr_values = tmp_attribute_line.value_ids
                for av in product_attr_values:
                    if float(av.name) == float(product.product_thickness):
                        ptav_val = self.env['product.template.attribute.value'].search([
                            ('product_attribute_value_id', '=', av.id),
                            ('attribute_line_id', '=', tmp_attribute_line.id),
                            ('product_tmpl_id', '=', tmp_id),
                            ('attribute_id', '=', attribute_kt1.id),
                        ])
                        ptav_val.ptav_product_variant_ids.write({
                            'product_template_attribute_value_ids': [(5, 0, 0)]
                        })
                        ptav_val.ptav_product_variant_ids.flush()
                        product.write({
                            'product_template_attribute_value_ids': [(6, 0, ptav_val.ids)]
                        })
                        product.flush()

        # =====================================================================================================
        # STEP 6:
        # find product attribute value should not be in  template to remove
        # -----------------------------------------------------------------------------------------------------
        for tmp_attribute_line in product_template.attribute_line_ids:
            if tmp_attribute_line.attribute_id != attribute_kt1:
                continue
            product_attr_values = tmp_attribute_line.value_ids
            values_to_remove = []
            for av in product_attr_values:
                should_remove = True
                for val in vals:
                    if float(val.get('product_thickness')) == float(av.name):
                        should_remove = False
                if should_remove:
                    values_to_remove.append(av.id)
            if values_to_remove:
                values_to_remove_args = []
                for vtr in values_to_remove:
                    values_to_remove_args.append((3, vtr, 0))
                product_template.write({
                    'attribute_line_ids': [[1, tmp_attribute_line.id, {
                        'value_ids': values_to_remove_args
                    }]]
                })
            if len(values_to_remove) == len(product_attr_values):
                product_template.write({
                    'attribute_line_ids': [
                        (3, tmp_attribute_line.id)
                    ]
                })
        # In case new erp id but thickness of that erp id already in product template attribute value
        for nav in all_attribute_values.filtered(lambda v: v in current_kt1_attr_values):
            ptav = self.env['product.template.attribute.value'].search([
                ('product_attribute_value_id', '=', nav.id),
                ('product_tmpl_id', '=', tmp_id),
                ('attribute_line_id', '=', tmp_line_kt1.id)
            ])
            product_variant = ptav.ptav_product_variant_ids[:1]
            for val in vals:
                if float(val.get('product_thickness')) == float(nav.name):
                    is_pv_in_vals = False
                    for val2 in vals:
                        if product_variant.erp_id == val2.get('erp_id'):
                            is_pv_in_vals = True
                            break
                    if not is_pv_in_vals:
                        product_variant.write(val)
        return True

    def add_size_variant(self, tmp_id, val):
        product_template = self.browse(tmp_id)
        if not product_template:
            return False
        # check product with erp_id exist
        searched_product = self.env['product.product'].search(
            [('erp_id', '=', val.get('erp_id')), '|', ('active', '=', True), ('active', '=', False)])
        if searched_product:
            searched_product.action_unarchive()
            searched_product.write(val)

        attribute_kt1 = self.env.ref('oristar_ecommerce_website.kt1_variant_attr')
        variant_name = str(val['product_thickness'])
        if val.get('product_width'):
            variant_name += 'x'+str(val.get('product_width'))
        if val.get('product_long'):
            variant_name += 'x' + str(val.get('product_long'))
        attr_value = self.env['product.attribute.value'].search([
            ('name', '=', variant_name),
            ('attribute_id', '=', attribute_kt1.id)
        ], limit=1)
        if not attr_value:
            attr_value = self.env['product.attribute.value'].create({
                'name': variant_name,
                'attribute_id': attribute_kt1.id
            })

        tmp_line_kt1s = product_template.attribute_line_ids.filtered(lambda line: line.attribute_id == attribute_kt1)
        current_kt1_attr_values = tmp_line_kt1s.value_ids

        if not tmp_line_kt1s:
            tmp_line_kt1 = self.env['product.template.attribute.line'].create({
                'product_tmpl_id': tmp_id,
                'attribute_id': attribute_kt1.id,
                'value_ids': [(6, 0, attr_value.ids)]
            })
            product_template.write({
                'attribute_line_ids': [(4, tmp_line_kt1.id)]
            })
        else:
            tmp_line_kt1 = tmp_line_kt1s[:1]
            tmp_line_kt1.write({
                'value_ids': [(4, attr_value.id)]
            })

        newly_ptav = self.env['product.template.attribute.value'].search([
            ('product_attribute_value_id', '=', attr_value.id),
            ('product_tmpl_id', '=', tmp_id),
            ('attribute_line_id', '=', tmp_line_kt1.id)
        ])
        newly_product = newly_ptav.ptav_product_variant_ids[:1]
        if searched_product and newly_product != searched_product:
            newly_product.write({
                'product_template_attribute_value_ids': [(5, 0, 0)]
            })
            newly_product.flush()
            val.update({
                'product_template_attribute_value_ids': [(6, 0, newly_ptav.ids)],
                'product_tmpl_id': tmp_id
            })
            searched_product.write(val)
            newly_product.unlink()
        else:
            newly_product.write(val)
        return True
