from odoo import models, fields, _, api
from odoo.http import request

class IrHttp(models.AbstractModel):
    _inherit =['ir.http']

    @classmethod
    def _get_translation_frontend_modules_name(cls):
        mods = super(IrHttp, cls)._get_translation_frontend_modules_name()
        return mods + ['oristar_ecommerce_website', 'oristar_sale_management']

    @api.model
    def get_frontend_session_info(self):
        session_info = super(IrHttp, self).get_frontend_session_info()
        user_context = request.session.get_context() if request.session.uid else {}
        lang = request.env.lang
        session_info.update({
            'lang': lang,
        })
        return session_info

