odoo.define('oristar_sale_management.CashManager', function (require) {
    const core = require('web.core');
    const CrashManager = require('web.CrashManager').CrashManager;

    const _lt = core._lt;

    CrashManager.include({
        init: function () {
            this._super.apply(this, arguments);
            Object.assign(this.odooExceptionTitleMap, {
                'odoo.addons.oristar_sale_management.models.sale_order.OutOfServiceException': _lt('Out of Service')
            });
        }
    })
})