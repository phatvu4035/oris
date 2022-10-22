odoo.define('oristar_ecommerce_website.Order', function (require) {
    "use strict";

    var utils = require('web.utils');
    var publicWidget = require('web.public.widget');
    var core = require('web.core');
    var SaleOrderForm = require('oristar_ecommerce_website.sale_order_form');
    var _t = core._t;
    const { WidgetAdapterMixin, ComponentWrapper } = require('web.OwlCompatibility');
    var Dialog = require('web.Dialog');


    publicWidget.registry.Order = publicWidget.Widget.extend(WidgetAdapterMixin, {
        selector: '.or_portal_orders',
        events: {
            'click .open-order-form': '_openOrderForm',
            'click .cancel-order-btn': '_cancelOrder',
            'click .clone-order-btn': '_cloneOrder',
        },
        /**
         * @override
         */
        start: function () {
            var self = this;
            var def = this._super.apply(this, arguments);
            $('.date-ord').each(function() {
                var $this = $(this);
                var date_text = $this.text();
                date_text = date_text.trim().split(' ')[0];
                $this.text(date_text)
            })
            this._rpc({
                'route': '/get_countries',
            }).then(function(res) {
                self.countries = res;
            });
            this._rpc({
                'route': '/get_res_states',
            }).then(function (res) {
                self.res_states = res;
            })
            return def;
        },
        _openOrderForm: function(ev) {
            var self = this;
            var $target = $(ev.target);
            var order_id = $target.data('order-id');
            // Get order data
            $.blockUI()
            this._rpc({
                route: '/shop/order/data',
                params: {
                    order_id: order_id
                }
            }).then(function (res) {
                var saleOrderForm = new ComponentWrapper(self, SaleOrderForm, {
                    order_data: res,
                    countries: self.countries,
                    res_states: self.res_states
                });
                self.$('#chitiet .modal-dialog').empty();
                saleOrderForm.mount(self.$('#chitiet .modal-dialog').get(0));
                self.$('#chitiet').modal('show');
                $.unblockUI()
            }, function () {
                $.unblockUI()
            })
        },
        _cancelOrder: function(ev) {
            ev.preventDefault();
            var self = this;
            var $target = $(ev.target);
            var order_id = $target.data('order-id');
            Dialog.confirm(
                this,
                _t('Are you sure to cancel this order ?'), {
                    confirm_callback: function () {
                        return self._rpc({
                            route: '/shop/order/cancel',
                            params: {
                                order_id: order_id
                            }
                        }).then(function (res) {
                            if(res.status) {
                                var dialog = new Dialog(self, {
                                    title: _t('Success'),
                                    $content: $('<p>' + _t('Order has been cancelled successfully.') +'</p>'),
                                    buttons: [
                                        {
                                            text: _t('Close'),
                                            classes: 'btn-secondary',
                                            close: true,
                                            click: self._reload.bind(self)
                                        }
                                    ],
                                });
                                dialog.open();
                            } else {
                                var dialog = new Dialog(self, {
                                    title: _t('Failed'),
                                    $content: res.message,
                                    buttons: [
                                        {
                                            text: _t('Close'),
                                            classes: 'btn-secondary',
                                            close: true,
                                        }
                                    ],
                                });

                                dialog.open();
                            }
                        })
                    },
                }
            );
        },
        _reload: function () {
            window.location.reload()
        },
        _cloneOrder: function (ev) {
            ev.preventDefault();
            var self = this;
            var $target = $(ev.target)
            var order_id = $target.data('order-id');
            Dialog.confirm(
                this,
                _t('Are you sure to repurchase this order?'), {
                    confirm_callback: function () {
                        $.blockUI()
                        return self._rpc({
                            route: '/my/orders/clone',
                            params: {
                                order_id
                            }
                        }).then(function (res) {
                            $.unblockUI();
                            if (!res.status) {
                                Dialog.alert(_t('Can not repurchase this order.'));
                                return
                            }
                            var d = new Dialog(self, {
                                title: _t('Success'),
                                $content:  $('<main/>', {
                                    text: _t('The order has been repurchased.'),
                                }),
                                buttons: [
                                    {
                                        text: _t('Close'),
                                        classes: 'btn-secondary o_form_button_cancel',
                                        close: true,
                                    }
                                ],
                            }).open();
                        }, function () {
                            Dialog.alert(this, _t('Something wrong happen.'));
                            setTimeout(function () {
                                window.location.reload()
                            }, 1500);
                            $.unblockUI();
                        })
                    },
                }
            );
        }
    })

});