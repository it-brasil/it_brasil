# -*- coding: utf-8 -*-

from odoo import api, models, fields, _
from datetime import date

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    partner_id = fields.Many2one(
        comodel_name="res.partner",
        related="move_id.partner_id",
        string="Partner",
        store=True
    )

    # # existe o price_total 
    # payment_value = fields.Monetary(
    #     string="Valor",
    #     compute="_compute_payment_value",
    #     currency_field="company_currency_id"
    # )

    payment_date = fields.Date(
        string="Data do Pagamento"
    )

    # # pra que serve ???
    # current_date = fields.Date(
    #     default= lambda self: date.today().strftime('%Y-%m-%d')
    # )

    number_nfe = fields.Char(
        related="move_id.document_number",
        string="Nota Fiscal",
    )

    # @api.depends("debit", "credit", "account_id.internal_type", "amount_residual")
    # def _compute_payment_value(self):
    #     for res in self:
    #         if res.account_id.internal_type == "receivable":
    #             res.payment_value = res.debit
    #         else:
    #             res.payment_value = (res.credit * -1)

	# def action_register_payment_move_line(self):
	# 	dummy, act_id = self.env["ir.model.data"].get_object_reference(
	# 		"itbr_account_line_report_menu", "action_payment_account_move_line"
	# 	)
	# 	receivable = self.account_id.internal_type == "receivable"
	# 	vals = self.env["ir.actions.act_window"].browse(act_id).read()[0]
	# 	vals["context"] = {
	# 		"default_amount": self.debit or self.credit,
	# 		"default_partner_type": "customer" if receivable else "supplier",
	# 		"default_partner_id": self.partner_id.id,
	# 		"default_communication": self.name,
	# 		"default_move_line_id": self.id,
	# 	}
	# 	return vals

    def action_register_payment_move_line(self):
        ''' Open the account.payment.register wizard to pay the selected journal entries.
        :return: An action opening the account.payment.register wizard.
        '''
        return {
            'name': _('Register Payment'),
            'res_model': 'account.payment.register',
            'view_mode': 'form',
            'context': {
                'active_model': 'account.move.line',
                'active_ids': self.ids,
            },
            'target': 'new',
            'type': 'ir.actions.act_window',
        }