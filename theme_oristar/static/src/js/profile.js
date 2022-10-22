odoo.define('theme_oristar.UploadFile', function (require) {
    "use strict";

    var utils = require('web.utils');
    var publicWidget = require('web.public.widget');
    var core = require('web.core');
    var _t = core._t;
    var Dialog = require('web.Dialog');

    publicWidget.registry.AccountImageUpload = publicWidget.Widget.extend({
        selector: '.portal-profile-form',
        events: {
            'click .ta': function (ev) {
                this.$('.profile_input_file').click();
                ev.preventDefault();
            },
            'change .profile_input_file': '_onSelectFile',
            'click .xa': function(ev) {
                $('.profile-avatar-source').attr('src', '/web/static/src/img/placeholder.png')
                ev.preventDefault();
                this.$('input[name=image_1920]').val(false);
            },
        },
        init: function (parent, options) {
            this._super.apply(this, arguments);
            this.useFileAPI = !!window.FileReader;
            this.max_upload_size = 128 * 1024 * 1024;
        },
        start: function () {
            var self = this;
            // Validate form account
            this.$target.submit(function () {
                var phone = $('input[name=phone]').val();
                if(phone && !self.regexPhoneNumber(phone)) {
                    Dialog.alert(self, _t('Invalid phone number.'));
                    return false;
                }
            })
            if(this.$('.portal-image-1920').val()) {
                var file = this.$('.portal-image-1920').val();
                this.$('.profile-avatar-source').attr('src', 'data:image/jpg;base64,'+file)
            }
            return this._super.apply(this, arguments);
        },
        _onSelectFile: function(ev) {
            var self = this;
            var file_node = ev.target;
            if ((this.useFileAPI && file_node.files.length) || (!this.useFileAPI && $(file_node).val() !== '')) {
                var file = file_node.files[0];
                if (file.size > this.max_upload_size) {
                    var msg = _t("The selected file exceed the maximum file size of %s.");
                    this.do_warn(_t("File upload"), _.str.sprintf(msg, utils.human_size(this.max_upload_size)));
                    return false;
                }
                utils.getDataURLFromFile(file).then(function (data) {
                    self.on_file_uploaded(file.size, file.name, file.type, data);
                });
            }
        },
        on_file_uploaded: function(size, name) {
            if (size === false) {
            this.do_warn(false, _t("There was a problem while uploading your file"));
                // TODO: use crashmanager
                console.warn("Error while uploading file : ", name);
            } else {
                this.on_file_uploaded_and_valid.apply(this, arguments);
            }
        },
        on_file_uploaded_and_valid: function (size, name, content_type, file_base64) {
            var data = file_base64.split(',')[1];
            $('.profile-avatar-source').attr('src', file_base64);
            this.$('input[name=image_1920]').val(data)
        },
        regexPhoneNumber: function(str) {
            const regexPhoneNumber = /^\+?\d{1,4}?[-.\s]?\(?\d{1,3}?\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}$/;

            if (str.match(regexPhoneNumber)) {
                return true;
            } else {
                return false;
            }
        }
    });

    publicWidget.registry.LoadAddress = publicWidget.Widget.extend({
        selector: '.portal-for-address',
        events: {
            'change select[name="country_id"]': '_onCountryChange',
            'change select[name=state_id]': '_onStateChange',
            'change select[name=district_id]': '_onDistrictChange',
        },
        /**
         * @override
         */
        start: function () {
            var def = this._super.apply(this, arguments);
            var self = this;
            // Save state options along with country select id
            this.$state_options = {};
            this.$('select[name=state_id]').each(function() {
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
            return def;
        },
        _onCountryChange: function(ev) {
            var $target = $(ev.target);
            var rs = $target.data('is');
            if(!this.$state_options[rs]) {
                return;
            }
            this.$state_options[rs].detach();
            var selected_country_id = $target.val() || 0;
            var $display_states = this.$state_options[rs].filter('[data-country_id=' + selected_country_id + ']');
            $display_states.appendTo($target.closest('form').find('select[name=state_id]')).show();
            var state_id = $target.closest('form').find('select[name=state_id]').val();
            if(parseInt(state_id) > 0) {
                this._loadDistrictAndTownship(state_id, $target.closest('form'));
            }
        },
        _onStateChange: function(ev) {
            var $target = $(ev.target);
            var $form = $target.closest('form');
            var state_id = $target.val();
            this._loadDistrictAndTownship(state_id, $form);
        },
        _loadDistrict: function(state_id, $form) {
            this._rpc({
                route: '/address_district',
                params: {
                    state_id
                }
            }).then(function(res) {
                var $district = $form.find('select[name=district_id]');
                $district.empty();
                _.map(res, function (d) {
                    $district.append(`<option value="${d.id}">${d.name}</option>`)
                });
            });
        },
        _loadTownship: function(state_id, district_id , $form) {
            this._rpc({
                route: '/address_township',
                params: {
                    state_id,
                    district_id: district_id ? district_id : 0,
                }
            }).then(function(res) {
                var $township = $form.find('select[name=township_id]');
                $township.empty();
                _.map(res, function (d) {
                    $township.append(`<option value="${d.id}">${d.name}</option>`)
                });
            });
        },
        _loadDistrictAndTownship: function(state_id, $form) {
            this._loadDistrict(state_id, $form);
            this._loadTownship(state_id, 0, $form)
        },
        _onDistrictChange: function(ev) {
            var $target = $(ev.target);
            var $form = $target.closest('form');
            var district_id = $target.val();
            this._rpc({
                route: '/address_township',
                params: {
                    district_id
                }
            }).then(function(res) {
                var $township = $form.find('select[name=township_id]');
                $township.empty();
                _.map(res, function (d) {
                    $township.append(`<option value="${d.id}">${d.name}</option>`)
                });
            });
        },
        _createRandomString: function() {
            var r = (Math.random() + 1).toString(36).substring(2);
            return r;
        },
    })

});