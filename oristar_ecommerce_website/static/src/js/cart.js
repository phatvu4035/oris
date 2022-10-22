odoo.define('oristar_ecommerce_website', function(require) {
    'use strict';
    var publicWidget = require('web.public.widget');
    var core = require('web.core');
    var wSaleUtils = require('website_sale.utils');
    var Dialog = require('web.Dialog');
    var CartComponentsMixin = require('oristar_ecommerce_website.CartComponentsMixin');
    const { WidgetAdapterMixin, ComponentWrapper } = require('web.OwlCompatibility');
    var PartnerAddressForm = require('oristar_ecommerce_website.partner_address_form');
    var translate_help = require('oristar_ecommerce_website.translate_help');

    var _t = core._t;

    publicWidget.registry.websiteSaleCartPage = publicWidget.Widget.extend(WidgetAdapterMixin, CartComponentsMixin, {
        selector: '.or_website_sale',
        events: {
            'click .or_cart .js_delete_product': '_onClickDeleteProduct',
            'change .or_cart .js_quantity[data-product-id]': '_onChangeCartQuantity',
            'change input[name=drone]': '_onChangePayMethod',
            'click .or_cart .quantity .plus.is-form': '_onPlusQuantity',
            'click .or_cart .quantity .minus.is-form': '_onMinusQuantity',
            'click .open_addr_modal': function() {
                this.$('#giaohang').modal('show')
            },
            'click .open_invoice_addr_modal': function() {
                this.$('#hoadon').modal('show')
            },
            'click .thanh-toan .btn-do': '_openCartPayment',
            'click .open-update-addr': '_openEditAddressForm',
            'click .open-delete-addr': '_openDeleteAddress',
            'change input[name=create_custom_declaration]': '_changeCustomDeclaration'
        },
        /**
         * @override
         */
        start: function () {
            var self = this;
            var def = this._super.apply(this, arguments);
            this._rpc({
                'route': '/get_countries',
            }).then(function(res) {
                self.countries = res;
            });
            this._rpc({
                'route': '/get_res_states',
            }).then(function (res) {
                self.res_states = res;
            });
            // This value is for optimise performance
            this.editting_cart = false;
            this._updateCartView();
            return def;
        },
        _onPlusQuantity: function (ev) {
            ev.preventDefault();
            if(!this.editting_cart) {
                var $target = $(ev.target);
                var $input_quantity = $target.prev('.js_quantity');
                var input_quantity = $input_quantity.val();
                $input_quantity.val(parseInt(input_quantity) + 1);
                $input_quantity.change();
            }
        },
        _onMinusQuantity: function (ev) {
            ev.preventDefault();
            if(!this.editting_cart) {
                var $target = $(ev.target);
                var $input_quantity = $target.next('.js_quantity');
                var input_quantity = $input_quantity.val();
                input_quantity = parseInt(input_quantity) - 1 < 0 ? 0 : parseInt(input_quantity) - 1;
                $input_quantity.val(input_quantity);
                $input_quantity.change();
            }
        },
        /**
         * @private
         * @param {Event} ev
         */
        _onChangeCartQuantity: function (ev) {
            var $input = $(ev.currentTarget);
            if ($input.data('update_change')) {
                return;
            }
            var value = parseInt($input.val() || 0, 10);
            if (isNaN(value)) {
                value = 1;
            }
            var $dom = $input.closest('tr');
            // var default_price = parseFloat($dom.find('.text-danger > span.oe_currency_value').text());
            var $dom_optional = $dom.nextUntil(':not(.optional_product.info)');
            var line_id = parseInt($input.data('line-id'), 10);
            var productIDs = [parseInt($input.data('product-id'), 10)];
            this.editting_cart = true;
            this._changeCartQuantity($input, value, $dom_optional, line_id, productIDs);
        },
        /**
         * @private
         */
        _changeCartQuantity: function ($input, value, $dom_optional, line_id, productIDs) {
            var self = this;
            _.each($dom_optional, function (elem) {
                $(elem).find('.js_quantity').text(value);
                productIDs.push($(elem).find('span[data-product-id]').data('product-id'));
            });
            $input.data('update_change', true);
            this._rpc({
                route: "/shop/cart/update_json",
                params: {
                    line_id: line_id,
                    product_id: parseInt($input.data('product-id'), 10),
                    set_qty: value
                },
            }).then(function (data) {
                self.editting_cart = false;
                $input.data('update_change', false);
                var cart_quantity = data.cart_quantity;
                $('.my_cart_quantity').html(cart_quantity);
                var check_value = parseInt($input.val() || 0, 10);
                if (isNaN(check_value)) {
                    check_value = 1;
                }
                if (value !== check_value) {
                    $input.trigger('change');
                    return;
                }
                if (!data.cart_quantity) {
                    return window.location = '/shop/cart';
                }
                $input.val(data.quantity);
                self._updateCartView();
            });
        },
        /**
         * @private
        * */
        _onClickDeleteProduct: function (ev) {
            ev.preventDefault();
            $(ev.currentTarget).closest('tr').find('.js_quantity').val(0).trigger('change');
        },
        _onChangePayMethod: function(ev) {
            var self = this;
            var $target = $(ev.target);
            var val = $target.val();
            var sale_order = CartComponentsMixin.o_order_data ? CartComponentsMixin.o_order_data.website_sale_order : self.order_data.website_sale_order;
            var partner_shipping = CartComponentsMixin.o_order_data ? CartComponentsMixin.o_order_data.partner_shipping : self.order_data.partner_shipping;
            var credit_data =CartComponentsMixin.o_order_data ? CartComponentsMixin.o_order_data.credit_data : self.order_data.credit_data;
            $('.thanh-toan').empty();
            self.cart_order_info = $(self.renderCartOrderInfo(val, sale_order, partner_shipping, credit_data));
            self.cart_order_info.appendTo(self.$('.thanh-toan'));
        },
        _openCartPayment: function (ev) {
            var tt_method = $('input[name=drone]:checked').val();
            if(!tt_method) {
                Dialog.alert(this, _t('You need to select payment method in order to order.'));
                return;
            }
            $('#thanhtoan').modal('show');
        },
        _openEditAddressForm: function(ev) {
            ev.preventDefault()
            var $target = $(ev.currentTarget);
            var self = this;
            var address_id = $target.data('addrid');
            var type = $target.data('type');
            $.blockUI()
            this._rpc({
                route: '/my/address-data',
                params: {
                    address_id: address_id
                }
            }).then(function(res) {
                var partnerAddressForm = new ComponentWrapper(self, PartnerAddressForm, {
                    address_data: res[0],
                    countries: self.countries,
                    res_states: self.res_states,
                    type: type
                });
                self.$('#suadiachi .modal-content').empty();
                partnerAddressForm.mount($('#suadiachi .modal-content').get(0));
                // Wait to render state because there are over 8000 option html tags for states
                setTimeout(function() {
                    $('#suadiachi').modal('show');
                    $.unblockUI();
                }, 500);
            }, function () {
                Dialog.alert(this, _t('Something wrong happen.'));
                setTimeout(function () {
                    window.location.reload()
                }, 1500);
                $.unblockUI();
            })
        },
        _openDeleteAddress: function(ev) {
            ev.preventDefault()
            var $target = $(ev.currentTarget);
            var self = this;
            var address_id = $target.data('addrid');
            Dialog.confirm(
                this,
                _t('Are you sure to delete this address?'), {
                    confirm_callback: function () {
                        return self._rpc({
                            route: '/my/address-book/delete',
                            params: {
                                child_id: address_id,
                            }
                        })
                        .then(function (res) {
                            if (res.status == true) {
                                Dialog.alert(self, _t('Address has been deleted.'))
                                window.location.reload();
                                return
                            } else {
                                Dialog.alert(self, _t('Can not delete the address.'))
                                window.location.reload();
                                return
                            }
                        });
                    },
                }
            );
        },
        _changeCustomDeclaration: function(ev) {
            var $target = $(ev.target);
            var self = this;
            var order_id = $('input[name=order_id]').first().val();
            if (!order_id) {
                console.error('There is no order id or cart is empty.')
            }
            $.blockUI()
            this._rpc({
                route: '/shop/cart/update-custom-declaration',
                params: {
                    order_id,
                    create_custom_declaration: $target.is(':checked'),
                }
            }).then(function (res) {
                if ($target.is(':checked')) {
                    var msg = _t('Custom declaration created.')
                } else {
                    var msg = _t('Save order successfully.')
                }
                if(res.status) {
                    self._updateCartView();
                    $.unblockUI();
                    var d = new Dialog(this, {
                        title: _t('Success'),
                        $content:  $('<main/>', {
                            text: msg,
                        }),
                        buttons: [
                            {
                                text: _t('Close'),
                                classes: 'btn-secondary o_form_button_cancel',
                                close: true,
                            }
                        ],
                    }).open();
                }
            }, function () {
                Dialog.alert(this, _t('Something wrong happen.'));
                setTimeout(function () {
                    window.location.reload()
                }, 1500);
                $.unblockUI();
            })
        }
    });
    publicWidget.registry.confirmCartpage = publicWidget.Widget.extend({
        selector: '.or_website_sale .thanh-toan',
        events: {
            'click #thanhcongs': '_confirmCart',
            'click .closeThanhtoan': '_closeThanhToanModal'
        },
        _confirmCart: function (ev) {
            ev.preventDefault();
            var self = this;
            var $target = $(ev.target);
            var order_id = $target.data('order-id');
            var address_id = $target.data('address-id');
            if(!address_id) {
                Dialog.alert(this, _t('You must select delivery address before order.'));
                return;
            }
            $.blockUI()
            this._rpc({
                route: '/oristar_shop/confirm-order',
                params: {
                    order_id,
                    address_id,
                }
            }).then(function (res) {
                $.unblockUI();
                if(res.status == true) {
                    $('#thanhcong').modal('show');
                } else {
                    Dialog.alert(self, res.message);
                    return;
                }
            }, function () {
                Dialog.alert(this, _t('Something wrong happen.'));
                setTimeout(function () {
                    window.location.reload()
                }, 1500);
                $.unblockUI();
            });
        },
        _closeThanhToanModal: function(ev) {
            ev.preventDefault();
            $('#thanhtoan').modal('hide');
        }
    });
    publicWidget.registry.modalCartPage = publicWidget.Widget.extend(CartComponentsMixin, {
        selector: '.or_website_sale .diachi',
        events: {
            'click .btn-d, .inv-btn-d': '_onCloseAddrModal',
            'click .addr-btn': '_onAddAddress',
            'click .inv-addr-btn': '_onAddInvoiceAddress',
            'click .select-addr': '_onSelectAddress',
            'click .select-inv-addr': '_onSelectInvAddress',
        },
        /**
         * @override
         */
        start: function () {
            var self = this;
            var def = this._super.apply(this, arguments);
            return def;
        },
        _onCloseAddrModal: function (ev) {
            ev.preventDefault();
            this.$target.modal('hide');
        },
        _onSelectAddress: function (ev) {
            var self = this;
            ev.preventDefault();
            var $target = $(ev.target);
            var address_id = $target.data('address-id');
            // Update address id when select address
            $('#thanhtoan .btn-do').data('address-id', address_id);
            var addr_name = $target.closest('.item-layout').find('.addr_name').text();
            var addr_phone = $target.closest('.item-layout').find('.addr_phone').text();
            var addr_street = $target.closest('.item-layout').find('.addr_street').text();
            var address = `
                <h3>${translate_help('Shipping Address')} <span><a type="button" class="open_addr_modal small"> Thay đổi</a></span></h3>
                <p class="addr_name">${translate_help('Customer Name')} : <span>${addr_name}</span></p>
                <p class="addr_phone">${translate_help('Phone')} : <span>${addr_phone}</span></p>
                <p class="addr_street">${translate_help('Address')} : <span>${addr_street}</span></p>
            `;
            $('.title.shipping_address').html(address);
            this.$target.modal('hide');
            // Calculate shipping amount
            var order_id = $target.data('order-id');
            if (!order_id) {
                Dialog.alert(this, 'Bạn cần phải chọn sản phẩm trước khi đặt hàng.');
                return;
            }
            $.blockUI()
            this._rpc({
                route: '/order/shipping-price',
                params: {
                    order_id,
                    address_id
                }
            }).then(function(data) {
                $.unblockUI();
                var updated_view = self._updateCartView();
                if (updated_view) {
                    updated_view.then(function () {
                        CartComponentsMixin.o_order_data = self.order_data;
                    })
                }
            }, function () {
                Dialog.alert(this, _t('Something wrong happen.'));
                setTimeout(function () {
                    window.location.reload()
                }, 1500);
                $.unblockUI();
            })
        },
        _onSelectInvAddress: function(ev) {
            var self = this;
            ev.preventDefault();
            var $target = $(ev.target);
            var address_id = $target.data('address-id');
            // Update address id when select address
            $('#thanhtoan .btn-do').data('invoice-address-id', address_id);
            var addr_name = $target.closest('.item-layout').find('.addr_inv_name').text();
            var addr_phone = $target.closest('.item-layout').find('.addr_inv_phone').text();
            var addr_street = $target.closest('.item-layout').find('.addr_inv_street').text();
            var address = `
                <h3>${translate_help('Invoice Address')} <span><a type="button" class="open_invoice_addr_modal small"> Thay đổi</a></span></h3>
                <p class="addr_inv_name">${translate_help('Customer Name')} : <span>${addr_name}</span></p>
                <p class="addr_inv_phone">${translate_help('Phone')} : <span>${addr_phone}</span></p>
                <p class="addr_inv_street">${translate_help('Address')} : <span>${addr_street}</span></p>
            `;
            this.$target.modal('hide');
            var order_id = $target.data('order-id');
            if (!order_id) {
                Dialog.alert(this, 'Bạn cần phải chọn sản phẩm trước khi đặt hàng.');
                return;
            }
            $.blockUI()
            this._rpc({
                route: '/order/select-invoice-address',
                params: {
                    order_id,
                    address_id
                }
            }).then(function(data) {
                $.unblockUI()
                self._updateCartView();
            })
            $('.title.invoice_address').html(address);
        },
        _updateAddress: function(ev) {
            var $target = $(ev.target);
            var self = this;
            var data = this.$('#or_cart_add_addr').serializeArray();
            var params = {}
            for (var i = 0; i < data.length; i++) {
                var d = data[i];
                params[d.name] = d.value;
            }
            if(!this._validateInputAddress(params)) {
                return;
            }
            this._rpc({
                route: '/my/address-book/data/'+params.type,
                params
            }).then(function(res) {
                if(res.status) {
                    var d = new Dialog(self, {
                        title: _t('Success'),
                        $content:  $('<main/>', {
                            text: _t('The address has been added.'),
                        }),
                        buttons: [
                            {
                                text: _t('Close'),
                                classes: 'btn-secondary o_form_button_cancel',
                                close: true,
                            }
                        ],
                    }).open();
                    d.on('closed', d, function() {
                        window.location.reload();
                    });
                    self.$target.modal('hide');
                    return false;
                } else {
                    Dialog.alert(self, res.message);
                    return false;
                }
            });
        },
        _onAddAddress: function(ev) {
            this._updateAddress(ev);
            ev.preventDefault()
        },
        _onAddInvoiceAddress: function(ev) {
            var self = this;
            var $target = $(ev.target);
            var data = this.$('#or_cart_add_inv_addr').serializeArray();
            var params = {}
            for (var i = 0; i < data.length; i++) {
                var d = data[i];
                params[d.name] = d.value;
            }
            if(!this._validateInputAddress(params)) {
                return;
            }
            this._rpc({
                route: '/my/address-book/data/invoice',
                params
            }).then(function(res) {
                if(res.status) {
                    var d = new Dialog(self, {
                        title: _t('Success'),
                        $content:  $('<main/>', {
                            text: _t('The address has been added.'),
                        }),
                        buttons: [
                            {
                                text: _t('Close'),
                                classes: 'btn-secondary o_form_button_cancel',
                                close: true,
                            }
                        ],
                    }).open();
                    d.on('closed', d, function() {
                        window.location.reload();
                    });
                    self.$target.modal('hide');
                    return false;
                } else {
                    Dialog.alert(self, res.message);
                    return false;
                }
            });
            ev.preventDefault()
        },
        _validateInputAddress: function(params, type='delivery') {
            var required_fields = ['name', 'country_id', 'state_id', 'district_id', 'phone', 'street'];
            var field_labels = {
                'name': type == 'delivery' ? _t('Full Name') : _t('Company Name'),
                'country_id': _t('Country'),
                'state_id': _t('State'),
                'district_id': _t('District'),
                'phone': _t('Phone'),
                'type': _t('Address Type'),
                'street': _t('Detailed Address'),
            }
            for(var i = 0; i < required_fields.length; i++) {
                var f = required_fields[i];
                if (params['type'] == 'invoice' && f == 'phone') {
                    continue
                }
                if(!params[f]) {
                    Dialog.alert(this, 'Trường ' + field_labels[f] + ' là bắt buộc.');
                    return false;
                }
            }
            if(params['phone'] || (!params['phone'] && params['type'] == 'delivery')) {
                if(!this.regexPhoneNumber(params['phone'])) {
                    return false;
                }
            }
            if(params['email'] && !this.regexEmailAddress(params['email'])) {
                return false;
            }
            return true;
        },
        regexPhoneNumber: function(str) {
            const regexPhoneNumber = /^\+?\d{1,4}?[-.\s]?\(?\d{1,3}?\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}$/;

            if (str.match(regexPhoneNumber)) {
                return true;
            } else {
                Dialog.alert(this, _t('Invalid phone number.'));
                return false;
            }
        },
        regexEmailAddress: function(str) {
            const regexEmail = /^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*$/;
            if (str.match(regexEmail)) {
                return true;
            } else {
                Dialog.alert(this, _t('Invalid email address.'));
                return false;
            }
        }
    });
});