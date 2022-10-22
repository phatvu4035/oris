odoo.define('oristar_ecommerce_website.Alloy', function (require) {
    "use strict";

    var translate_help = require('oristar_ecommerce_website.translate_help');
    const { Component } = owl;
    const { xml } = owl.tags;

    class Alloy extends Component {
        static template = 'AlloyComponent';

        translate_help = translate_help;

        constructor() {
            super(...arguments);
        }
        selectAlloy(ev) {
            var elem = $(ev.target);
            var val = elem.val();
            this.trigger('select-alloy', {value: val});
        }
    }

    return Alloy;
});