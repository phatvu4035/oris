odoo.define('theme_oristar.oristar_menu', function(require) {
    'use strict';

    var publicWidget = require('web.public.widget');
    var core = require('web.core');
    var _t = core._t;

    var timeout;

    // Remove unnecessary element on menu
    $(document).ready(function() {
        $('#top_menu .o_wsale_my_cart').remove();
        $('#top_menu .js_usermenu').closest('li').remove();
        $('#top_menu .o_no_autohide_item').remove();
    });

    publicWidget.registry.OristarWebsiteSaleCart = publicWidget.Widget.extend({
        selector: '.header-cart a[href$="/shop/cart"]',
        events: {
            'mouseenter': '_onMouseEnter',
            'mouseleave': '_onMouseLeave',
            'click': '_onClick',
        },
        /**
         * @constructor
         */
        init: function () {
            this._super.apply(this, arguments);
            this._popoverRPC = null;
        },
        /**
         * @override
         */
        start: function () {
            this.$el.popover({
                trigger: 'manual',
                animation: true,
                html: true,
                title: function () {
                    return _t("My Cart");
                },
                container: 'body',
                placement: 'auto',
                template: '<div class="popover mycart-popover" role="tooltip"><div class="arrow"></div><h3 class="popover-header"></h3><div class="popover-body"></div></div>'
            });
            return this._super.apply(this, arguments);
        },

        //--------------------------------------------------------------------------
        // Handlers
        //--------------------------------------------------------------------------

        /**
         * @private
         * @param {Event} ev
         */
        _onMouseEnter: function (ev) {
            var self = this;
            clearTimeout(timeout);
            $(this.selector).not(ev.currentTarget).popover('hide');
            timeout = setTimeout(function () {
                if (!self.$el.is(':hover') || $('.mycart-popover:visible').length) {
                    return;
                }
                self._popoverRPC = $.get("/shop/cart", {
                    type: 'popover',
                }).then(function (data) {
                    self.$el.data("bs.popover").config.content = data;
                    self.$el.popover("show");
                    $('.popover').on('mouseleave', function () {
                        self.$el.trigger('mouseleave');
                    });
                });
            }, 300);
        },
        /**
         * @private
         * @param {Event} ev
         */
        _onMouseLeave: function (ev) {
            var self = this;
            setTimeout(function () {
                if ($('.popover:hover').length) {
                    return;
                }
                if (!self.$el.is(':hover')) {
                   self.$el.popover('hide');
                }
            }, 1000);
        },
        /**
         * @private
         * @param {Event} ev
         */
        _onClick: function (ev) {
            // When clicking on the cart link, prevent any popover to show up (by
            // clearing the related setTimeout) and, if a popover rpc is ongoing,
            // wait for it to be completed before going to the link's href. Indeed,
            // going to that page may perform the same computation the popover rpc
            // is already doing.
            clearTimeout(timeout);
            if (this._popoverRPC && this._popoverRPC.state() === 'pending') {
                ev.preventDefault();
                var href = ev.currentTarget.href;
                this._popoverRPC.then(function () {
                    window.location.href = href;
                });
            }
        },
    })
});