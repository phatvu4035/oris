odoo.define('theme_oristar.main', function (require) {
    "use strict";

    const { Component, Store, mount, router, QWeb } = owl;
    const { whenReady } = owl.utils;
    const { useRef, useDispatch, useState, useStore } = owl.hooks;
    const ProductSearch = require('theme_oristar.ProductSearch');
    var publicWidget = require('web.public.widget');

    const actions = {};

    const initialState = {};

    const ROUTES = [];

    // bad
    $(document).ready(function () {
        if ($('.oe_login_form').length > 0) {
            $('.oe_login_form').closest('.logins').addClass('logins-2');
        }
        $('.o_portal_docs a[href="/my/quotes"]').remove();
        $('.o_portal_docs a[href="/my/invoices"]').remove();
    });

    function makeStore() {
        const state = initialState;
        const store = new Store({ state, actions });
        return store;
    }

    async function setup() {
        owl.config.mode = "dev";
        var templates = await owl.utils.loadFile('/theme_oristar/static/src/xml/search_product_components.xml');
        const env = { qweb: new owl.QWeb({ templates }) };
        env.router = new router.Router(env, ROUTES, { mode: "history" });
        owl.Component.env = env;
        await env.router.start();
        if(document.getElementById('homepage_product_category_filter')) {
            mount(ProductSearch, {target: document.getElementById('homepage_product_category_filter')})
        }
    }
    whenReady(setup)
})
