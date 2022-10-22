from odoo import models, fields

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    price_service_url = fields.Char(string='Price Service URL', related='company_id.price_service_url', readonly=False)
    price_method_folder = fields.Char(string='Price Method Folder', related='company_id.price_method_folder', readonly=False)
    quotation_file = fields.Binary(string='Quotation File', related='company_id.quotation_file', readonly=False)
    tolerance_standard_table = fields.Char(string='Tolerance Standard Table Link', related='company_id.tolerance_standard_table', readonly=False)
    milling_min_limit = fields.Float(string='Min Limit For Milling', related='company_id.milling_min_limit', readonly=False, default=40)
    milling_max_limit = fields.Float(string='Max Limit For Milling', related='company_id.milling_max_limit', readonly=False, default=800)
    sale_notification_reception_partner_ids = fields.Many2many('res.partner', string='Notification Reception Partners', 
                                                               related='company_id.sale_notification_reception_partner_ids', readonly=False)
    working_time_delay_confirmation = fields.Float(string='Working-Time Delay Confirmation', 
                                                   related='company_id.working_time_delay_confirmation', readonly=False)
    offtime_delay_confirmation = fields.Float(string='Off-Time Delay Confirmation',
                                              related='company_id.offtime_delay_confirmation', readonly=False)
    viettelpost_api_url = fields.Char(string='Viettel Post API URL', related='company_id.viettelpost_api_url', readonly=False)
    viettelpost_user_name = fields.Char(string='Viettel Post API UserName', related='company_id.viettelpost_user_name', readonly=False)
    viettelpost_password = fields.Char(string='Viettel Post API Password', related='company_id.viettelpost_password', readonly=False)
