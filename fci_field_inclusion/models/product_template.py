# Copyright 2022 IT Brasil ((https://www.itbrasil.com.br).)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models

class ProductTemplate(models.Model):
	#_name = 'fci.product.template'
	_inherit = 'product.template'
	#_description = 'Template de Produto com FCI'

	fci = fields.Char(
		string = 'FCI',
		required=False,
        translate=False,
        readonly=False,
		size = 36
	)
