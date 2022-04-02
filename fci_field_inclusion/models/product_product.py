# Copyright 2022 IT Brasil ((https://www.itbrasil.com.br).)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models

class ProductProduct(models.Model):
	#_name = 'fci.product.product'
	_inherit = 'product.product'
	#_description = 'Template de Produto com FCI'

	fci = fields.Char(
		string = 'FCI',
		related = 'product_tmpl_id.fci',
		required=False,
        translate=False,
        readonly=True,
		size = 36
	)