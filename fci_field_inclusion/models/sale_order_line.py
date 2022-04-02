# Copyright 2022 IT Brasil ((https://www.itbrasil.com.br).)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields
from odoo.tools.translate import _


class SaleOrderLine(models.Model):
	#_name = 'fci.sale.order.line'
	_inherit = ['sale.order.line']
	#_description = 'Linha de Pedido com FCI'

	fci = fields.Char(
		related='product_template_id.fci',
		readonly=True
	)