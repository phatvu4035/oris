import uuid
from odoo import models, fields, _, api 

class ResUsers(models.Model):
    _inherit = 'res.users'
    
    def _create_user_from_template(self, values):
        values.update({'erp_id': str(uuid.uuid4())})
        return super(ResUsers, self)._create_user_from_template(values)
