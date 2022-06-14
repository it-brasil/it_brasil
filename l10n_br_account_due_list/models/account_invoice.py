# Copyright (C) 2021 - TODAY Renato Lima - Akretion
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, fields, models


class AccountInvoice(models.Model):
    _inherit = "account.move"

    financial_move_line_ids = fields.Many2many(
        comodel_name="account.move.line",
        relation="account_invoice_account_financial_move_line_rel",
        compute="_compute_financial",
        store=True,
        string="Financial Move Lines",
    )

    payment_move_line_ids = fields.Many2many(
        "account.move.line",
        string="Payment Move Lines",
        compute="_compute_payments",
        store=True,
    )

    @api.depends("line_ids", "state")
    def _compute_financial(self):
        for move in self:
            lines = move.line_ids.filtered(
                lambda l: l.account_id.internal_type in ("receivable", "payable")
            )
            move.financial_move_line_ids = lines.sorted()

    @api.depends("line_ids.amount_residual")
    def _compute_payments(self):
        for move in self:
            move.payment_move_line_ids = [
                aml.id
                for partial, amount, aml in move._get_reconciled_invoices_partials()
            ]

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
