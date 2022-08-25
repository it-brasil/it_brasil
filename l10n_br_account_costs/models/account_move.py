# Copyright (C) 2009  Renato Lima - Akretion
# Copyright (C) 2012  Raphaël Valyi - Akretion
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from functools import partial

from odoo import api, fields, models
from odoo.tools import float_is_zero
from odoo.tools.misc import formatLang
from collections import defaultdict

from ...l10n_br_fiscal.constants.fiscal import (
    CFOP_DESTINATION_EXPORT,
    FISCAL_IN
)


class AccountMove(models.Model):
    _inherit = "account.move"

    amount_freight_value = fields.Monetary(
        compute="_compute_freight_value",
        inverse="_inverse_amount_freight",
    )

    amount_insurance_value = fields.Monetary(
        compute="_compute_insurance_value",
        inverse="_inverse_amount_insurance",
    )

    amount_other_value = fields.Monetary(
        compute="_compute_other_value",
        inverse="_inverse_amount_other",
    )

    # Usado para tornar Somente Leitura os campos totais dos custos
    # de entrega quando a definição for por Linha
    delivery_costs = fields.Selection(
        related="company_id.delivery_costs",
    )

    @api.depends("amount_freight_value")
    def _compute_freight_value(self):
        total_freight = 0.0
        for record in self.invoice_line_ids:
            total_freight += record.freight_value
        self.amount_freight_value = total_freight

    @api.depends("amount_insurance_value")
    def _compute_insurance_value(self):
        total_insurance = 0.0
        for record in self.invoice_line_ids:
            total_insurance += record.insurance_value
        self.amount_insurance_value = total_insurance

    @api.depends("amount_other_value")
    def _compute_other_value(self):
        total_other = 0.0
        for record in self.invoice_line_ids:
            total_other += record.other_value
        self.amount_other_value = total_other

    def _inverse_amount_freight(self):
        for record in self.filtered(lambda inv: inv.invoice_line_ids):
            if record.company_id.delivery_costs == "total":
                amount_freight_value = record.amount_freight_value
                if all(record.invoice_line_ids.mapped("freight_value")):
                    amount_freight_old = sum(record.invoice_line_ids.mapped("freight_value"))
                    for line in record.invoice_line_ids[:-1]:
                        line.freight_value = amount_freight_value * (
                            line.freight_value / amount_freight_old
                        )
                    record.invoice_line_ids[-1].freight_value = amount_freight_value - sum(
                        line.freight_value for line in record.invoice_line_ids[:-1]
                    )
                else:
                    amount_total = sum(record.invoice_line_ids.mapped("price_total"))
                    for line in record.invoice_line_ids[:-1]:
                        line.freight_value = amount_freight_value * (
                            line.price_total / amount_total
                        )
                    record.invoice_line_ids[-1].freight_value = amount_freight_value - sum(
                        line.freight_value for line in record.invoice_line_ids[:-1]
                    )
                for line in record.invoice_line_ids:
                    price_subtotal = line._get_price_total_and_subtotal()
                    line.price_subtotal = price_subtotal['price_subtotal']
                    line.update(line._get_fields_onchange_subtotal())
                    line._onchange_fiscal_taxes()
                record._recompute_dynamic_lines(recompute_all_taxes=True)
                record._fields["amount_total"].compute_value(record)

                record.write(
                    {
                        name: value
                        for name, value in record._cache.items()
                        if record._fields[name].compute == "_compute_amount"
                        and not record._fields[name].inverse
                    }
                )

    def _inverse_amount_insurance(self):
        for record in self.filtered(lambda inv: inv.invoice_line_ids):
            if record.company_id.delivery_costs == "total":
                amount_insurance_value = record.amount_insurance_value
                if all(record.invoice_line_ids.mapped("insurance_value")):
                    amount_insurance_old = sum(
                        record.invoice_line_ids.mapped("insurance_value")
                    )
                    for line in record.invoice_line_ids[:-1]:
                        line.insurance_value = amount_insurance_value * (
                            line.insurance_value / amount_insurance_old
                        )
                    record.invoice_line_ids[
                        -1
                    ].insurance_value = amount_insurance_value - sum(
                        line.insurance_value for line in record.invoice_line_ids[:-1]
                    )
                else:
                    amount_total = sum(record.invoice_line_ids.mapped("price_total"))
                    for line in record.invoice_line_ids[:-1]:
                        line.insurance_value = amount_insurance_value * (
                            line.price_total / amount_total
                        )
                    record.invoice_line_ids[
                        -1
                    ].insurance_value = amount_insurance_value - sum(
                        line.insurance_value for line in record.invoice_line_ids[:-1]
                    )

                for line in record.invoice_line_ids:
                    price_subtotal = line._get_price_total_and_subtotal()
                    line.price_subtotal = price_subtotal['price_subtotal']
                    line.update(line._get_fields_onchange_subtotal())
                    line._onchange_fiscal_taxes()
                record._recompute_dynamic_lines(recompute_all_taxes=True)

                record._fields["amount_total"].compute_value(record)
                record.write(
                    {
                        name: value
                        for name, value in record._cache.items()
                        if record._fields[name].compute == "_amount_all"
                        and not record._fields[name].inverse
                    }
                )

    def _inverse_amount_other(self):
        for record in self.filtered(lambda inv: inv.invoice_line_ids):
            if record.company_id.delivery_costs == "total":
                amount_other_value = record.amount_other_value
                if all(record.invoice_line_ids.mapped("other_value")):
                    amount_other_old = sum(record.invoice_line_ids.mapped("other_value"))
                    for line in record.invoice_line_ids[:-1]:
                        line.other_value = amount_other_value * (
                            line.other_value / amount_other_old
                        )
                    record.invoice_line_ids[-1].other_value = amount_other_value - sum(
                        line.other_value for line in record.invoice_line_ids[:-1]
                    )
                else:
                    amount_total = sum(record.invoice_line_ids.mapped("price_total"))
                    for line in record.invoice_line_ids[:-1]:
                        line.other_value = amount_other_value * (
                            line.price_total / amount_total
                        )
                    record.invoice_line_ids[-1].other_value = amount_other_value - sum(
                        line.other_value for line in record.invoice_line_ids[:-1]
                    )

                for line in record.invoice_line_ids:
                    price_subtotal = line._get_price_total_and_subtotal()
                    line.price_subtotal = price_subtotal['price_subtotal']
                    line.update(line._get_fields_onchange_subtotal())
                    line._onchange_fiscal_taxes()
                record._recompute_dynamic_lines(recompute_all_taxes=True)
                record._fields["amount_total"].compute_value(record)
                record.write(
                    {
                        name: value
                        for name, value in record._cache.items()
                        if record._fields[name].compute == "_amount_all"
                        and not record._fields[name].inverse
                    }
                )

    # @api.depends(
    #     'line_ids.matched_debit_ids.debit_move_id.move_id.payment_id.is_matched',
    #     'line_ids.matched_debit_ids.debit_move_id.move_id.line_ids.amount_residual',
    #     'line_ids.matched_debit_ids.debit_move_id.move_id.line_ids.amount_residual_currency',
    #     'line_ids.matched_credit_ids.credit_move_id.move_id.payment_id.is_matched',
    #     'line_ids.matched_credit_ids.credit_move_id.move_id.line_ids.amount_residual',
    #     'line_ids.matched_credit_ids.credit_move_id.move_id.line_ids.amount_residual_currency',
    #     'line_ids.debit',
    #     'line_ids.credit',
    #     'line_ids.currency_id',
    #     'line_ids.amount_currency',
    #     'line_ids.amount_residual',
    #     'line_ids.amount_residual_currency',
    #     'line_ids.payment_id.state',
    #     'line_ids.full_reconcile_id')
    # def _compute_amount(self):
    #     total_tax = 0.0
    #     # coloquei o len abaixo pq tem hora q traz todas as faturas do sistema
    #     # import pudb;pu.db
    #     if len(self) == 1:
    #         for move in self:
    #             for line in move.line_ids.filtered(lambda l: l.tax_line_id):
    #                 # Create Wh Invoice only for supplier invoice
    #                 # if line.move_id and line.move_id.type != "in_invoice":
    #                 #     continue
                    
    #                 account_tax_group = line.tax_line_id.tax_group_id
    #                 if account_tax_group and account_tax_group.fiscal_tax_group_id:
    #                     fiscal_group = account_tax_group.fiscal_tax_group_id
    #                     if fiscal_group.tax_withholding:
    #                         invoice = self.env["account.move"].create(
    #                             self._prepare_wh_invoice(line, fiscal_group)
    #                         )

    #                         self.env["account.move.line"].create(
    #                             self._prepare_wh_invoice_line(invoice, line)
    #                         )


    #         # total do ICMS
    #         for line in self.line_ids:
    #             line._onchange_fiscal_taxes()
    #         #     if line.purchase_line_id:
    #         #         continue
    #         #     if (
    #         #         line.cfop_id
    #         #         and line.cfop_id.destination == CFOP_DESTINATION_EXPORT
    #         #         and line.fiscal_operation_id.fiscal_operation_type == FISCAL_IN
    #         #     ):
    #         #         total_tax += line.icms_value
    #         # dif = 0.0
    #         # total = 0.0
    #         # # Corrige a conta de ICMS Importacao
    #         # for line in self.line_ids:
    #         #     if line.purchase_line_id:
    #         #         continue
    #         #     if (
    #         #         line.name and 'ICMS Entrada Importa' in line.name 
    #         #         and total_tax
    #         #         and not self.purchase_id
    #         #     ):
    #         #         dif = total_tax - line.debit
    #         #         line.debit = total_tax
    #         #     if (
    #         #         line.account_id and dif
    #         #         and 'Fornecedor' in line.account_id.name
    #         #     ):
    #         #         line.credit = line.credit + dif
    #         #         # menos pq o amount currency e negativo
    #         #         line.amount_currency = line.amount_currency - dif
    #         #         total += line.amount_currency + total_tax
    #             line._update_taxes()
    #     super()._compute_amount()

    # @api.model
    # def _compute_taxes_mapped(self, base_line):
    #     import pudb;pu.db
    #     super()._compute_taxes_mapped(base_line)