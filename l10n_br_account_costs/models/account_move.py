# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html


from odoo import _, api, fields, models


class AccountMove(models.Model):
    _name = "account.move"
    _inherit = [
        _name,
        "l10n_br_fiscal.document.move.mixin",
    ]
    _inherits = {"l10n_br_fiscal.document": "fiscal_document_id"}
    _order = "date DESC, name DESC"

    @api.model_create_multi
    def create(self, vals_list):
        result = super(AccountMove, self).create(vals_list)        
        if result.amount_freight_value or result.amount_insurance_value or result.amount_other_value:
            self._amount_other_costs(result)

        return result

    def _amount_other_costs(self, moves):
        new_line = False
        freight = 0.0
        insurance = 0.0
        other = 0.0
        for move in moves:
            if move.payment_state == 'invoicing_legacy':
                move.payment_state = move.payment_state
                continue
            # se ja existe tem q excluir
            for line in move.line_ids:
                if line.name in ["[FREIGHT]", "[INSURANCE]", "[OTHER]"]:
                    move.with_context(
                        check_move_validity=False,
                        skip_account_move_synchronization=True,
                        force_delete=True,
                    ).write(
                        {
                            "line_ids": [(2, line.id)],
                            "to_check": False,
                        }
                    )
            for line in move.line_ids:
                if not line.exclude_from_invoice_tab and line.freight_value > 0:
                    if line.freight_value:
                        new_line = self.env["account.move.line"].new(
                            {
                                "name": "[FREIGHT]",
                                "account_id": line.account_id.id,
                                "move_id": self.id,
                                "exclude_from_invoice_tab": True,
                                "price_unit": line.freight_value,
                                "debit":  line.freight_value,
                            }
                        )
                        freight += line.freight_value
                        move.with_context(check_move_validity=False).line_ids += new_line
                        to_write = []

                        valor = line.balance - line.freight_value
                        to_write.append((1, line.id, {
                                    'debit': valor,
                                    'credit': 0.0,
                                    'amount_currency': line.balance - line.freight_value,
                            }))

                        move.write({'line_ids': to_write})                    
                    
                if not line.exclude_from_invoice_tab and line.insurance_value > 0:
                    if line.insurance_value:
                        new_line = self.env["account.move.line"].new(
                            {
                                "name": "[INSURANCE]",
                                "account_id": line.account_id.id,
                                "move_id": self.id,
                                "exclude_from_invoice_tab": True,
                                "price_unit": line.insurance_value,
                                "debit":  line.insurance_value,
                            }
                        )
                        insurance += line.insurance_value
                        move.with_context(check_move_validity=False).line_ids += new_line
                        to_write = []

                        valor = line.balance - line.insurance_value
                        to_write.append((1, line.id, {
                                    'debit': valor,
                                    'credit': 0.0,
                                    'amount_currency': line.balance - line.insurance_value,
                            }))

                        move.write({'line_ids': to_write})                    

                if not line.exclude_from_invoice_tab and line.other_value > 0:
                    if line.other_value:
                        new_line = self.env["account.move.line"].new(
                            {
                                "name": "[OTHER]",
                                "account_id": line.account_id.id,
                                "move_id": self.id,
                                "exclude_from_invoice_tab": True,
                                "price_unit": line.other_value,
                                "debit":  line.other_value,
                            }
                        )
                        other += line.other_value
                        move.with_context(check_move_validity=False).line_ids += new_line
                        to_write = []

                        valor = line.balance - line.other_value
                        to_write.append((1, line.id, {
                                    'debit': valor,
                                    'credit': 0.0,
                                    'amount_currency': line.balance - line.other_value,
                            }))

                        move.write({'line_ids': to_write})                    

            if freight or insurance or other:
                move.write({
                    'amount_total': move.amount_total + freight + insurance + other,
                    'amount_total_signed': move.amount_total_signed - freight - insurance - other})
