
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
		('unblocked','Desbloqueado'),
		('invoiced_order','Pedido Faturado')],
		string = 'Status de Bloqueio',
		default = 'no_block',
		tracking = True
	)

	passou_limite = fields.Boolean()
	msg_error = fields.Char()

	def action_liberar_entrega(self):
		self.status_bloqueio = 'unblocked'
		self.msg_error = False
		self.picking_ids.msg_error = False
		self.passou_limite = False

	def action_cancel(self):
		super().action_cancel()
		if self.state == 'cancel':
			self.status_bloqueio = 'no_block'

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
					if modo_pagamento.allow_sales_order:
						if (self.status_bloqueio != 'no_block') and (self.status_bloqueio != 'cleared'):
							self.status_bloqueio = 'unblocked'
					else:
						self.msg_error = 'Essa condição de pagamento não permite confirmar cotações caso o cliente esteja inadimplente.'
						return None
				else:	
					self.msg_error = 'A Cotação não pode ser confirmada pois o Cliente está inadimplente. Para confirmar essa cotação é necessário o mesmo tornar-se solvente ou o Usuário possuir acesso financeiro correspondente (Gerente de Limite de Crédito).'
					return None			
		else:
			self.status_bloqueio = 'cleared'
		bool_credit_limit = self.partner_id.enable_credit_limit
		if bool_credit_limit:
			self.limite_credito()
			if self.partner_id.credit_rest == 0: 
				self.status_bloqueio = 'credit'
				self.passou_limite = True
				self.msg_error = 'O Cliente não possui crédito suficiente para que outros usuários possam validar as ordens de entrega (PICK e OUT). É necessário liberação da entrega por parte de um usuário com acesso financeiro correspondente (gerente de limite de crédito).'
		return super().action_confirm() 

	def limite_credito(self):
		self.ensure_one()
		amount_sales, debit, credit = 0.0, 0.0, 0.0
		parceiro = self.partner_id
		confirmed_sale_orders = self.env['sale.order'].search([
			('partner_id', '=', parceiro.id),
			('state', 'in', ['sale','done']),
			('invoice_status', '!=', 'invoiced')
		])
		if not confirmed_sale_orders:
			amount_sales = self.amount_total	
		invoice_lines = self.env['account.move.line'].search([
            ('partner_id', '=', parceiro.id),
            ('account_id.user_type_id.type', 'in',['receivable', 'payable']),
            ('parent_state','!=','cancel')
        ])
		if confirmed_sale_orders:
			for sale in confirmed_sale_orders:
				amount_sales += sale.amount_total
		if invoice_lines:
			for line in invoice_lines:
				credit += line.credit
				debit += line.debit
		partner_credit_limit = (debit + amount_sales) - credit
		available_credit_limit = parceiro.credit_limit - partner_credit_limit
		if available_credit_limit < 0: 
			parceiro.credit_rest = 0
			parceiro.credit_negative_margin = available_credit_limit
		else:
			parceiro.credit_rest = available_credit_limit
			parceiro.credit_negative_margin = 0