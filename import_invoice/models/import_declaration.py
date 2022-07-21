import logging
from odoo import fields, models, _, api

class ImportDeclarationLine(models.Model):
    _name = 'nfe.import.declaration.line'
    _description = "Linha da declaração de importação"

    import_declaration_id = fields.Many2one(
        'account.move.line', 'DI', ondelete='cascade')
    sequence = fields.Integer('Sequência', default=1, required=True)
    name = fields.Char('Adição', size=3, required=True)
    manufacturer_code = fields.Char(
        'Código do Fabricante', size=60, required=True)
    amount_discount = fields.Float(
        string='Valor', digits='Account', default=0.00)
    drawback_number = fields.Char('Número Drawback', size=11)