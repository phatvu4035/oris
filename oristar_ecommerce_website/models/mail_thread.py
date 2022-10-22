from odoo import models

class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'

    def _notify_thread(self, message, msg_vals=False, **kwargs):
        recipients_data = super(MailThread, self)._notify_thread(message, msg_vals=msg_vals, **kwargs)
        self._notify_record_to_inbox_force_from_email(message, recipients_data, msg_vals=msg_vals, **kwargs)
        return recipients_data
    
    def _notify_record_to_inbox_force_from_email(self, message, recipients_data, msg_vals=False, **kwargs):
        partner_to_notify = []
        for partner in recipients_data['partners']:
            if partner['notif'] == 'email':
                partner['notif'] = 'inbox'
                partner_to_notify.append(partner)

        if partner_to_notify:
            recipients_data.update({'partners': partner_to_notify})
            self._notify_record_by_inbox(message, recipients_data, msg_vals=msg_vals, **kwargs)
        return True
