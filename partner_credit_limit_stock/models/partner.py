# See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    credit_limit = fields.Float(
        string='Limite crédito',
        default=0.0,
    )
    credit_rest = fields.Float(
        string='Valor Faturado',
        readonly=True,
        compute='_check_limit',
    )


    def _check_limit(self):
        self.ensure_one()
        moveline_obj = self.env['account.move.line']
        movelines = moveline_obj.search(
            [('partner_id', '=', self.id),
             ('account_id.user_type_id.name', 'in',
                ['Receivable', 'Payable']),
             ('parent_state','!=','cancel')]
        )
        # TODO verificar se o pedido atual esta entrando aqui...
        confirm_sale_order = self.env['sale.order'].search(
            [('partner_id', '=', self.id),
               ('state', '=', 'sale'),
               ('invoice_status', '!=', 'invoiced')])
        debit, credit = 0.0, 0.0
        amount_total = 0.0
        for status in confirm_sale_order:
            amount_total += status.amount_total
        print ('total vendas faturado: %s' %(str(amount_total)))
        x = 0.0
        for line in movelines:
            credit += line.credit
            debit += line.debit
            x += debit - credit
        print ('total faturado: %s' %(str(x)))
        partner_credit_limit = (
            debit + amount_total) - credit
        available_credit_limit = round(
            self.credit_limit - partner_credit_limit, 2)
        for prt in self:
            prt.credit_rest = available_credit_limit
        return prt.credit_rest
