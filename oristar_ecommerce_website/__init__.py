# -*- coding: utf-8 -*-

from . import controllers
from . import models
from odoo import api, fields, tools

def add_product_templates(cr, registry):
    tools.convert_file(cr, 'oristar_ecommerce_website', 'data/product.template.csv',
                       None, mode='init', noupdate=True, kind='init')