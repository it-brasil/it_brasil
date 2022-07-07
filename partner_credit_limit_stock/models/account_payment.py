# -*- coding: utf-8 -*-

from odoo import fields, models, _


class AccountPaymentTerm(models.Model):
    _inherit = 'account.payment.term'

    allow_sales_order = fields.Boolean(
        string="Permitir pedido de venda?",
        help="Ao ativar essa opção, caso o cliente esteja inadimplente, essa condição de pagamento poderá ser utilizada por algum usuário com permissão Gerente de Limite de Crédito",
        tracking=True,
    )
