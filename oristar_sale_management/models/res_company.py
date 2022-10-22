from odoo import models, fields, api, _

class ResCompany(models.Model):
    _inherit = 'res.company'

    price_service_url = fields.Char(string='Price Service URL')
    price_method_folder = fields.Char(string='Price Method Folder')
    quotation_file = fields.Binary(string='Quotation File', attachment=True)
    tolerance_standard_table = fields.Char(string='Tolerance Standard Table Link', placeholder="",
                                           help="Paste the link here\n"
                                           "Ex: https://drive.google.com/file/d/1BaBe7VwHgp3H5tYQt7y4H9IA7fkQ7de9/view",
                                           attachment=True)
    milling_min_limit = fields.Float(string='Min Limit For Milling')
    milling_max_limit = fields.Float(string='Max Limit For Milling')
    sale_notification_reception_partner_ids = fields.Many2many('res.partner', string='Notification Reception Partners')
    working_time_delay_confirmation = fields.Float(string='Working-Time Delay Confirmation')
    offtime_delay_confirmation = fields.Float(string='Off-Time Delay Confirmation')
    viettelpost_api_url = fields.Char(string='Viettel Post API URL')
    viettelpost_user_name = fields.Char(string='Viettel Post API UserName')
    viettelpost_password = fields.Char(string='Viettel Post API Password')
