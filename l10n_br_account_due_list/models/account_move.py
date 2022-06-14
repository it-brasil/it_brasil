# Copyright (C) 2021 - TODAY Renato Lima - Akretion
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, fields, models


class AccountInvoice(models.Model):
    _inherit = "account.move"

    financial_move_line_ids = fields.One2many(
        comodel_name="account.move.line",
        inverse_name="move_id",
        string="Financial Move Lines",
        readonly=True,
        domain="[('account_id.user_type_id.type', 'in', ('receivable', 'payable'))]",
    )

    payment_move_line_ids = fields.Many2many(
        comodel_name="account.move.line",
        relation="account_invoice_account_payment_move_line_rel",
        string="Payment Move Lines",
        compute="_compute_payments",
        store=True,
    )

    @api.depends("line_ids.amount_residual")
    def _compute_payments(self):
        for move in self.filtered(lambda m: not m.payment_state == "not_paid"):
            amls = [
                aml.id
                for partial, amount, aml in move._get_reconciled_invoices_partials()
            ]
            move.payment_move_line_ids = amls
            
    def _get_reconciled_invoices_partials(self):
        ''' Helper to retrieve the details about reconciled invoices.
        :return A list of tuple (partial, amount, invoice_line).
        '''
        self.ensure_one()
        pay_term_lines = self.line_ids\
            .filtered(lambda line: line.account_internal_type in ('receivable', 'payable'))
        invoice_partials = []
        # ALTEREI ABAIXO PRA CARREGAR NA TELA DA FATURA O TOTAL RECEBIDO OU PAGO
        for partial in pay_term_lines.matched_debit_ids:
            # invoice_partials.append((partial, partial.credit_amount_currency, partial.debit_move_id))
            for line in partial.debit_move_id.move_id.line_ids:
                if not line.account_internal_type in ('receivable', 'payable'):
                    invoice_partials.append((partial, line.amount_currency, line))
        for partial in pay_term_lines.matched_credit_ids:
            # invoice_partials.append((partial, partial.debit_amount_currency, partial.credit_move_id))
            for line in partial.credit_move_id.move_id.line_ids:
                if not line.account_internal_type in ('receivable', 'payable'):
                    invoice_partials.append((partial, line.amount_currency, line))
        return invoice_partials