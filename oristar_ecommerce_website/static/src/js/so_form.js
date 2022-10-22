odoo.define('oristar_ecommerce_website.sale_order_form', function(require) {
    "use strict";

    const {Component} = owl;
    const {xml} = owl.tags;
    const {useRef, useDispatch, useState, useStore} = owl.hooks;
     var translate_help = require('oristar_ecommerce_website.translate_help');
    var ajax = require('web.ajax');
    var Dialog = require('web.Dialog');

    class SaleOrderForm extends Component {
        static template = 'OrSaleOrderForm';
        translate_help = translate_help
        constructor() {
            super(...arguments);
            var date_order = this.props.order_data.website_sale_order.date_order;
            var date_order_date = new Date(date_order);
            var date_order_timestamp = date_order_date.getTime();
            var timezone_offset = date_order_date.getTimezoneOffset();
            date_order_timestamp = date_order_timestamp - timezone_offset * 60 * 1000;
            date_order_date = new Date(date_order_timestamp);
            date_order = moment(date_order_date).format('YYYY-MM-DD HH:mm:ss');
            this.props.order_data.website_sale_order.date_order = date_order;
        }
        formatCurrency(value) {
            if(!value) {
                return 0
            }
            return value.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
        }
    }
    return SaleOrderForm;
})