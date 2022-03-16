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

	def valida_dados_obrigatorios(self):

		msg = ''
		partner = self.partner_id
		products = self.invoice_line_ids.product_id.product_tmpl_id

		if partner:
			if partner.company_type == 'person':
				if not partner.legal_name:
					msg += '\n O campo Nome Completo, no registro de contato, não foi preenchido'
				if not partner.cnpj_cpf:
					msg += '\n O campo CPF, no registro de contato, não foi preenchido'
			if partner.company_type == 'company':
				if not partner.legal_name:
					msg += '\n O campo Razão Social, no registro de contato, não foi preenchido'
				if not partner.cnpj_cpf:
					msg += '\n O campo CNPJ, no registro de contato, não foi preenchido'
				if not partner.inscr_est:
					msg += '\n O campo Inscrição Estadual, no registro de contato, não foi preenchido'
		else: 
			msg += 'Não há Parceiro vinculado ao documento fiscal'

		if products:
			for product in products:
				if not product.ncm_id:
					msg += '\n O campo Ncm, no cadastro do produto %s, não foi preenchido' %(product.name)
				if not product.name:
					msg += '\n O campo Nome do Produto para o produto de id %d não foi preenchido' %(product.product_id.product_tmpl_id.id)
		else:
			msg += 'Não há Produto vinculado ao documento fiscal' 
			
		if msg: 
			raise ValidationError(msg)


	def _valida_xml(self, xml_file):
		self.ensure_one()
		self.valida_dados_obrigatorios()
		erros = nfe_sub.schema_validation(StringIO(xml_file))
		erros = "\n".join(erros)
		self.write({"xml_error_message": erros or False})