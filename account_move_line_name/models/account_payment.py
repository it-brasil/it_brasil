# -*- coding: utf-8 -*-

from odoo import api, models, fields, _
from datetime import date

class AccountPayment(models.Model):
    _inherit = 'account.payment'


    def _prepare_move_line_default_vals(self, write_off_line_vals=None):

        # VER SE ADICIONA AQUI PRA SAIR A CONTA TBEM NO CAMPO NAME
        # QUANDO E JUROS NAO ESTA SAINDO NADA

        line_vals_list = super()._prepare_move_line_default_vals(write_off_line_vals)
        for vals in line_vals_list:
            if (self.ref 
                and "name" in vals
                and self.ref not in vals["name"]):
                vals["name"] = self.ref + ' ' + vals["name"]
                if vals["name"] == self.ref:
                    vals["name"] = self.ref + ' ' + self.account_id.name
        return line_vals_list