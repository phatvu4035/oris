odoo.define('theme_oristar.Alloy', function (require) {
    "use strict";

    var translate_help = require('theme_oristar.translate_help');
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