odoo.define('theme_oristar.website_sale', function (require) {
    'use strict';

    var publicWidget = require('web.public.widget');
    const wUtils = require('website.utils');
    var core = require('web.core');
    var Dialog = require('web.Dialog');

    var _t = core._t;


    publicWidget.registry.WebsiteSale.include({
        /**
         * @override
         */
        _handleAdd: function ($form) {
            var self = this;
            this.$form = $form;

            var productSelector = [
                'input[type="hidden"][name="product_id"]',
                'input[type="radio"][name="product_id"]:checked'
            ];

            var productReady = this.selectOrCreateProduct(
                $form,
                parseInt($form.find(productSelector.join(', ')).first().val(), 10),
                $form.find('.product_template_id').val(),
                false
            );

            return productReady.then(function (productId) {
                $form.find(productSelector.join(', ')).val(productId);

                self.rootProduct = {
                    product_id: productId,
                    quantity: parseFloat($form.find('input[name="add_qty"]').val() || 1),
                    product_custom_attribute_values: self.getCustomVariantValues($form.find('.js_product')),
                    variant_values: self.getSelectedVariantValues($form.find('.js_product')),
                    no_variant_attribute_values: self.getNoVariantAttributeValues($form.find('.js_product'))
                };

                self._submitForm2();
            });
        },
        /**
         * @override
         */
        _submitForm2: function () {
            var self = this;
            let params = this.rootProduct;
            params.add_qty = params.quantity;

            var thickness = $('#height_cart_val').val() || 0;
            var long = $('#long_cart_val').val() || 0;
            var width = $('#width_cart_val').val() || 0;
            var price_unit = $('#price_unit_cart_val').val() || 0;
            var weight_per_roll = $('#weight_per_roll').val() || 0;
            var weight = $('#weight_cart_val').val() || 0;
            var subtotal = $('#subtotal_price_cart_val').val() || 0;

            params.thickness = parseFloat(thickness);
            params.long = parseFloat(long);
            params.width = parseFloat(width);
            params.price_unit = parseFloat(price_unit);
            params.weight_per_roll = parseFloat(weight_per_roll);
            params.weight = parseFloat(weight);
            params.subtotal = parseFloat(subtotal);

            params.product_custom_attribute_values = JSON.stringify(params.product_custom_attribute_values);
            params.no_variant_attribute_values = JSON.stringify(params.no_variant_attribute_values);

            var is_custom_dim = $('#is_custom_dim_val').val() || 0;
            is_custom_dim = parseInt(is_custom_dim)
            var notes = '';
            var purpose = $('textarea[name=purpose]').val();
            var note = $('textarea[name=notes]').val();
            if (note && note.trim()) {
                notes += _t('Note: \n') + note;
            }
            if (purpose && purpose.trim() && is_custom_dim > 0) {
                notes += _t('\nPurpose: \n') + purpose;
            }
            params.notes = notes
            params.order_is_new = true;
            var phay;
            var milling_face;
            if ($('input[name=radio_phay]').is(':checked') && is_custom_dim > 0) {
                phay = $('.milling-sfs .box  .nav-link.active').data('milling_method');
                if(phay == 'PHAY2F') {
                    milling_face = $('.milling-sfs .tab-content #home .box-img .active:not(.d-none)').data('milling_face');
                } else if(phay == 'PHAY4F') {
                    milling_face = $('.milling-sfs .tab-content #menu1 .box-img .active:not(.d-none)').data('milling_face');
                }
            }
            if (phay != 'PHAY6F' && !milling_face) {
                phay = null;
            }
            params.milling_method = phay;
            params.milling_faces = milling_face;
            if (this.isBuyNow) {
                params.express = true;
            }
            return this._rpc({
                route: '/oristar_shop/cart/update',
                params
            }).then(function(res) {
                self.adding_to_cart = false;
                if(res.status == true) {
                    var cart_quantity = res.cart_quantity;
                    $('.my_cart_quantity').html(cart_quantity);
                    if(self.isBuyNow) {
                        window.location.href = '/shop/cart';
                    } else {
                        self.trigger_add_btn.addClass('is-added').find('path').eq(0).animate({
                            //draw the check icon
                            'stroke-dashoffset':0
                        }, 300, function(){
                            setTimeout(function(){
                                self.trigger_add_btn.removeClass('is-added').find('span').on('webkitTransitionEnd otransitionend oTransitionEnd msTransitionEnd transitionend', function(){
                                    //wait for the end of the transition to reset the check icon
                                    self.trigger_add_btn.find('path').eq(0).css('stroke-dashoffset', '19.79');
                                });
                            }, 600);
                        });
                    }
                }
            });
        },
        /**
         * @override
        * */
        _onClickAdd: function(ev) {
            // Compare value in form with value in size input to know have the customer calculated price yet
            let input_width = $('#or_calc_price_width').val();
            input_width = parseFloat(input_width)
            let input_long = $('#or_calc_price_longs').val() || 0;
            input_long = parseFloat(input_long)
            let input_thickness = $('#or_calc_price_height').val() || 0;
            input_thickness = parseFloat(input_thickness);
            var input_weight_per_roll = $('#or_calc_price_weight').val() || 0;
            input_weight_per_roll = parseFloat(input_weight_per_roll);
            var milling_method_val = $('#milling_method_val').val();
            var milling_faces_val = $('#milling_faces_val').val();

            var thickness = $('#height_cart_val').val() || 0;
            thickness = parseFloat(thickness)
            var long = $('#long_cart_val').val() || 0;
            long = parseFloat(long)
            var width = $('#width_cart_val').val() || 0;
            width = parseFloat(width);
            var weight_per_roll = $('#weight_per_roll').val() || 0;
            weight_per_roll = parseFloat(weight_per_roll);
            var phay = '';
            var milling_face = '';
            var is_custom_dim = $('input[name=is_custom_dim_val]').val() || 0;
            is_custom_dim = parseInt(is_custom_dim)
            if ($('input[name=radio_phay]').is(':checked')) {
                phay = $('.milling-sfs .box  .nav-link.active').data('milling_method');
                if(phay == 'PHAY2F') {
                    milling_face = $('.milling-sfs .tab-content #home .box-img .active:not(.d-none)').data('milling_face') || '';
                } else if(phay == 'PHAY4F') {
                    milling_face = $('.milling-sfs .tab-content #menu1 .box-img .active:not(.d-none)').data('milling_face') || '';
                }
            }
            if (phay != 'PHAY6F' && !milling_face) {
                phay = '';
            }

            if((input_width != width || input_long != long || input_thickness != thickness ||
                input_weight_per_roll != weight_per_roll ||
                ((phay != milling_method_val || milling_face != milling_faces_val) &&
                    ($('input[name=radio_phay]').is(':checked') && is_custom_dim > 0) ))) {
                Dialog.alert(this, _t('Please calculate price before add to cart!'));
                return;
            }
            this.trigger_add_btn = $(ev.target);
            if(!this.trigger_add_btn.hasClass('tvgh')) {
                this.trigger_add_btn = this.trigger_add_btn.closest('.tvgh')
            }
            if (this.adding_to_cart) {
                // This force user to finish adding previous item before add next item
                return;
            }
            this.adding_to_cart = true;
            return this._super.apply(this, arguments);
        }
    });
})