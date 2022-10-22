import werkzeug.exceptions
import werkzeug.routing
import werkzeug.urls

from odoo import models
from odoo.http import request

class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    # @classmethod
    # def _dispatch(cls):
    #     if not request.session.set_lang:
    #         request.session.set_lang = True
    #         return werkzeug.utils.redirect('/vi'+request.httprequest.path, 301)
    #     return super(IrHttp, cls)._dispatch()