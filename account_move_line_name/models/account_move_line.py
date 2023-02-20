# -*- coding: utf-8 -*-
from odoo import models, fields, _

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"
    
    installment_number = fields.Char(string='Installment Number')
    installment_total = fields.Char(string='Installment Total')