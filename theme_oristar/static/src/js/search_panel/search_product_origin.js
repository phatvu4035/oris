odoo.define('theme_oristar.Origin', function (require) {
    "use strict";

    var translate_help = require('theme_oristar.translate_help');
    const { Component } = owl;
    const { xml } = owl.tags;

    class Origin extends Component {
        static template = 'OriginComponent';

        translate_help = translate_help

        constructor() {
            super(...arguments);
        }
        selectOrigin(ev) {
            var elem = $(ev.target);
            var val = elem.val();
            this.trigger('select-origin', {value: val});
        }
    }

    return Origin;
});