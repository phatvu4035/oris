import requests
import logging
import urllib.parse

from odoo import fields, models, _, api, SUPERUSER_ID
from odoo.http import request
from odoo.exceptions import UserError, ValidationError
from _datetime import timedelta
from werkzeug.urls import url_encode

_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def manually_create_order_line(self, product_id=None, add_qty=0, set_qty=0, options={}, **kwargs):
        self.ensure_one()
        product_context = dict(self.env.context)
        product_context.setdefault('lang', self.sudo().partner_id.lang)
        SaleOrderLineSudo = self.env['sale.order.line'].sudo().with_context(product_context)
        # change lang to get correct name of attributes/values
        product_with_context = self.env['product.product'].with_context(product_context)
        product = product_with_context.browse(int(product_id))

        try:
            if add_qty:
                add_qty = int(add_qty)
        except ValueError:
            add_qty = 1
        try:
            if set_qty:
                set_qty = int(set_qty)
        except ValueError:
            set_qty = 0
        quantity = 0

        if not product:
            raise UserError(_("The given product does not exist therefore it cannot be added to cart."))

        no_variant_attribute_values = kwargs.get('no_variant_attribute_values') or []
        received_no_variant_values = product.env['product.template.attribute.value'].browse(
            [int(ptav['value']) for ptav in no_variant_attribute_values])
        received_combination = product.product_template_attribute_value_ids | received_no_variant_values
        product_template = product.product_tmpl_id

        # handle all cases where incorrect or incomplete data are received
        combination = product_template._get_closest_possible_combination(received_combination)

        # get or create (if dynamic) the correct variant
        product = product_template._create_product_variant(combination)

        if not product:
            raise UserError(_("The given combination does not exist therefore it cannot be added to cart."))

        product_id = product.id
        values = self._website_product_new_dimension(self.id, product_id, qty=1, options=options)

        # add no_variant attributes that were not received
        for ptav in combination.filtered(
                lambda ptav: ptav.attribute_id.create_variant == 'no_variant' and ptav not in received_no_variant_values):
            no_variant_attribute_values.append({
                'value': ptav.id,
            })

        # save no_variant attributes values
        if no_variant_attribute_values:
            values['product_no_variant_attribute_value_ids'] = [
                (6, 0, [int(attribute['value']) for attribute in no_variant_attribute_values])
            ]

        # add is_custom attribute values that were not received
        custom_values = kwargs.get('product_custom_attribute_values') or []
        received_custom_values = product.env['product.template.attribute.value'].browse(
            [int(ptav['custom_product_template_attribute_value_id']) for ptav in custom_values])

        for ptav in combination.filtered(lambda ptav: ptav.is_custom and ptav not in received_custom_values):
            custom_values.append({
                'custom_product_template_attribute_value_id': ptav.id,
                'custom_value': '',
            })

        # save is_custom attributes values
        if custom_values:
            values['product_custom_attribute_value_ids'] = [(0, 0, {
                'custom_product_template_attribute_value_id': custom_value[
                    'custom_product_template_attribute_value_id'],
                'custom_value': custom_value['custom_value']
            }) for custom_value in custom_values]

        # create the line
        order_line = SaleOrderLineSudo.create(values)

        try:
            order_line._compute_tax_id()
        except ValidationError as e:
            # The validation may occur in backend (eg: taxcloud) but should fail silently in frontend
            _logger.debug("ValidationError occurs during tax compute. %s" % (e))
        if add_qty:
            add_qty -= 1

            # compute new quantity
            if set_qty:
                quantity = set_qty
            elif add_qty is not None:
                quantity = order_line.product_uom_qty + (add_qty or 0)

        # Remove zero of negative lines
        if quantity <= 0:
            linked_line = order_line.linked_line_id
            order_line.unlink()
            if linked_line:
                # update description of the parent
                linked_product = product_with_context.browse(linked_line.product_id.id)
                linked_line.name = linked_line.get_sale_order_line_multiline_description_sale(linked_product)
        else:
            # update line
            no_variant_attributes_price_extra = [ptav.price_extra for ptav in
                                                 order_line.product_no_variant_attribute_value_ids]
            values = self.with_context(no_variant_attributes_price_extra=tuple(
                no_variant_attributes_price_extra))._website_product_new_dimension(self.id, product_id, qty=quantity, options=options)
            order = self.sudo().browse(self.id)
            if self.pricelist_id.discount_policy == 'with_discount' and not self.env.context.get('fixed_price'):
                product_context.update({
                    'partner': order.partner_id,
                    'quantity': quantity,
                    'date': order.date_order,
                    'pricelist': order.pricelist_id.id,
                })
            product_with_context = self.env['product.product'].with_context(product_context).with_company(
                order.company_id.id)
            product = product_with_context.browse(product_id)

            order_line.write(values)

            # link a product to the sales order
            if kwargs.get('linked_line_id'):
                linked_line = SaleOrderLineSudo.browse(kwargs['linked_line_id'])
                order_line.write({
                    'linked_line_id': linked_line.id,
                })
                linked_product = product_with_context.browse(linked_line.product_id.id)
                linked_line.name = linked_line.get_sale_order_line_multiline_description_sale(linked_product)
            # Generate the description with everything. This is done after
            # creating because the following related fields have to be set:
            # - product_no_variant_attribute_value_ids
            # - product_custom_attribute_value_ids
            # - linked_line_id
            order_line.name = order_line.get_sale_order_line_multiline_description_sale(product)

        option_lines = self.order_line.filtered(lambda l: l.linked_line_id.id == order_line.id)

        return {'line_id': order_line.id, 'quantity': quantity, 'option_ids': list(set(option_lines.ids))}

    def _website_product_new_dimension(self, order_id, product_id, qty=0, options={}):
        order = self.sudo().browse(order_id)
        product_context = dict(self.env.context)
        product_context.setdefault('lang', order.partner_id.lang)
        product_context.update({
            'partner': order.partner_id,
            'quantity': qty,
            'date': order.date_order,
            'pricelist': order.pricelist_id.id,
        })
        product = self.env['product.product'].with_context(product_context).with_company(order.company_id.id).browse(
            product_id)

        values = {
            'product_id': product_id,
            'product_uom_qty': qty,
            'order_id': order_id,
            'product_uom': product.uom_id.id,
            'price_unit': options.get('price_unit'),
            'product_thickness': options.get('thickness'),
            'product_long': options.get('long'),
            'product_width': options.get('width'),
            'weight_per_roll': options.get('weight_per_roll'),
            'product_weight': options.get('weight'),
            'notes': options.get('notes'),
            'milling_method': options.get('milling_method'),
            'milling_faces': options.get('milling_faces'),
            'discount': 0,
        }
        return values

    def set_default_addresss_to_order(self, partner):
        self.ensure_one()
        for child in partner.child_ids:
            if child.type == 'delivery' and child.default_delivery_address:
                values = {
                    'partner_shipping_id': child.id,
                    'state_id': child.state_id.id if child.state_id else False,
                    'district_id': child.district_id.id if child.district_id else False,
                    'township_id': child.township_id.id if child.township_id else False,
                }
                self.write(values)


    def set_default_inv_addresss_to_order(self, partner):
        self.ensure_one()
        for child in partner.child_ids:
            if child.type == 'invoice' and child.default_delivery_address:
                values = {
                    'partner_invoice_id': child.id,
                }
                self.write(values)
                return
        # if not found default invoice address attach to first invoice address
        if partner.child_ids and partner.child_ids.filtered(lambda c: c.type == 'invoice'):
            first_child = partner.child_ids.filtered(lambda c: c.type == 'invoice')[0]
            values = {
                'partner_invoice_id': first_child.id,
            }
            self.write(values)
            
    
    @api.model
    def _is_working_time(self, utc_offset=0):
        dt = fields.Datetime.now() + timedelta(hours=utc_offset or 0)
        weekday = dt.weekday() #weekday index start from 0 for Monday to 6 for Sunday
        time_hours = timedelta(hours=dt.hour, minutes=dt.minute, seconds=dt.second).total_seconds() / 3600
        if weekday == 6:
            return False
        
        if weekday == 5:
            if time_hours >= 8 and time_hours <= 12:
                return True
            else:
                return False
        
        if time_hours >= 8 and time_hours <= 17:
            return True
        else:
            return False
    
    @api.model
    def _cron_check_non_confirmed_sale_order(self):
        non_confirmed_orders = self.search([('state', 'in', ['sent'])])
        is_working_time = self._is_working_time(utc_offset=7)
        time_threshold = 3
        if self.env.company.offtime_delay_confirmation:
            time_threshold = self.env.company.offtime_delay_confirmation #1 hour for working time, 3 for off-time
        if is_working_time:
            if self.env.company.working_time_delay_confirmation:
                time_threshold = self.env.company.working_time_delay_confirmation
            else:
                time_threshold = 1
        
        notify_2_manager_orders = []
        notify_2_pic_orders = {}
        
        for order in non_confirmed_orders:
            if fields.Datetime.now() - order.create_date > timedelta(hours=time_threshold):
                if order.partner_id.seller_in_charge:
                    if order.partner_id.seller_in_charge.id in notify_2_pic_orders:
                        notify_2_pic_orders[order.partner_id.seller_in_charge.id].append((order.id, order.name))
                    else:
                        notify_2_pic_orders[order.partner_id.seller_in_charge.id] = [(order.id, order.name)]
                else:
                    notify_2_manager_orders.append((order.id, order.name))
                    
        # notify to responsible user
        for partner, orders in notify_2_pic_orders.items():
            refs = ["<a href='/mail/view?%s' data-oe-model='%s' data-oe-id='%d'>%s</a>"
                % (url_encode({'model': self._name, 'res_id': r[0]}), self._name, r[0], r[1]) for r in orders]
            message = _("The following sale orders are not confirmed: %s. Please check them!", ','.join(refs))
            subject = _("[IMPORTANR] Sale orders are not confirmed timely!")
            self.env['mail.thread'].with_user(SUPERUSER_ID).message_notify(
                partner_ids=[partner],
                body=message,
                subject=subject,
                email_layout_xmlid='mail.mail_notification_light')
            
        
        # notify to manager
        if notify_2_manager_orders:
            refs = ["<a href='/mail/view?%s' data-oe-model='%s' data-oe-id='%d'>%s</a>"
                    % (url_encode({'model': self._name, 'res_id': r[0]}), self._name, r[0], r[1]) for r in notify_2_manager_orders]
            message = _("The following sale orders are not confirmed: %s. Please check them!", ','.join(refs))
            subject = _("[IMPORTANR] Sale orders are not confirmed timely!")
            self.env['mail.thread'].with_user(SUPERUSER_ID).message_notify(
                partner_ids=self.env.company.sale_notification_reception_partner_ids.ids,
                body=message,
                subject=subject,
                email_layout_xmlid='mail.mail_notification_light')
