
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from datetime import date

class SaleOrder(models.Model):
	_inherit = 'sale.order'

	status_bloqueio = fields.Selection([
		('no_block','Sem Bloqueio'),
		('defaulter','Cliente Inadimplente'),
		('credit','Cliente sem Crédito'),
		('cleared','Liberado'),
		('unblocked','Desbloqueado')],
		string = 'Status de Bloqueio',
		default = 'no_block'
	)

	msg_error = fields.Char()

	def action_confirm(self):
		self.ensure_one()
		unpaid_invoices = self.partner_id.unpaid_invoices
		self.msg_error = False
		if unpaid_invoices:
			data_atual = date.today()
			faturas_vencidas_id = []
			#faturas_vencidas = self.env['account.move']
			for invoice in unpaid_invoices:
				data_vencimento = invoice.invoice_date_due
				if data_atual > data_vencimento:
					faturas_vencidas_id.append(invoice.id)
			modo_pagamento =  self.payment_term_id
			permissao_confirmacao = self.env.user.has_group('partner_credit_limit_stock.group_credit_limit_manager')
			if faturas_vencidas_id:
				self.status_bloqueio = 'defaulter'
				if permissao_confirmacao: 
					if modo_pagamento.name == 'A VISTA':
						if self.status_bloqueio != 'no_block':
							self.status_bloqueio = 'unblocked'
					else:
						self.msg_error = 'Devido a inadimplência do Cliente, essa Cotação só pode ser confirmada caso a condição de pagamento seja \'À VISTA\'.'
						return None
				else:	
					#faturas_vencidas = faturas_vencidas.browse(faturas_vencidas_id)
					self.msg_error = 'A Cotação não pode ser confirmada pois o Cliente está inadimplente. Para confirmar essa cotação é necessário o mesmo tornar-se solvente ou o Usuário possuir acesso financeiro correspondente (Gerente de Limite de Crédito).'
					return None			
		else:
			self.status_bloqueio = 'cleared'

		return super().action_confirm() 
