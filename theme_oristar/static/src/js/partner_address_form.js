odoo.define('theme_oristar.partner_address_form', function(require) {
    "use strict";

    const {Component} = owl;
    const {xml} = owl.tags;
    const {useRef, useDispatch, useState, useStore} = owl.hooks;
    var ajax = require('web.ajax');
    var Dialog = require('web.Dialog');
    var core = require('web.core');
    var translate_help = require('theme_oristar.translate_help');

    var _t = core._t;

    class PartnerAddressForm extends Component {
        static template = xml`
            <div class="form">
                <form t-att-action="'/my/address-book/data/'+ props.type" class="portal-for-address" id="or_edit_cart_add_addr" method="POST">
                    <input type="hidden" name="type" t-att-value="props.type"/>
                    <input type="hidden" name="id" t-att-value="props.address_data.id"/>
                    <div class="title">
                        <t t-if="props.type == 'delivery'">
                        <h3>${translate_help('Update delivery address')}</h3>
                        </t>
                        <t t-elif="props.type == 'invoice'">
                        <h3>${translate_help('Update invoice address')}</h3>
                        </t>
                    </div>
                    <div class="form-group row">
                        <div class="col-lg-12">
                            <t t-if="props.type == 'invoice'">
                                <label for="">${translate_help('Company Name')}<span>*</span></label>
                                <input name="name" type="text" class="form-control" placeholder="Oristar" t-att-value="props.address_data.name" />
                            </t>
                            <t t-else="">
                                <label for="">${translate_help('Full Name')}<span>*</span></label>
                                <input name="name" type="text" class="form-control" placeholder="Nguyễn Văn A" t-att-value="props.address_data.name" />
                            </t>
                        </div>
                        <div class="col-lg-6">
                            <label for="">${translate_help('Country')} <span>*</span></label>
                            <div class="select">
                                <select name="country_id" id="" class="form-control" t-on-change="_onCountryChange">
                                    <option value="0">${translate_help('Country')}...</option>
                                    <t t-foreach="props.countries or []" t-as="country">
                                        <option t-att-value="country.id" t-att-selected="country.id == props.address_data.country_id[0] || country.external_id == 'base.vn'">
                                            <t t-esc="country.name" />
                                        </option>
                                    </t>
                                </select>
                            </div>
                        </div>
                        <div class="col-lg-6">
                            <label for="">${translate_help('State')} <span>*</span></label>
                            <div class="select">
                                <select name="state_id" id="" class="form-control" t-on-change="selectResState">
                                    <option value="">${translate_help('State')} ...</option>
                                    <t t-foreach="props.res_states or []" t-as="state">
                                        <option
                                                t-att-value="state.id"
                                                t-att-data-country_id="state.country_id"
                                                t-att-selected="state.id == props.address_data.state_id[0]"
                                        >
                                            <t t-esc="state.name" />
                                        </option>
                                    </t>
                                </select>
                            </div>
                        </div>
                        <div class="col-lg-4">
                            <label for="">${translate_help('City')} <span>*</span></label>
                            <input name="city" type="text" class="form-control" t-att-value="props.address_data.city || ''" />
                        </div>
                        <div class="col-lg-4">
                            <label for="">${translate_help('District')} <span>*</span></label>
                            <div class="select">
                                <select name="district_id" id="" class="form-control" t-on-change="selectDistrict">
                                    <option value="">${translate_help('District')}...</option>
                                    <t t-if="props.address_data.district_id.length > 0">
                                        <option t-att-selected="true" t-att-value="props.address_data.district_id[0]">
                                        <t t-esc="props.address_data.district_id[1]"/>
                                        </option>
                                    </t>
                                </select>
                            </div>
                        </div>
                        <div class="col-lg-4">
                            <label for="">${translate_help('Township')}</label>
                            <div class="select">
                                <select name="township_id" id="" class="form-control">
                                    <option value="">${translate_help('Township')}...</option>
                                    <t t-if="props.address_data.township_id.length > 0">
                                        <option t-att-selected="true" t-att-value="props.address_data.township_id[0]">
                                            <t t-esc="props.address_data.township_id[1]"/>
                                        </option>
                                    </t>
                                </select>
                            </div>
                        </div>
                        <div class="col-lg-12">
                            <label for="">${translate_help('Detailed Address')}<span>*</span></label>
                            <input name="street" type="text" class="form-control" t-att-value="props.address_data.street"/>
                        </div>
                        <div class="col-lg-12">
                            <label for="">${translate_help('ZIP / Postal Code')}</label>
                            <input name="zip" type="text" class="form-control" t-att-value="props.address_data.zip"/>
                        </div>
                        
                        <t t-if="props.type == 'invoice'">
                            <div class="col-lg-12">
                                <label for="">${translate_help('TAX Number')} <span>*</span></label>
                                <input name="vat" type="text" class="form-control" t-att-value="props.address_data.vat"/>
                            </div>
                        </t>
                        <t t-else="">
                            <div class="col-lg-12">
                                <label for="">${translate_help('Phone')} <span>*</span></label>
                                <input name="phone" type="text" class="form-control" t-att-value="props.address_data.phone"/>
                            </div>
                        </t>
                        
                        <div class="col-lg-12">
                            <t t-if="props.type == 'invoice'">
                                <label for="">${translate_help('Invoice Email')}<span class="be">  ${translate_help('Please enter correct email format')}. ${translate_help('Ex')} : haianhzz123@gmail.com</span></label>
                            </t>
                            <t t-else="">
                                <label for="">Email<span class="be">  ${translate_help('Please enter correct email format')}. ${translate_help('Ex')} : haianhzz123@gmail.com</span></label>
                            </t>
                            <input name="email" type="text" class="form-control" t-att-value="props.address_data.email"/>
                        </div>
                        <div class="col-lg-12">
                            <t t-if="!props.my_address">
                                <div class="text-right">
                                    <a href="javascript:void(0);" class="btn-tm edit-addr-btn" t-on-click="_updateAddress">${translate_help('Update')}</a>
                                    <a href="javascript:void(0);" class="btn-d">${translate_help('Close')}</a>
                                </div>
                            </t>
                            <t t-else="">
                                <div class="text-center">
                                    <a href="javascript:void(0);" class="btn-tm edit-addr-btn" t-on-click="_updateAddress">${translate_help('Update')}</a>
                                </div>
                            </t>
                        </div>
                    </div>
                </form>
            </div>
        `
        constructor() {
            super(...arguments);
        }
        selectResState(ev) {
            var $target = $(ev.target);
            var $form = $target.closest('form');
            var state_id = $target.val();
            this._loadDistrictAndTownship(state_id, $form);
        }
        _loadDistrict(state_id, $form) {
            ajax.rpc(
                '/address_district', {state_id}
            ).then(function(res) {
                var $district = $form.find('select[name=district_id]');
                $district.empty();
                _.map(res, function (d) {
                    $district.append(`<option value="${d.id}">${d.name}</option>`)
                });
            });
        }
        _loadTownship(state_id, district_id , $form) {
            ajax.rpc('/address_township', {
                state_id,
                district_id: district_id ? district_id : 0,
            }).then(function(res) {
                var $township = $form.find('select[name=township_id]');
                $township.empty();
                _.map(res, function (d) {
                    $township.append(`<option value="${d.id}">${d.name}</option>`)
                });
            });
        }
        _loadDistrictAndTownship(state_id, $form) {
            this._loadDistrict(state_id, $form);
            this._loadTownship(state_id, 0, $form);
        }
        selectDistrict(ev) {
            var $target = $(ev.target);
            var $form = $target.closest('form');
            var district_id = $target.val();
            ajax.rpc('/address_township', {
                district_id
            }).then(function(res) {
                var $township = $form.find('select[name=township_id]');
                $township.empty();
                _.map(res, function (d) {
                    $township.append(`<option value="${d.id}">${d.name}</option>`)
                });
            });
        }
        mounted() {
            var self = this;
            this.$state_options = {};
            $(this.el).find('select[name=state_id]').each(function() {
                var $state_options = $(this).find('option:not(:first)');
                $state_options.detach();
                var rs = self._createRandomString();
                $(this).closest('form').find('select[name=country_id]').data('is', rs);
                self.$state_options[rs] = $state_options;
                var $form = $(this).closest('form');
                var country_id = $(this).closest('form').find('select[name=country_id]').val();
                var $display_states = self.$state_options[rs].filter('[data-country_id=' + country_id + ']');
                $display_states.appendTo($(this)).show();
                var state_id = $form.find('select[name=state_id]').val();
                if (state_id) {
                    self._loadDistrict(state_id, $form)
                }
                var district_id = $form.find('select[name=district_id]').val();
                district_id = district_id ? district_id : 0;
                self._loadTownship(state_id, district_id, $form)
            });
        }
        _createRandomString() {
            var r = (Math.random() + 1).toString(36).substring(2);
            return r;
        }
        _onCountryChange(ev) {
            var $target = $(ev.target);
            var rs = $target.data('is');
            if(!this.$state_options[rs]) {
                return;
            }
            this.$state_options[rs].detach();
            var selected_country_id = $target.val();
            var $display_states = this.$state_options[rs].filter('[data-country_id=' + selected_country_id + ']');
            $display_states.appendTo($target.closest('form').find('select[name=state_id]')).show();
            var state_id = $target.closest('form').find('select[name=state_id]').val();
            if(parseInt(state_id) > 0) {
                this._loadDistrictAndTownship(state_id, $target.closest('form'));
            }
        }
        _updateAddress(ev) {
            var $target = $(ev.target);
            var self = this;
            var data = $target.closest('.portal-for-address').serializeArray();
            var params = {}
            for (var i = 0; i < data.length; i++) {
                var d = data[i];
                params[d.name] = d.value;
            }
            if(!this._validateInputAddress(params)) {
                return;
            }
            ajax.rpc('/my/address-book/data/'+params.type, params).then(function(res) {
                if(res.status) {
                    var d = new Dialog(self, {
                        title: _t('Success'),
                        $content:  $('<main/>', {
                            text: _t('The address has been updated successful.'),
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
                        $target.closest('#suadiachi').modal('hide')
                        window.location.reload();
                    });
                    return false;
                } else {
                    Dialog.alert(self, res.message);
                    return false;
                }
            });
        }
        _validateInputAddress(params) {
            var required_fields = ['name', 'country_id', 'state_id', 'district_id', 'phone', 'street'];
            var field_labels = {
                'name': _t('Full Name'),
                'country_id': _t('Country'),
                'state_id': _t('State'),
                'district_id': _t('District'),
                'phone': _t('Phone'),
                'street': _t('Detailed Address'),
            }
            for(var i = 0; i < required_fields.length; i++) {
                var f = required_fields[i];
                if (params['type'] == 'invoice' && f == 'phone') {
                    continue
                }
                if(!params[f]) {
                    Dialog.alert(this, _.str.sprintf(_t("Field %s is required."), field_labels[f]));
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
        }
        regexPhoneNumber(str) {
            const regexPhoneNumber = /^\+?\d{1,4}?[-.\s]?\(?\d{1,3}?\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}$/;

            if (str.match(regexPhoneNumber)) {
                return true;
            } else {
                Dialog.alert(this, _t('Phone is invalid!'));
                return false;
            }
        }
        regexEmailAddress(str) {
            const regexEmail = /^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*$/;
            if (str.match(regexEmail)) {
                return true;
            } else {
                Dialog.alert(this, _t('Invalid email address.'));
                return false;
            }
        }
    }
    return PartnerAddressForm;
})