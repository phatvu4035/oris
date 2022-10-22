from odoo import models, fields, _, api

class OrderProcessingStatus(models.Model):
    _name = 'order.processing.status'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'ERP Order Processing Status'
    
    erp_id = fields.Char(string='ERP ID')
    status_code = fields.Integer(string='Status Code')
    status_name = fields.Char(string='Status Name')
    updated_time = fields.Datetime(string='Updated Time')
