odoo.define('oristar_sale_management.UserSystray', function(require) {
    "use strict";

    var core = require('web.core');
    var Widget = require('web.Widget');
    var SystrayMenu = require('web.SystrayMenu');
    var rpc = require('web.rpc');
    var ActionManager = require('web.ActionManager');
    var session = require('web.session');

    var QWeb = core.qweb;
    var _t = core._t;

    var SOSystray = Widget.extend({
        template: 'oris.systray.SaleOrders',
        events: {
            'click .open-detail': '_openDetailOrder',
            'click .read-so-noti': '_onReadViewNotification',
        },
        init: function () {
            this._super(...arguments);
            this.call('bus_service', 'onNotification', this, this._onNotification);
        },
        start: function() {
            var self = this;
            this._rpc({
                route: '/get_so_notification'
            }).then(function(res) {
                var counter = res.length;
                if (counter > 0) {
                    self.$('.o_notification_counter').text(counter);
                }
                self._updateSaleActivityPreview(res);
            })
            return this._super.apply(this, arguments);
        },
        _updateSaleActivityPreview: function (orders) {
            this.$('.o_mail_systray_dropdown_items').empty();
            var $activies = QWeb.render('or.systray.ActivitySaleOrder.Previews', {
                orders
            });
            this.$('.o_mail_systray_dropdown_items').html($activies);
        },
        _openDetailOrder: function(ev) {
            var $target = $(ev.target);
            var res_id = $target.data('res_id');
            var action = {
                type: 'ir.actions.act_window',
                name: 'Sale Order',
                res_model: 'sale.order',
                view_mode: 'form',
                views: [[false, 'form']],
                context: {},
                res_id: res_id,
            }
            this.do_action(action);
        },
        _onNotification: function(notifications) {
            var self = this;
            for (var notification of notifications) {
                var channel = notification[0];
                var message = notification[1];
                if (channel[1] == 'new_so' && channel[0] == session.db && message.notif_users.includes(session.uid)) {
                    var action = {
                        'type': 'ir.actions.client',
                        'tag': 'display_notification',
                        'params': {
                            'type': 'success',
                            'message': _.str.sprintf(_t("%s has been created"), message['name']),
                        }
                    }
                    this.do_action(action);
                    this._rpc({
                        route: '/get_so_notification'
                    }).then(function (res) {
                        var counter = res.length;
                        if (counter > 0) {
                            self.$('.o_notification_counter').text(counter);
                        }
                        self._updateSaleActivityPreview(res);
                    });
                }
            }
        },
        _onReadViewNotification: function () {
            var self = this;
            setTimeout(function () {
                self.$('.o_notification_counter').text('');
            }, 100)
        }
    });
    SystrayMenu.Items.push(SOSystray);
});