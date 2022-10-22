odoo.define('theme_oristar.AddressBook', function(require) {
    "use strict";

    var utils = require('web.utils');
    var publicWidget = require('web.public.widget');
    var core = require('web.core');
    var Dialog = require('web.Dialog');
    var Dialog = require('web.Dialog');
    var PartnerAddressForm = require('theme_oristar.partner_address_form');
    const { WidgetAdapterMixin, ComponentWrapper } = require('web.OwlCompatibility');
    var translate_help = require('theme_oristar.translate_help');

    var _t = core._t;

    publicWidget.registry.AddressBook = publicWidget.Widget.extend({
        selector: '.or_portal_address_book',
        events: {
            'click .set-default-addr': '_onUpdateDefaultAddr',
            'click .delete-addr': '_onDeleteAddr',
            'click .edit-addr': '_onEditAddr',
            'click .save-address-btn': '_onSaveAddress',
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
            return def;
        },
        _onUpdateDefaultAddr: function(ev) {
            ev.preventDefault();
            var self = this;
            var $target = $(ev.target)
            var child_id = $target.data('child-id');
            var type = $target.data('type');
            this._rpc({
                route: '/my/address-book/default',
                params: {
                    type,
                    child_id,
                }
            }).then(function(res) {
                if(res.status == true) {
                    self.$('.df-btn').addClass('btn-luu set-default-addr').text(_t('Set as default'));
                    $target.removeClass('btn-luu set-default-addr').text('Default');
                } else {
                    Dialog.alert(_t('Can not set as default'));
                }
            })
        },
        _onDeleteAddr: function (ev) {
            ev.preventDefault();
            var self = this;
            var $target = $(ev.target)
            var child_id = $target.data('child-id');
            this._rpc({
                route: '/my/address-book/delete',
                params: {
                    child_id : child_id,
                }
            }).then(function(res) {
                if(res.status == true) {
                    window.location.reload()
                } else {
                    Dialog.alert(_t('Can not delete this address.'));
                }
            })
        },
        _onEditAddr: function (ev) {
            ev.preventDefault();
            var self = this;
            var $target = $(ev.target);
            var address_id = $target.data('address-id');
            var type = $target.data('type');
            if (!address_id) {
                console.error('Address id is not defined.')
                return;
            }
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
                    type: type,
                    my_address: true
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
        _onSaveAddress: function (ev) {
            ev.preventDefault()
            var self = this;
            var data = $(ev.target).closest('form').serializeArray();
            var $modal_target = $(ev.target).closest('.modal')
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
                    var d = new Dialog(this, {
                        title: _t('Success'),
                        $content:  $('<main/>', {
                            text: _t('Save address successfully.'),
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
                    $modal_target.modal('hide');
                    return false;
                }
            }, function() {
                Dialog.alert(self, _t('Something wrong happend.'));
                setTimeout(function () {
                    window.location.reload()
                }, 1500)
            });
            ev.preventDefault();
        },
        _validateInputAddress: function(params) {
            var required_fields = ['name', 'country_id', 'state_id', 'district_id', 'phone', 'type', 'street'];
            var field_labels = {
                'name': params['type'] == 'delivery' ? _t('Full Name') : _t('Company Name'),
                'country_id': _t('Country'),
                'state_id': _t('State'),
                'district_id': _t('District'),
                'phone': _t('Phone'),
                'type': _t('Address Type'),
                'street': _t('Detailed Address'),
            }
            for(var i = 0; i < required_fields.length; i++) {
                var f = required_fields[i];
                if(!params[f]) {
                    Dialog.alert(this, _.str.sprintf(_t("Field %s is required."), field_labels[f]));
                    return false;
                }
            }
            // Validate phone number
            if(!this.regexPhoneNumber(params['phone'])) {
                return false;
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
                Dialog.alert(this, _t('Phone is invalid!'));
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
    })
})