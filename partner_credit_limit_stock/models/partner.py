# See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    credit_limit = fields.Float(
        string='Limite de Crédito',
        default=0.0,
        tracking = True,
    )
    credit_rest = fields.Float(
        string='Valor Disponível', #antigo valor faturado
        readonly=True,
        compute='_check_limit',
    )
    credit_negative_margin = fields.Float(
        string='Margem Negativa', #antigo valor faturado
        readonly=True,
        compute='_check_limit',
    )

    enable_credit_limit = fields.Boolean(
        string = 'Tem limite de crédito?',
        tracking = True,
    )

    def _check_limit(self):
        vendas = self.env['sale.order'].search([
            ('partner_id','=', self.id),
            ('state', 'in', ['sale','done'])], 
            order='id desc'
        )
        #faturas = self.env['account.move'].search([
        #    ('partner_id', '=', self.id),
        #    ('state','!=','cancel')
        #])
        if self.enable_credit_limit and vendas: # (vendas or faturas): 
            vendas[0].limite_credito()
        else: 
            self.credit_rest = self.credit_limit
            self.credit_negative_margin = 0.0

