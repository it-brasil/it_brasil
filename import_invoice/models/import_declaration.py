from odoo import fields, models

class ImportDeclarationLine(models.Model):
    _name = 'declaration.line'
    _description = "Linha da declaração de importação"

    name = fields.Char('Adição', size=3, required=True)
    sequence_di = fields.Integer('Sequência', default=1, required=True)
    manufacturer_code = fields.Char('Código do Fabricante', size=60, required=True)
    amount_discount = fields.Float(string='Valor', digits='Account', default=0.00)
    drawback_number = fields.Char('Número Drawback', size=11)