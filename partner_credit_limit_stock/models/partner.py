# See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    credit_limit = fields.Float(
        string='Limite de Crédito',
        default=0.0,
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
        string = 'Tem limite de crédito?'
    )

    def _check_limit(self):
        self.ensure_one()
        confirmed_sale_orders = self.env['sale.order'].sudo().search([
            ('partner_id', '=', self.id),
            ('state', 'in', ['sale','done']),
            ('invoice_status', '!=', 'invoiced')
        ])
        invoice_lines = self.env['account.move.line'].sudo().search([
            ('partner_id', '=', self.id),
            ('account_id.user_type_id.type', 'in',['receivable', 'payable']),
            ('parent_state','!=','cancel')
        ])
        amount_sales, debit, credit = 0.0, 0.0, 0.0
        if confirmed_sale_orders:
            for sale in confirmed_sale_orders:
                amount_sales += sale.amount_total
        if invoice_lines:
            for line in invoice_lines:
                credit += line.credit
                debit += line.debit
        partner_credit_limit = (debit + amount_sales) - credit
        available_credit_limit = self.credit_limit - partner_credit_limit
        if available_credit_limit < 0: 
            for partner in self:
                partner.credit_rest = 0
                partner.credit_negative_margin = available_credit_limit
            return 0
        else:
            for partner in self:
                partner.credit_rest = available_credit_limit
                partner.credit_negative_margin = 0
            return available_credit_limit



    # def _check_limit(self):
    #     self.ensure_one()
    #     moveline_obj = self.env['account.move.line']
    #     movelines = moveline_obj.search(
    #         [('partner_id', '=', self.id),
    #          ('account_id.user_type_id.name', 'in',
    #             ['Receivable', 'Payable']),
    #          ('parent_state','!=','cancel')]
    #     )
    #     # TODO verificar se o pedido atual esta entrando aqui...
    #     confirm_sale_order = self.env['sale.order'].search(
    #         [('partner_id', '=', self.id),
    #            ('state', '=', 'sale'),
    #            ('invoice_status', '!=', 'invoiced')])
    #     debit, credit = 0.0, 0.0
    #     amount_total = 0.0
    #     for status in confirm_sale_order:
    #         amount_total += status.amount_total
    #     #print ('total vendas faturado: %s' %(str(amount_total)))
    #     x = 0.0
    #     for line in movelines:
    #         credit += line.credit
    #         debit += line.debit
    #         x += debit - credit
    #     #print ('total faturado: %s' %(str(x)))
    #     partner_credit_limit = (
    #         debit + amount_total) - credit
    #     available_credit_limit = round(
    #         self.credit_limit - partner_credit_limit, 2)
    #     for prt in self:
    #         prt.credit_rest = available_credit_limit
    #     return prt.credit_rest
