odoo.define('theme_oristar.Stiffness', function (require) {
    "use strict";

    var translate_help = require('theme_oristar.translate_help');
    const { Component } = owl;
    const { xml } = owl.tags;

    class Stiffness extends Component {
        static template = 'StiffnessComponent';

        translate_help = translate_help

        constructor() {
            super(...arguments);
        }
        selectStiffness(ev) {
            var elem = $(ev.target);
            var val = elem.val();
            this.trigger('select-stiffness', {value: val});
        }
    }

    return Stiffness;
});