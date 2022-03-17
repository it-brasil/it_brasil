#
#    Copyright © 2022–; Brasil; IT Brasil; Todos os direitos reservados
#    Copyright © 2022–; Brazil; IT Brasil; All rights reserved
#

from odoo import _, api, fields
from odoo.exceptions import UserError, ValidationError
from odoo.addons.spec_driven_model.models import spec_models
from nfelib.v4_00 import leiauteNFe_sub as nfe_sub
from io import StringIO

class NFe(spec_models.StackedModel):
	_inherit = "l10n_br_fiscal.document" # l10n_br_nfe

	def valida_dados_destinatario(self):
		partner = self.partner_id
		if partner:
			msg = 'Os dados cadastrais do destinário estão incompletos. Favor preencher os seguintes campos:\n'
			count = 0
			if partner.company_type == 'person':
				if not partner.legal_name:
					msg += '\n    - Nome Completo;'
					count += 1
				if not partner.cnpj_cpf:
					msg += '\n    - CPF;'
					count += 1
			if partner.company_type == 'company':
				if not partner.legal_name:
					msg += '\n    - Razão Social;'
					count += 1
				if not partner.cnpj_cpf:
					msg += '\n    - CNPJ;'
					count += 1
				if not partner.inscr_est:
					msg += '\n    - Inscrição Estadual;'
					count += 1
			if not partner.zip:
				msg += '\n    - CEP;'
				count += 1
			if not partner.street_name:
				msg += '\n    - Nome da Rua (Logradouro);'
				count += 1
			if not partner.street_number:
				msg += '\n    - Casa (Número da rua);'
				count += 1
			if not partner.district:
				msg += '\n    - Bairro;'
				count += 1
			if not partner.city:
				msg += '\n    - Cidade;'
				count += 1
			if not partner.state_id:
				msg += '\n    - Estado;'
				count += 1
			if not partner.country_id:
				msg += '\n    - País;'
				count += 1
			if not partner.phone and partner.mobile:
				partner.phone = partner.mobile
			else:
				msg += '\n    - Telefone;'
				count += 1
			if count > 0:
				raise ValidationError(msg)		
		else: 
			raise ValidationError('Não há Parceiro vinculado ao documento fiscal!')


	def valida_dados_produtos(self):
		products = self.fiscal_line_ids.product_id.product_tmpl_id
		if products:
			final_msg = ''
			for product in products:
				count = 0
				msg  = ''
				if product.name:
					msg += 'Os dados cadastrais do produto %s estão incompletos. Favor preencher os seguintes campos:\n - ' %(product.name)
					if not product.ncm_id:
						lista += 'Ncm, ' 
						count += 1
					if not product.icms_origin:
						lista += 'Origem do ICMS'
						count += 1 
					if msg.endswith(','):
						msg = msg.rstrip(',')
					msg += '\n\n'
					if count > 0:
						final_msg += msg
				else:
					count += 1
					msg += 'Os dados cadastrais do produto com id %d estão incompletos. Favor preencher os seguintes campos:\n - Nome do Produto, ' %(product.product_id.product_tmpl_id.id)
					if not product.ncm_id:
						msg += 'Ncm, ' 
					if not product.icms_origin:
						msg += 'Origem do ICMS'
					if msg.endswith(','):
						msg = msg.rstrip(',')
					msg += '\n\n'
					final_msg += msg
			if final_msg:
				raise ValidationError(final_msg)
		else:
			raise ValidationError('Não há Produto vinculado ao documento fiscal!')


	def _valida_xml(self, xml_file):
		self.ensure_one()
		self.valida_dados_destinatario()
		self.valida_dados_produtos()
		erros = nfe_sub.schema_validation(StringIO(xml_file))
		erros = "\n".join(erros)
		self.write({"xml_error_message": erros or False})