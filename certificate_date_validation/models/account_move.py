#
#    Copyright © 2021–; Brasil; IT Brasil; Todos os direitos reservados
#    Copyright © 2021–; Brazil; IT Brasil; All rights reserved
#

from datetime import datetime, timedelta
from odoo import _, models

class AccountMove(models.Model):
	_inherit = 'account.move'


	def action_post(self):
		super().action_post()
		if self.env.user.has_group('partner_credit_limit_stock.group_credit_limit_manager'):
			data_expiracao = self.env.user.company_id.certificate_nfe_id.date_expiration
			data_inicio_contagem = data_expiracao - timedelta(30)
			data_atual = datetime.now()
			if data_inicio_contagem <= data_atual and data_atual < data_expiracao:
				data_restante = data_expiracao - data_atual
				return {
					'name': _('Wizard Certificate Message'),
				'view_mode': 'form',
					'res_model': 'wizard.certificate.message',
					'view_id': self.env.ref('certificate_date_validation.wizard_certificate_message_view_form').id,
					'type': 'ir.actions.act_window',
					'context': {
						'default_account_move_id': self.id,
						'default_dias_restantes' : str(data_restante.days),
					},
					'target': 'new'
				}
		
		