from odoo import _, api, fields, models
from odoo.exceptions import UserError

from ...l10n_br_fiscal.constants.fiscal import (
    CFOP_DESTINATION_EXPORT,
    FISCAL_IN
)


class AccountMoveLine(models.Model):
    _name = "account.move.line"
    _inherit = [_name, "l10n_br_fiscal.document.line.mixin.methods"]
    _inherits = {"l10n_br_fiscal.document.line": "fiscal_document_line_id"}

    @api.model
    def _get_price_total_and_subtotal_model(self, price_unit, quantity, discount, currency, product, partner, taxes, move_type):
        # self._update_taxes()
        res = super()._get_price_total_and_subtotal_model(price_unit, quantity, discount, currency, product, partner, taxes, move_type)
        line_discount_price_unit = price_unit * (1 - (discount / 100.0))
        subtotal = quantity * line_discount_price_unit
        subtotal = subtotal + self.freight_value + self.insurance_value + self.other_value
        # # self._compute_amounts()
        # # Compute 'price_total'.
        # # import pudb;pu.db
        # # if taxes:
        # #     taxes_res = taxes._origin.with_context(force_sign=1).compute_all(line_discount_price_unit,
        # #         quantity=quantity, currency=currency, product=product, partner=partner, is_refund=move_type in ('out_refund', 'in_refund'))
        # #     res['price_subtotal'] = taxes_res['total_excluded']
        # #     #  self.freight_value + self.insurance_value + self.other_value
        # #     res['price_total'] = taxes_res['total_included']
        # else:
        res['price_total'] = res['price_subtotal'] = subtotal
        # # self.amount_total = res['price_subtotal'] + self.amount_tax
        # self.amount_residual = subtotal
        #In case of multi currency, round before it's use for computing debit credit
        if currency:
            res = {k: currency.round(v) for k, v in res.items()}

        return res

        # import pudb;pu.db
        # res = super()._get_price_total_and_subtotal_model(price_unit, quantity, discount, currency, product, partner, taxes, move_type)
        # line_discount_price_unit = price_unit * (1 - (discount / 100.0))
        # subtotal = quantity * line_discount_price_unit

        # # Compute 'price_total'.
        # if taxes:
        #     taxes_res = taxes._origin.with_context(force_sign=1).compute_all(line_discount_price_unit,
        #         quantity=quantity, currency=currency, product=product, partner=partner, is_refund=move_type in ('out_refund', 'in_refund'))
        #     res['price_subtotal'] = taxes_res['total_excluded'] + self.freight_value + self.insurance_value + self.other_value
        #     res['price_total'] = taxes_res['total_included'] + self.freight_value + self.insurance_value + self.other_value
        # else:
        #     res['price_total'] = subtotal + self.freight_value + self.insurance_value + self.other_value
    
        # return res

    # @api.depends(
    #     "fiscal_price",
    #     "discount_value",
    #     "insurance_value",
    #     "other_value",
    #     "freight_value",
    #     "fiscal_quantity",
    #     "amount_tax_not_included",
    #     "uot_id",
    #     "product_id",
    #     "partner_id",
    #     "company_id",
    # )
    # def _compute_amounts(self):
    #     super._compute_amounts()
    #     for record in self:
    #         import pudb;pu.db
    #         round_curr = record.currency_id or self.env.ref("base.BRL")
    #         # Valor dos produtos
    #         record.price_gross = round_curr.round(record.price_unit * record.quantity)

    #         record.amount_untaxed = record.price_gross - record.discount_value

    #         record.amount_fiscal = (
    #             round_curr.round(record.fiscal_price * record.fiscal_quantity)
    #             - record.discount_value
    #         )

    #         record.amount_tax = record.amount_tax_not_included

    #         add_to_amount = sum([record[a] for a in record._add_fields_to_amount()])
    #         rm_to_amount = sum([record[r] for r in record._rm_fields_to_amount()])

    #         # Valor do documento (NF)
    #         record.amount_total = (
    #             record.amount_untaxed + record.amount_tax + add_to_amount - rm_to_amount
    #         )

    #         # Valor Liquido (TOTAL + IMPOSTOS - RETENÇÕES)
    #         record.amount_taxed = record.amount_total - record.amount_tax_withholding

    #         if (
    #             record.cfop_id
    #             and record.cfop_id.destination == CFOP_DESTINATION_EXPORT
    #             and record.fiscal_operation_id.fiscal_operation_type == FISCAL_IN
    #         ):
    #             record.amount_total = (
    #                 record.amount_untaxed + record.amount_tax + add_to_amount - rm_to_amount + record.icms_value
    #             )            

