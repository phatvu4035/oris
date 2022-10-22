odoo.define('oristar_ecommerce_website.ShapeType', function (require) {
    "use strict";

    var translate_help = require('oristar_ecommerce_website.translate_help');
    const { Component } = owl;
    const { xml } = owl.tags;
    const { useState, useStore, onMounted } = owl.hooks;


    class ShapeType extends Component {
        static template = 'ShapeTypeComponent';
        translate_help = translate_help
        constructor() {
            super(...arguments);
        }
        selectShapeType(ev) {
            var elem = $(ev.target);
            var val = elem.val();
            this.trigger('select-shape-type', {value: val});
        }
    }

    return ShapeType;
});