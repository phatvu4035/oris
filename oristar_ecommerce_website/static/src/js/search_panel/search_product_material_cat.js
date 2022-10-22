odoo.define('oristar_ecommerce_website.MaterialCategory', function (require) {
    "use strict";

    var translate_help = require('oristar_ecommerce_website.translate_help');
    const { Component } = owl;
    const { xml } = owl.tags;

    class MaterialCategory extends Component {
        static template = 'MaterialCatComponent';

        translate_help = translate_help

        constructor() {
            super(...arguments);
        }
        selectMaterialCategory(ev) {
            var elem = $(ev.target);
            var val = elem.val();
            this.trigger('select-material-category', {value: val});
        }
    }

    return MaterialCategory;
});