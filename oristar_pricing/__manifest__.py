# -*- coding: utf-8 -*-
{
    'name': "Oristar Pricing",

    'summary': """
        Custom pricelist and add LME price management""",

    'description': """
        Custom pricelist to allow upload excel file of price calculation for each price rule
        Add LME model to manage LME price
        Add profit margin (TSLN) into pricelist
    """,

    'author': "CMC",
    'website': "",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Sales/Sales',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['oristar_product'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/product_pricelist_views.xml',
        'views/lme_price_views.xml',
        'views/lme_market_views.xml',
        'views/price_file_views.xml',
        'views/lme_spot_price_views.xml',
        'views/profit_margin_range_views.xml'
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
