# Copyright (C) 2020  Magno Costa - Akretion
# Copyright (C) 2020  Renato Lima - Akretion
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, models


class AccountMove(models.Model):
    _inherit = "account.move"

    # @api.onchange("purchase_vendor_bill_id", "purchase_id")
    # def _onchange_purchase_auto_complete(self):
    #     if self.purchase_id:
    #         self.fiscal_operation_id = self.purchase_id.fiscal_operation_id
    #         if not self.document_type_id:
    #             self.document_type_id = self.company_id.document_type_id
    #     return super()._onchange_purchase_auto_complete()

    # @api.onchange("fiscal_operation_id")
    # def _onchange_fiscal_operation_id(self):
    #     res = {}
    #     lines_without_product = []
    #     invoice_lines = self.invoice_line_ids.filtered(lambda l: not l.display_type)
    #     for line in invoice_lines:
    #         if line.product_id:
    #             line.account_id = line._get_computed_account()
    #             taxes = line._get_computed_taxes()
    #             # if taxes and line.move_id.fiscal_position_id:
    #             #     taxes = line.move_id.fiscal_position_id.map_tax(
    #             #         taxes, partner=line.partner_id
    #             #     )
    #             line._onchange_fiscal_tax_ids()
    #             # line.tax_ids = taxes
    #             line._onchange_price_subtotal()
    #             line._onchange_mark_recompute_taxes()
    #         else:
    #             lines_without_product.append(line.name)
    #     self._onchange_invoice_line_ids()
    #     return res
