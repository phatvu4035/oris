# -*- coding: utf-8 -*-
{
    'name': "Oristar Theme",

    'summary': """
       Theme, Layout, Snippets for website Oristar""",

    'description': """
        Theme for website Oristar
    """,

    'author': "Oristar",
    'website': "http://www.oristar.vn",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Theme/Corporate',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        'views/views.xml',
        'views/assets.xml',
        'views/website_template.xml',
        'views/homepage.xml',
        'views/contact.xml',
        'views/login.xml',
        'views/reset_password.xml',
        'views/select_account_type.xml',
        'views/signup.xml',
        'views/cart.xml',
        'views/my_account.xml',
        'views/orders.xml',
        'views/address_book.xml',
        'views/templates.xml',
        'views/footer.xml',
    ],
}
