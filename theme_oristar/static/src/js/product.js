odoo.define('theme_oristar.product', function(require) {
    "use strict";

    var ajax = require('web.ajax');
    var utils = require('web.utils');
    var publicWidget = require('web.public.widget');
    var core = require('web.core');
    var _t = core._t;
    var Dialog = require('web.Dialog');
    const wUtils = require('website.utils');

    publicWidget.registry.ProductDetail = publicWidget.Widget.extend({
        selector: '#product_details',
        events: {
            'click .pricing-btn': '_callPriceAPI',
            'change .input-qty': '_callPriceAPI',
            'change #kt1_selection': '_changeKT1Selection',
            'click .size-variant': '_selectSizeVariants',
            'change .sass': '_selectMachineMethod',
            'click .box-img .item': '_selectMillingSurfaces',
            'change .form.or_call_price input[type=text]': '_changeCustomSize',
            'click .milling-sfs .nav-item': '_changeCustomSize',
            'change input[name=dimension_type]': '_changeDimensionType'
        },
        /**
         * @override
         */
        start: function () {
            this.user_product_data =  {
                type: 'standard',
                standard_product_data: {
                    product_thickness: product_thickness,
                    product_long: product_long,
                    product_width: product_width,
                    product_price: list_price,
                    product_weight: product_weight,
                    weight_per_roll: product_weight,
                },
                custom_product_data: {
                    product_thickness: product_thickness,
                    product_long: product_long,
                    product_width: product_width,
                    price_unit: 0,
                    product_weight: product_weight,
                    weight_per_roll: product_weight,
                    milling_method: null,
                    milling_faces: null,
                }
            };
            this.$size_variants = $('.size-variant');
            this.$size_variants.addClass('d-none');
            this.default_product_id = $('input[name=product_id]').val();
            this.default_standard_product_data = Object.assign({}, this.user_product_data.standard_product_data);
            this._updateProductView();
            this._highlightCurrentProductVariant();
            var def = this._super.apply(this, arguments);
            $('.product-deta .box-thumbnail img').each(function () {
                var $elem = $(this);
                var src = $elem.attr('src');
                $elem.closest('.item').attr('data-dot', `<img src=${src} />`);
            })
            $('.product-deta').owlCarousel({
                items: 1,
                loop: true,
                margin: 10,
                nav: false,
                center: true,
                dots: true,
                dotsData: true,
                navText: ['<i class="fas fa-chevron-left"></i>', '<i class="fas fa-chevron-right"></i>'],
                autoplay: false,
                autoplayTimeout: 5000,
                autoplayHoverPause: true,
            });
            // Remove price in product detail
            $('.css_quantity').remove();
            $('.product_price').remove();
            $(".locs").click(function () {
                $(".loc").slideToggle();
            });
            $('input.input-qty').each(function () {
                var $this = $(this),
                    qty = $this.parent().find('.is-form');
                var min = 0;
                $(qty).on('click', function () {
                    var d = Number($this.val());
                    if ($(this).hasClass('minus')) {
                        d = d > min ? d - 1 : 0;
                    } else if ($(this).hasClass('plus')) {
                        d = d < 0 ? 1 : d + 1;
                    }
                    $this.val(d)
                    $this.change()
                });
            });
            this._disableProductForSpecificUser();
            var $add_to_cart = $(`<a href="javascript:void(0)" class="tvgh" id="add_to_cart">
                                                <span>`+_t('Add to Cart')+`</span>
                                                <svg x="0px" y="0px" width="32px" height="32px" viewBox="0 0 32 32">
                                                    <path stroke-dasharray="19.79 19.79" stroke-dashoffset="19.79" fill="none" stroke="#FFFFFF" stroke-width="2" stroke-linecap="square" stroke-miterlimit="10" d="M9,17l3.9,3.9c0.1,0.1,0.2,0.1,0.3,0L23,11"/>
                                                </svg>
                                            </a>`);
            var $buy_now = $(`<button class="mns" id="buy_now" >`+_t('Buy now')+`</button>`);
            var $contact = $(`<a href="/contactus" class="mns mns-contact" >`+ _t('Contact') +`</a>`);
            this.$add_to_cart_btn = $('#add_to_cart').length > 0 ? $('#add_to_cart') : $add_to_cart;
            this.$buy_now = $('#buy_now').length > 0 ? $('#buy_now') : $buy_now;
            this.$contact = $('.mns-contact').length > 0 ? $('.mns-contact') : $contact;
            this._hideAddToCartandBuyNowBtn(this.default_product_id);
            this._setToZeroWhenNoSizeSelected();
            return def;
        },
        _setToZeroWhenNoSizeSelected: function () {
            // if product has many variant size, by default reset all weight, width, long to 0 and readonly
            if (Object.keys(size_variants['kt1_product_ids']).length > 0) {
                $('#or_calc_price_height').val(0).attr('readonly', true);
                $('#or_calc_price_width').val(0).attr('readonly', true);
                $('#or_calc_price_longs').val(0).attr('readonly', true);
                $('#or_calc_price_weight').val(0).attr('readonly', true);
                this.$add_to_cart_btn.detach();
            }
        },
        _callPriceAPI: function(ev) {
            var self = this;
            ev.preventDefault();
            let quantity = $('#or_calc_price_quantity').val() || 0;
            quantity = parseFloat(quantity)
            let width = $('#or_calc_price_width').val();
            width = parseFloat(width)
            let long = $('#or_calc_price_longs').val() || 0;
            long = parseFloat(long)
            let thickness = $('#or_calc_price_height').val() || 0;
            thickness = parseFloat(thickness);
            var weight_per_roll = $('#or_calc_price_weight').val() || 0;
            weight_per_roll = parseFloat(weight_per_roll);
            var weight = weight_per_roll * quantity;
            var standard_price = $('#or_calc_price_standard_price').val() || 0;
            var max_thickness = $('input[name=max_height]').val();
            var standard_thickness = this.user_product_data.standard_product_data.product_thickness;
            var standard_long = this.user_product_data.standard_product_data.product_long;
            var standard_width = this.user_product_data.standard_product_data.product_width;
            var standard_product_price = this.user_product_data.standard_product_data.product_price;
            var standard_weight_per_roll = this.user_product_data.standard_product_data.weight_per_roll;
            var standard_product_weight = this.user_product_data.standard_product_data.product_weight;
            var shouldCallAPI = false;
            if (price_method_group != 'base') {
                shouldCallAPI = true
            }
            if(
                (thickness > 0 && standard_thickness != thickness) ||
                (long > 0 && standard_long != long) ||
                (width > 0 && standard_width != width) ||
                (weight_per_roll > 0 && standard_weight_per_roll != weight_per_roll)
            ) {
                shouldCallAPI = true;
            }
            if (specific_customer_id) {
                shouldCallAPI = false;
            }
            /*
             if product dimension is no different with standard and specific customer for product is defined
             dimension then don't need to call price API
            */
            if(!shouldCallAPI) {
                this.user_product_data.type = 'standard';
                // In case product is plate
                $('#referenceLink').html(`<a href="javascript:void(0)" target="_blank">Link</a>`);

                this._updateProductView();
                return;
            }
            // Validate
            var msg;
            var isInValid = false;
            if($('#or_calc_price_width').length > 0
                && (!$('#or_calc_price_width').val() || isNaN(parseFloat($('#or_calc_price_width').val())))) {
                msg = _t('Invalid KT3 value');
                isInValid = true;
            }
            if($('#or_calc_price_longs').length > 0
                && (!$('#or_calc_price_longs').val() || isNaN(parseFloat($('#or_calc_price_longs').val())))) {
                msg = _t('Invalid KT2 value');
                isInValid = true;
            }
            if($('#or_calc_price_height').length > 0
                && (!$('#or_calc_price_height').val() || isNaN(parseFloat($('#or_calc_price_height').val()))) ) {
                msg = _t('Invalid KT1 value');
                isInValid = true;
            }
            if($('#or_calc_price_weight').length > 0
                && (!$('#or_calc_price_weight').val() || isNaN(parseFloat($('#or_calc_price_weight').val())))) {
                msg = _t('Invalid weight value');
                isInValid = true;
            }
            if(!quantity) {
                msg = _t('Field quantity is required.');
                isInValid = true;
            } else if(!Number.isInteger(parseInt(quantity))) {
                isInValid = true;
                msg = _t('Invalid quantity value.');
            }
            if(max_thickness && thickness > parseFloat(max_thickness)) {
                msg = 'Gía trị chiều dày phải nhỏ hơn hoặc bằng giá trị ' + max_thickness;
                isInValid = true;
            }
            if(isInValid) {
                Dialog.alert(this, msg);
                return;
            }
            $('.tab-summary .indicator-ajax').removeClass('hide');
            // TODO Call to calculation price API
            var product_id = $('#product_details input[name=product_id]').val();
            var g_param = 'long';
            var g_value = long;
            if($('#or_calc_price_weight').length > 0) {
                g_param = 'weight';
                g_value = weight;
            }
            // Milling method
            var phay;
            var milling_face;
            if ($('input[name=radio_phay]').is(':checked')) {
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
            this._rpc({
                route: '/product_calc_price',
                params: {
                    product_id: product_id,
                    options: {
                        qty: quantity,
                        width: width,
                        [g_param]: g_value,
                        thickness: thickness,
                        cost: standard_price,
                        milling_method: phay,
                        milling_faces: milling_face,
                    }
                }
            }).then(function (result) {
                if(result.status) {
                    $('.tab-summary .indicator-ajax').addClass('hide');
                    var price_unit = result.data.price_unit || 0;
                    var weight = result.data.weight || 0;
                    var sub_total = price_unit * weight || 0;
                    sub_total = Math.round(sub_total * 100) / 100;
                    var link = result.data.subtotal || 0;
                    $('#referenceLink').html(`<a href="${link}" target="_blank">Link</a>`);
                    self.user_product_data.type = 'custom';
                    self.user_product_data.custom_product_data.product_thickness = thickness;
                    self.user_product_data.custom_product_data.product_long = long;
                    self.user_product_data.custom_product_data.product_width = width;
                    self.user_product_data.custom_product_data.price_unit = price_unit;
                    self.user_product_data.custom_product_data.product_weight = weight;
                    self.user_product_data.custom_product_data.weight_per_roll = weight_per_roll;
                    self.user_product_data.custom_product_data.milling_method = phay;
                    self.user_product_data.custom_product_data.milling_faces = milling_face;
                    self._updateProductView();
                }
            }).catch(function () {
                $('.tab-summary .indicator-ajax').addClass('hide');
            });
        },
        _disableProductForSpecificUser: function() {
            if(specific_customer_id) {
                $('#or_calc_price_width').attr('readonly', true);
                $('#or_calc_price_longs').attr('readonly', true);
                $('#or_calc_price_height').attr('readonly', true);
                $('#or_calc_price_weight').attr('readonly', true);
            }
        },
        _updateProductView: function() {
            // Set checked for custom dimension
            if(this.user_product_data.type == 'custom') {
                $('#is_custom_dim_val').val(1);
            } else {
                $('#is_custom_dim_val').val(0);
            }
            var quantity = $('input[name=add_qty]').val() || 0;
            quantity = parseInt(quantity);
            var product_thickness = this.user_product_data.standard_product_data.product_thickness;
            var product_long = this.user_product_data.standard_product_data.product_long;
            var product_width = this.user_product_data.standard_product_data.product_width;
            var price_unit = this.user_product_data.standard_product_data.product_price;
            var product_weight = this.user_product_data.standard_product_data.product_weight;
            var weight_per_roll = this.user_product_data.standard_product_data.weight_per_roll;
            var total = price_unit * quantity;
            total = Math.round(total * 100) / 100;
            if(this.user_product_data.type == 'standard' && !specific_customer_id) {
                total = price_unit * product_weight * quantity;
                product_weight = product_weight * quantity;
            } else if(this.user_product_data.type == 'custom') {
                product_thickness = this.user_product_data.custom_product_data.product_thickness;
                product_long = this.user_product_data.custom_product_data.product_long;
                product_width = this.user_product_data.custom_product_data.product_width;
                price_unit = this.user_product_data.custom_product_data.price_unit;
                product_weight = this.user_product_data.custom_product_data.product_weight;
                weight_per_roll = this.user_product_data.custom_product_data.weight_per_roll;
                total = price_unit * product_weight;
                total = Math.round(total * 100) / 100;
            }
            if(total > 0) {
                $('.ct-product .ht-gia h3').removeClass('d-none')
                    .text(total.toFixed(2).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",") + ' VNĐ');
                $('.ct-product .ht-gia p').addClass('d-none');
            } else {
                $('.ct-product .ht-gia h3').addClass('d-none')
                    .text(total.toFixed(2).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",") + ' VNĐ');
                $('.ct-product .ht-gia p').removeClass('d-none');
            }

            if (this.user_product_data.type == 'custom' && $('input[name=radio_nhietluyen]').prop('checked')) {
                $('.text-help-annealing').removeClass('d-none')
            } else {
                $('.text-help-annealing').addClass('d-none')
            }

            $('#add_to_cart').prop('disabled', false);
            $('#buy_now').prop('disabled', false);

            $('#or_calc_price_height').val(product_thickness);
            $('#or_calc_price_width').val(product_width).attr('readonly', !machinable_size2);
            $('#or_calc_price_longs').val(product_long).attr('readonly', !machinable_size3);
            $('#or_calc_price_weight').val(weight_per_roll).attr('readonly', !editable_weight);

            // Update to product form
            $('#height_cart_val').val(product_thickness);
            $('#long_cart_val').val(product_long);
            $('#width_cart_val').val(product_width);
            $('#weight_cart_val').val(product_weight);
            $('#price_unit_cart_val').val(price_unit);
            $('#weight_per_roll').val(weight_per_roll);
            $('#subtotal_price_cart_val').val(total.toFixed(2));
            $('#milling_method_val').val(this.user_product_data.custom_product_data.milling_method);
            $('#milling_faces_val').val(this.user_product_data.custom_product_data.milling_faces);
            if(this.user_product_data.type == 'custom') {
                if($('#nhiet').is(':checked')) {
                    $('.purpose-note').removeClass('d-none');
                } else {
                    $('.purpose-note').addClass('d-none');
                }
            } else {
                $('.purpose-note').addClass('d-none');
            }
        },
        _changeKT1Selection: function (ev) {
            var self = this;
            var $target = $(ev.target);
            var val = $target.val();

            // get product id candidate with the kt1
            var kt1_product_ids = size_variants['kt1_product_ids'];
            var inventory_availables = size_variants['inventory_availables'];
            var product_id = 0
            for (let kp in kt1_product_ids) {
                if (val != 'choose_size' && parseFloat(kp) == parseFloat(val)) {
                    product_id = kt1_product_ids[kp][0]
                }
            }
            this._hideAddToCartandBuyNowBtn(product_id);
            this._updateProductVariantId(product_id);
            this._updateStandardProductData(product_id);
            this._updateProductView();
            if (val == 'choose_size') {
                this._setToZeroWhenNoSizeSelected();
            }
            this.$size_variants.each(function () {
                if ($(this).attr('kt1-attribute') != val) {
                    $(this).hide();
                } else {
                    $(this).removeClass('d-none');
                    $(this).show();
                    $('#or_calc_price_height').val(val).attr('readonly', !machinable_size1);
                }
            });
            this._highlightCurrentProductVariant(product_id);
        },
        _updateProductVariantId: function(product_id) {
            if(product_id) {
                $('#product_details input[name=product_id]').val(product_id);
            } else {
                $('#product_details input[name=product_id]').val(this.default_product_id);
            }
        },
        _updateStandardProductData: function(product_id) {
            var product_data = data_variants[product_id];
            if (!product_data) {
                this.standard_product_data = Object.assign({}, this.default_standard_product_data);
                product_data = Object.assign({}, this.default_standard_product_data);
            }
            this.user_product_data.standard_product_data.product_thickness = product_data.product_thickness;
            this.user_product_data.standard_product_data.product_long = product_data.product_long;
            this.user_product_data.standard_product_data.product_width = product_data.product_width;
            this.user_product_data.standard_product_data.product_price = product_data.list_price || product_data.product_price || 0;
            this.user_product_data.standard_product_data.product_weight = product_data.product_weight;
            this.user_product_data.standard_product_data.weight_per_roll = product_data.product_weight;
            $('#product_details input[name=max_height]').val(product_data.product_thickness);
        },
        _selectSizeVariants: function(ev) {
            $('.size-variant').removeClass('active');
            var $target = $(ev.target);
            $target.addClass('active');
            this.user_product_data.type = 'standard';
            var product_id = $target.data('product-id');
            this._updateProductVariantId(product_id);
            this._updateStandardProductData(product_id);
            // set value from standard to dimension input
            var product_thickness = this.user_product_data.standard_product_data.product_thickness;
            var product_long = this.user_product_data.standard_product_data.product_long;
            var unit_price = this.user_product_data.standard_product_data.product_price;
            var product_weight = this.user_product_data.standard_product_data.product_weight;
            var product_width = this.user_product_data.standard_product_data.product_width;
            var weight_per_roll = this.user_product_data.standard_product_data.weight_per_roll;
            this._hideAddToCartandBuyNowBtn(product_id);
            this._updateProductView();
            var quantity = $('#or_calc_price_quantity').val() || 0;
            this._updatePriceDeclaration(unit_price, product_weight, quantity);
        },
        formatCurrency: function(val) {
            if(!val) {
                return 0
            }
            return val.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
        },
        _highlightCurrentProductVariant: function(product_id) {
            if(!product_id) {
                product_id = this.default_product_id;
            }
            $('.size-variant').each(function() {
                var $this = $(this);
                var variant_id = $this.data('product-id');
                if(parseInt(variant_id) == parseInt(product_id)) {
                   $this.addClass('active');
                } else {
                   $this.removeClass('active');
                }
            });
        },
        _updatePriceDeclaration: function(unit_price, weight, quantity) {

        },
        _selectMachineMethod: function(ev) {
            $('.purpose-note').addClass('d-none');
            $('.milling-sfs').addClass('d-none');
            if($('#nhiet').is(':checked')) {
                $('.purpose-note').removeClass('d-none');
            }
            if ($('#phay').is(':checked')) {
                $('.milling-sfs').removeClass('d-none');
            }
            if ($('#nhiet').is(':checked') && this.user_product_data.type == 'custom') {
                $('.text-help-annealing').removeClass('d-none');
            } else {
                $('.text-help-annealing').addClass('d-none');
            }
        },
        _selectMillingSurfaces: function (ev) {
            $(ev.target).closest('.box-img').find('.item').removeClass('active');
            if($(ev.target).hasClass('item')) {
                $(ev.target).addClass('active');
            } else {
                $(ev.target).closest('.item').addClass('active');
            }
        },
        _changeCustomSize: function(ev) {
            let width = $('#or_calc_price_width').val();
            width = parseFloat(width)
            let long = $('#or_calc_price_longs').val() || 0;
            long = parseFloat(long)
            let thickness = $('#or_calc_price_height').val() || 0;
            thickness = parseFloat(thickness);
            var isSizeValid = true;
            var fit_width = width >= milling_min_limit && width <= milling_max_limit ? true : false;
            var fit_long = long >= milling_min_limit && long <= milling_max_limit ? true : false;
            var fit_thickness = thickness >= milling_min_limit && thickness <= milling_max_limit ? true : false;
            var shouldShowProcessing = false
            var phay_checked = $('#phay').is(':checked');
            $('.milling-sfs .box-img .item').each(function () {
                    var $this = $(this);
                    var kt1 = parseInt($this.data('kt1'));
                    var kt2 = parseInt($this.data('kt2'));
                    var kt3 = parseInt($this.data('kt3'));
                    if (kt1 > 0 && !fit_thickness) {
                        $this.addClass('d-none');
                        return
                    } else if (kt2 > 0 && !fit_width) {
                        $this.addClass('d-none');
                        return
                    } else if (kt3 > 0 && !fit_long) {
                        $this.addClass('d-none');
                        return;
                    }
                    shouldShowProcessing = true;
                    $this.removeClass('d-none');
            });
            if(phay_checked) {
                $('.milling-sfs').removeClass('d-none');
            }
            if (!shouldShowProcessing) {
                $('input[name=radio_phay]').closest('.p-method').addClass('d-none').removeClass('d-flex');
            } else {
                $('input[name=radio_phay]').closest('.p-method').removeClass('d-none').addClass('d-flex');
            }
        },
        _changeDimensionType: function(ev) {
            var $target = $(ev.target);
            this._changeCustomSize()
            if ($target.is(':checked')) {
                $('.machine-phay').removeClass('d-none');
                $('.machine-nhietluyen .annealing').removeClass('d-none');
                $('.machine-nhietluyen .purpose-note').removeClass('d-none');
            } else {
                $('.machine-phay').addClass('d-none');
                $('.machine-nhietluyen .annealing').addClass('d-none');
                $('.machine-nhietluyen .purpose-note').addClass('d-none');
                $('#phay').prop('checked', false);
                $('#nhiet').prop('checked', false);
            }
        },
        _hideAddToCartandBuyNowBtn: function(product_id) {
            // Some product template have multiple product variants
            // some variants is available and some other ones is not
            // This function control the display of 'add to cart' button
            var inventory_availables = size_variants['inventory_availables'];
            if(Object.keys(inventory_availables).length <= 0) {
                return
            }
            this.$add_to_cart_btn.detach();
            this.$buy_now.detach();
            this.$contact.detach();
            if (inventory_availables[product_id]) {
                $('.pricing-btn').after(this.$buy_now)
                $('.pricing-btn').after(this.$add_to_cart_btn)
            } else {
                $('.pricing-btn').after(this.$contact)
            }
        }
    })

    publicWidget.registry.ProductList = publicWidget.Widget.extend({
        selector: '.or_product_list',
        events: {
            'click .sumale .gh': '_onAddProductToCart',
            'click .sumale .mn': '_onAddProductToCart',
        },
        _onAddProductToCart: function (ev) {
            ev.preventDefault();
            var $target = $(ev.target);
            var product_template_id = $target.data('product-template-id');
            var isMn = false;
            var trigger_add_btn = $target;
            if(!$target.hasClass('gh')) {
                var trigger_add_btn = $target.closest('.gh');
                trigger_add_btn.prop('disabled', true);
            }
            if($target.hasClass('mn')) {
                isMn = true;
            }
            this._rpc({
                route: '/oristar_shop/add_to_cart',
                params: {
                    product_template_id
                }
            }).then(function(res) {
                var cart_quantity = res.cart_quantity;
                $('.my_cart_quantity').html(cart_quantity);
                if(res.status = true) {
                    if(isMn) {
                        window.location.href = '/shop/cart';
                    } else if(trigger_add_btn) {
                        trigger_add_btn.html('ĐÃ THÊM');
                        setTimeout(function () {
                            trigger_add_btn.prop('disabled', false);
                            trigger_add_btn.html('THÊM VÀO GIỎ HÀNG');
                        }, 700);
                    }
                }
            });
        },
    })
});