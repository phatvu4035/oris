odoo.define('theme_oristar.ProductSearch', function (require) {
    "use strict";

    const {Component} = owl;
    const {xml} = owl.tags;
    const {useRef, useDispatch, useState, useStore} = owl.hooks;
    var ajax = require('web.ajax');

    var translate_help = require('theme_oristar.translate_help');
    var ShapeType = require('theme_oristar.ShapeType');
    var Alloy = require('theme_oristar.Alloy');
    var Material = require('theme_oristar.Material');
    var MaterialCategory = require('theme_oristar.MaterialCategory');
    var Stiffness = require('theme_oristar.Stiffness');
    var Origin = require('theme_oristar.Origin');
    var DetailShape = require('theme_oristar.DetailShape');

    const getSearchFilter = (search_product) => {
        var searchs = {
            material_category: search_product.search_value.material_category,
            material: search_product.search_value.material,
            shape_type: search_product.search_value.shape_type,
            alloy: search_product.search_value.alloy,
            stiffness: search_product.search_value.stiffness,
        }
        ajax.rpc('/get_search_filter_value', searchs).then(function (result) {
            search_product.materials = result.materials;
            search_product.shape_types = result.shape_types;
            search_product.alloys = result.alloys;
            search_product.detail_shapes = result.detail_shapes;
            search_product.stiffness = result.stiffness;
            search_product.origins = result.origins;
        });
    }

    const getMaterialCategory = (search_product) => {
        ajax.rpc('/product_material_category', {}).then(function (result) {
            search_product.material_categories = result;
        });
    }

    const initSearchProduct = () => {
        const search_product = useState({
            shape_types: [],
            alloys: [],
            materials: [],
            material_categories: [],
            stiffness: [],
            origins: [],
            detail_shapes: [],
            search_value: {
                shape_types: false,
                alloy: false,
                material: false,
                material_category: false,
                stiffness: false,
                detail_shape: false,
                origin: false,
            }
        });
        var href = window.location.href;
        const url = new URL(href);
        const searchParams = new URLSearchParams(url.search);
        if (searchParams.get('shape_type')) {
            search_product.search_value.shape_type = parseInt(searchParams.get('shape_type'));
        }
        if (searchParams.get('alloy')) {
            search_product.search_value.alloy = parseInt(searchParams.get('alloy'));
        }
        if(searchParams.get('detail_shape')) {
            search_product.search_value.detail_shape = parseInt(searchParams.get('detail_shape'));
        }
        if (searchParams.get('material')) {
            search_product.search_value.material = parseInt(searchParams.get('material'));
        }
        if (searchParams.get('material_category')) {
            search_product.search_value.material_category = parseInt(searchParams.get('material_category'));
        }
        if (searchParams.get('stiffness')) {
            search_product.search_value.stiffness = parseInt(searchParams.get('stiffness'));
        }
        if (searchParams.get('origin')) {
            search_product.search_value.origin = parseInt(searchParams.get('origin'));
        }
        return search_product;
    }
    const getRightTemplate = () => {
        var pathname = window.location.pathname;
        // Get current lang from path name
        var langcode_list = ['vi', 'en']
        var current_lang_search = langcode_list.indexOf(pathname.split('/')[1]);
        var lang_segment = current_lang_search >= 0 ? '/' + pathname.split('/')[1] : '';
        pathname = lang_segment ? pathname.replace(lang_segment, '') : pathname;
        if(pathname.startsWith('/shop')) {
            return 'ProductSearchTemp0'
        } else {
            return 'ProductSearchTemp1'
        }
    }
    getRightTemplate();
    class ProductSearch extends Component {
        static template = getRightTemplate();

        static components = {ShapeType, Alloy, Material, MaterialCategory, Stiffness, Origin, DetailShape}

        translate_help = translate_help;

        search_product = initSearchProduct();

        onSearch(ev) {
            var $target = $(ev.target);
            $target.closest('form').find('search-btn').click();
        }

        _onSelectOrigin2(ev) {
            $('#auto-product-filter').submit();
        }

        _onSelectStiffness(ev) {
            var stiffness = ev.detail.value;
            this.search_product.search_value.stiffness = parseInt(stiffness);
        }
        _onSelectStiffnes2s(ev) {
            $('#auto-product-filter').submit();
        }

        _onSelectDetailShape2(ev) {
            $('#auto-product-filter').submit();
        }

        _onSelectAlloy(ev) {
            var alloy = ev.detail.value;
            this.search_product.search_value.alloy = parseInt(alloy);
            getSearchFilter(this.search_product);
        }
        _onSelectAlloy2(ev) {
            $('#auto-product-filter').submit();
        }
        _onSelectStiffness2(ev) {
            $('#auto-product-filter').submit();
        }

        _onSelectShapeType(ev) {
            var shape_type = ev.detail.value;
            this.search_product.search_value.shape_type = parseInt(shape_type);
            this.search_product.search_value.detail_shape = false;
        }
        _onSelectShapeType2(ev) {
            $('#auto-product-filter').submit();
        }

        _onSelectMaterial(ev) {
            var material = ev.detail.value
            this.search_product.search_value.material = parseInt(material);
            this.search_product.search_value.stiffness = false;
            this.search_product.search_value.alloy = false;
            getSearchFilter(this.search_product);
        }
        _onSelectMaterial2(ev) {
            $('#auto-product-filter').submit();
        }

        _onSelectMaterialCategory(ev) {
            var material_category = ev.detail.value
            this.search_product.search_value.material_category = parseInt(material_category);
            this.search_product.search_value.material = false;
            getSearchFilter(this.search_product);
        }
        _onSelectMaterialCategory2(ev) {
            $('#auto-product-filter').submit();
        }

        mounted() {
            var self = this
            getMaterialCategory(this.search_product);
            setTimeout(function () {
                getSearchFilter(self.search_product)
            }, 200);
        }
    }

    return ProductSearch;
});
