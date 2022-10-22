odoo.define('oristar_ecommerce_website.CartComponentsMixin', function(require) {
    'use strict';

    var core = require('web.core');
    var publicWidget = require('web.public.widget');
    var translate_help = require('oristar_ecommerce_website.translate_help');
    var _t = core._t;
    var QWeb = core.qweb;

    var cart_compnents_xml = '/oristar_ecommerce_website/static/src/xml/cart_components.xml';
    return {
        xmlDependencies: (publicWidget.Widget.prototype.xmlDependencies || []).concat([cart_compnents_xml]),
        order_lines: null,
        order_info_summary: null,
        checkout: null,
        successful_checkout: null,
        credit_information: null,
        payment_methods: null,
        call_to_checkout: null,
        cart_order_info: null,
        order_data: {
            website_sale_order: {},
            order_lines: [],
            partner_shipping: {},
            credit_data: {},
        },
        formatCurrency: function(val, payment_method) {
            if(!val) {
                return 0
            }
            if (payment_method == 'advan') {
                var val = (val*0.7).toFixed(2);
                return val.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
            } else {
                return val.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
            }
        },
        amountWithPaymentMethod: function(val, payment_method) {
            if (payment_method == 'advance') {
                return (val*0.7).toFixed(2)
            } else {
                return val;
            }
        },
        renderOrderLines: function(order_lines) {
            var cart = QWeb.render('orisCartOrderLine', {
                formatCurrency: this.formatCurrency,
                order_lines: order_lines,
                translate_help
            });
            return cart;
        },
        renderOrderInfoSummary: function(payment_method, website_sale_order) {
            var orderInfoSummary = QWeb.render('orisOrderInfoSummary', {
                formatCurrency: this.formatCurrency,
                website_sale_order: website_sale_order,
                payment_method,
                translate_help
            })
            return orderInfoSummary;
        },
        renderCheckout: function (payment_method, website_sale_order, partner_shipping) {
            var payment_method_label = {'debt': _t('DEBT'), 'advan': _t('ADVANCE'), 'pay': _t('PAY')};
            var checkout = QWeb.render('orisCheckout', {
                payment_method: payment_method,
                website_sale_order: website_sale_order,
                partner_shipping: partner_shipping,
                payment_method_label: payment_method_label,
                formatCurrency: this.formatCurrency,
                translate_help
            })
            return checkout;
        },
        renderSuccessfulCheckout: function() {
            var successfulCheckout = QWeb.render('orisSuccessfulCheckout')
            return successfulCheckout;
        },
        renderCreditPayment: function(website_sale_order, partner_shipping, amount_to_pay) {
            var creditPayment = QWeb.render('orisCreditPayment', {
                website_sale_order,
                partner_shipping,
                amount_to_pay,
                formatCurrency: this.formatCurrency,
                translate_help
            })
            return creditPayment;
        },
        renderCreditInformation: function (amount_to_pay, website_sale_order, partner_shipping) {
            var creditInformation = QWeb.render('orisCreditInformation', {
                amount_to_pay,
                website_sale_order,
                partner_shipping,
                formatCurrency: this.formatCurrency,
                translate_help
            })
            return creditInformation;
        },
        renderPaymentMethods: function (payment_method) {
            var paymentMethod = QWeb.render('orisPaymentMethods', {
                can_pay_by_cod,
                user_external_id,
                payment_method,
                formatCurrency: this.formatCurrency,
                translate_help
            });

            return paymentMethod;
        },
        renderCallToCheckoutProcess: function(payment_method, website_sale_order, partner_shipping, credit_limit) {
            var payment_method_label = {'debt': _t('DEBT'), 'advan': _t('ADVANCE'), 'pay': _t('PAY')};
            var should_show_debt_method = true;
            if (credit_limit <= 0) {
                should_show_debt_method = false;
            }
            var callToCheckoutProcess = QWeb.render('orisCallToCheckoutProcess', {
                payment_method,
                user_external_id,
                website_sale_order,
                partner_shipping,
                formatCurrency: this.formatCurrency,
                payment_method_label,
                can_pay_by_cod,
                translate_help,
                should_show_debt_method
            });
            return callToCheckoutProcess
        },
        renderCartOrderInfo: function (payment_method, website_sale_order, partner_shipping, credit_data) {
            var amount_total = website_sale_order.amount_total || 0;
            var current_credit = credit_data.current_credit || 0;
            var credit_limit = credit_data.credit_limit || 0;
            var status = 'full_credit';
            var amount_to_pay = 0;

            if(current_credit + amount_total <= credit_limit || (current_credit == 0 && credit_limit == 0)) {
                status = 'credit';
            }
            if (status == 'full_credit') {
                amount_to_pay = current_credit + amount_total - credit_limit;
            }
            if(status == 'full_credit') {
                return this.renderCreditInformation(amount_to_pay, website_sale_order, partner_shipping);
            } else if(status == 'credit') {
                return this.renderCallToCheckoutProcess(payment_method, website_sale_order, partner_shipping, credit_limit)
            }
        },
        appendComponentToDOM: function (component, $target) {
            $target.appendTo(component);
        },

        detachComponentFromDOM: function(component) {
            $(component).remove();
        },
        _updateCartView: function() {
            var self = this;
            var order_id = parseInt($('input[name=order_id]').val());
            var $drone = $('input[name=drone]:checked');
            var payment_method = $drone.length > 0 ? $drone.val() : '';
            if(isNaN(order_id)) {
                var sale_order = self.order_data.website_sale_order;
                var order_lines = self.order_data.order_lines;
                var partner_shipping = self.order_data.partner_shipping;
                var credit_data = self.order_data.credit_data;
                if(self.order_lines) {
                    self.order_lines.remove();
                }
                self.order_lines = $(self.renderOrderLines(order_lines));
                self.order_lines.appendTo(self.$('.or_cart'));

                if(self.cart_order_info) {
                    self.cart_order_info.remove();
                }
                self.cart_order_info = $(self.renderCartOrderInfo(payment_method, sale_order, partner_shipping, credit_data));
                self.cart_order_info.appendTo(self.$('.thanh-toan'));
                return
            }
            return this._rpc({
                route: "/shop/order/data",
                params: {
                    order_id: order_id
                }
            }).then(function(res) {
                self.order_data = res;
                var sale_order = self.order_data.website_sale_order;
                var order_lines = self.order_data.order_lines;
                var partner_shipping = self.order_data.partner_shipping;
                var credit_data = self.order_data.credit_data;
                $('.or_cart').empty();
                self.order_lines = $(self.renderOrderLines(order_lines));
                self.order_lines.appendTo($('.or_cart'));
                $('.thanh-toan').empty();
                self.cart_order_info = $(self.renderCartOrderInfo(payment_method, sale_order, partner_shipping, credit_data));
                self.cart_order_info.appendTo($('.thanh-toan'));
            });
        },
    }
});