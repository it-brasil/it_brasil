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

        # Compute 'price_total'.
        if taxes:
            taxes_res = taxes._origin.with_context(force_sign=1).compute_all(line_discount_price_unit,
                quantity=quantity, currency=currency, product=product, partner=partner, is_refund=move_type in ('out_refund', 'in_refund'))
            res['price_subtotal'] = taxes_res['total_excluded'] + self.freight_value + self.insurance_value + self.other_value
            #  + self.freight_value + self.insurance_value + self.other_value
            res['price_total'] = taxes_res['total_included']
        else:
            res['price_total'] = subtotal
        self._compute_amounts()
        # TODO 
        # nao esta calculando no total qdo insere pela linha do item
        return res