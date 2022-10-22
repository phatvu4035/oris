{
    'name': "oristar_ecommerce_website",
    'name_vi_VN': "oristar_ecommerce_website",

    'summary': """
Ecommerce website for Oristar""",
    'summary_vi_VN': """
    Website bán hàng cho Oristar
""",

    'description': """
This module build up website ecommerce for Oristar
    """,

    'description_vi_VN': """
Xây dựng tính năng trang bán hàng cho Oristar
""",
    'category': 'Uncategorized',
    'version': '0.1.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'website_sale', 'oristar_sale_management', 'contacts'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'data/price_file_data.xml',
        'data/lme_market_data.xml',
        # 'data/lme_prices_data.xml',
        # 'data/pricelist_item_data.xml',
        # 'data/prcelist_data.xml',
        'data/oristar_sample_user.xml',
        'data/config_pricing_data.xml',
        'data/website_data.xml',
        'data/cron.xml',
        'data/signup_notification_template.xml',
        'data/new_order_notification_template.xml',
        'data/product_data.xml',
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
        'views/menus.xml',
        'views/res_config_settings_views.xml',
        'views/res_currency_rate_views.xml',
        'views/res_users_views.xml',
        'views/sale_order_report.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'qweb': ['static/src/xml/*.xml'],
    'images': [
        'static/description/icon.png'
    ],
    'post_init_hook': 'add_product_templates',
    'installable': True,
    'application': False,
    'auto_install': False,
}
