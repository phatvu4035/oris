odoo.define('oristar_ecommerce_website.Material', function (require) {
    "use strict";

    var translate_help = require('oristar_ecommerce_website.translate_help');
    const { Component } = owl;
    const { xml } = owl.tags;

    class Material extends Component {
        static template = 'MaterialComponent';

        translate_help = translate_help

        constructor() {
            super(...arguments);
        }
        selectMaterial(ev) {
            var elem = $(ev.target);
            var val = elem.val();
            this.trigger('select-material', {value: val});
        }
    }

    return Material;
});