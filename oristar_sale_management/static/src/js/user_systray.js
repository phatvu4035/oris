odoo.define('oristar_sale_management.so_systray', function(require) {
    "use strict";

    var core = require('web.core');
    var Widget = require('web.Widget');
    var SystrayMenu = require('web.SystrayMenu');
    var rpc = require('web.rpc');
    var session = require('web.session');

    var QWeb = core.qweb;
    var _t = core._t;

    var UserSystray = Widget.extend({
        template: 'oris.systray.Users',
        events: {
            'click .open-detail': '_openDetailUser',
            'click .read-user-noti': '_onReadViewNotification',
        },
        init: function () {
            this._super(...arguments);
            var self = this;
            self.user_form_view_id = null;
            this._rpc({
                model: 'ir.model.data',
                method: 'search_read',
                domain: [['name','=','view_users_form'], ['module','=','base']],
                fields: ['res_id']
            }).then(function (result) {
                self.user_form_view_id = result[0].res_id
            });
            this.call('bus_service', 'onNotification', this, this._onNotification);
        },
        start: function() {
            var self = this;
            this._rpc({
                route: '/get_users_notification'
            }).then(function(res) {
                var counter = res.length;
                if(counter) {
                    self.$('.o_notification_counter').text(counter);
                }
                self._updateUserActivityPreview(res)
            })
            return this._super.apply(this, arguments);
        },
        _updateUserActivityPreview: function (users) {
            this.$('.o_mail_systray_dropdown_items').empty();
            var $activies = QWeb.render('or.systray.ActivityUser.Previews', {
                users
            });
            this.$('.o_mail_systray_dropdown_items').html($activies);
        },
        _openDetailUser: function(ev) {
            var $target = $(ev.target);
            var res_id = $target.data('res_id');
            var action = {
                type: 'ir.actions.act_window',
                name: 'Users',
                res_model: 'res.users',
                view_mode: 'form',
                views: [[this.user_form_view_id, 'form']],
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
                if (channel[1] == 'new_user' && channel[0] == session.db) {
                    var action = {
                        'type': 'ir.actions.client',
                        'tag': 'display_notification',
                        'params': {
                            'type': 'success',
                            'message': _.str.sprintf(_t("%s has been registered"), message['name']),
                        }
                    }
                    this.do_action(action);
                    this._rpc({
                        route: '/get_users_notification'
                    }).then(function (res) {
                        var counter = res.length;
                        if (counter > 0) {
                            self.$('.o_notification_counter').text(counter);
                        }
                        self._updateUserActivityPreview(res);
                    });
                }
            }
        },
        _onReadViewNotification: function(ev) {
            var self = this;
            setTimeout(function () {
                self.$('.o_notification_counter').text('');
            }, 100)
        }
    });
    SystrayMenu.Items.push(UserSystray);
});