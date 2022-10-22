# -*- coding: utf-8 -*-
{
    'name': "Oristar Sale Management",

    'summary': """
        Custom sale module to use customized pricing engine""",

    'description': """
        Custom sale module to allow add more information to SO line 
        and support calculate price for product in SO line
    """,

    'author': "CMC",
    'website': "",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Sales/Sales',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['oristar_pricing', 'sale'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/sale_order_views.xml',
        'views/res_country_state_views.xml',
        'views/customer_credit_limit_views.xml',
        'views/res_partner_views.xml',
        'views/res_company_views.xml',
        'views/res_config_settings_views.xml',
        'views/oristar_warehouse_views.xml',
        'views/inventory_management_views.xml',
        'views/res_district_views.xml',
        'views/res_township_views.xml',
        'views/shipping_method_views.xml',
        'views/product_views.xml',
        'views/assets.xml',
        'views/order_processing_status_views.xml',
        'views/viettelpost_province_views.xml',
        'views/viettelpost_district_views.xml'
    ],
    # only loaded in demonstration mode
    'demo': [],
    'qweb': ['static/src/xml/*.xml'],
    'post_init_hook': 'add_address_book',
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
