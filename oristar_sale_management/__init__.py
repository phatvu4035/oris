# -*- coding: utf-8 -*-

from . import controllers
from . import models
from odoo import api, fields, tools

def add_address_book(cr, registry):
    tools.convert_file(cr, 'oristar_sale_management', 'data/res.country.state.csv',
                       None, mode='init', noupdate=True, kind='init')
    tools.convert_file(cr, 'oristar_sale_management', 'data/res.district.csv',
                       None, mode='init', noupdate=True, kind='init')
    tools.convert_file(cr, 'oristar_sale_management', 'data/res.country.state.csv',
                       None, mode='init', noupdate=True, kind='init')
    tools.convert_file(cr, 'oristar_sale_management', 'data/res.township.csv',
                       None, mode='init', noupdate=True, kind='init')