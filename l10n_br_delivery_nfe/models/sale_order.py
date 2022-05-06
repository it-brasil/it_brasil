# Copyright 2022 ATSTi Soluções
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, fields, models
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _prepare_invoice(self):
        self.ensure_one()
        result = super()._prepare_invoice()
        result.update(self._prepare_br_fiscal_dict())

        amount_gross_weight = 0.0
        for record in self:
            for line in record.order_line:
                if line.product_id:
                    if line.product_id.invoice_policy == "delivery":
                        amount_gross_weight += line.qty_delivered * line.product_id.weight
                    else:
                        amount_gross_weight += line.product_qty * line.product_id.weight
            if amount_gross_weight and record.carrier_id:
                result["nfe40_vol"] = [
                    (5, 0, 0),
                    (0, 0, {
                        "nfe40_esp": record.especie,
                        "nfe40_qVol": int(record.amount_volume),
                        "nfe40_pesoL": amount_gross_weight,
                        "nfe40_pesoB": amount_gross_weight,
                    })]
                
        return result    