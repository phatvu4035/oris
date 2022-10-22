odoo.define('theme_oristar.DetailShape', function (require) {
    "use strict";

    var translate_help = require('theme_oristar.translate_help');
    const { Component } = owl;
    const { xml } = owl.tags;

    class DetailShape extends Component {
        static template ='DetailShapeComponent';

        translate_help = translate_help

        constructor() {
            super(...arguments);
        }
        selectDetailShape(ev) {
            var elem = $(ev.target);
            var val = elem.val();
            this.trigger('select-detail-shape', {value: val});
        }
    }

    return DetailShape;
});