import uuid
from odoo import models, fields, _, api 

class ResUsers(models.Model):
    _inherit = 'res.users'
    
    need_approval = fields.Boolean(string='Need Approve', readonly=True)
    
    def action_approve_user(self):
        self.ensure_one()
        
        self.need_approval = False
        
        template = self.env.ref('oristar_ecommerce_website.mail_template_user_signup_account_approved',
                                    raise_if_not_found=False)
        if template:
            template.sudo().send_mail(self.id, force_send=True)
