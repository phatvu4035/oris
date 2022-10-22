{
    'name': "Oristar Product",

    'summary': """
        Add custom attributes to product""",

    'description': """
        Add following attributes to product:
            + product code
            + material category
            + material
            + basic shape
            + detailed shape
            + alloy
            + stiffness
            + thickness
            + featured product
            + origin
            + surface
            + short description
            + inventory status
    """,

    'author': "CMC",
    'website': "",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Sales/Sales',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['product'],

    # always loaded
    'data': [
        'data/product_material_data.xml',
        'data/product_alloy_data.xml',
        # 'data/product_stiffness_data.xml',
        'data/product_shape_data.xml',
        'data/product_shape_type.xml',
        'data/product_category_data.xml',
        'security/ir.model.access.csv',
        'views/product_basic_shape_views.xml',
        'views/product_detailed_shape_views.xml',
        'views/product_material_category_views.xml',
        'views/product_material_views.xml',
        'views/product_alloy_views.xml',
        'views/product_stiffness_views.xml',
        'views/product_template_views.xml',
        'views/product_shape_type_views.xml'
    ],
    # only loaded in demonstration mode
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
# -*- coding: utf-8 -*-
