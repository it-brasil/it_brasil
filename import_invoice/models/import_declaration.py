from odoo import fields, models


class ImportDeclaration(models.Model):
    _name = 'nfe.import.declaration'
    _description = "Declaração de Importação"

    move_id = fields.Many2one(
        'account.move', 'Fatura',
        ondelete='cascade', index=True)
    eletronic_document_line_id = fields.Many2one(
        'eletronic.document.line', 'Linha de Documento Eletrônico',
        ondelete='cascade', index=True)

    name = fields.Char('Número da DI', size=10, required=True)
    date_registration = fields.Date('Data de Registro', required=True)
    state_id = fields.Many2one(
        'res.country.state', 'Estado',
        domain="[('country_id.code', '=', 'BR')]", required=True)
    location = fields.Char('Local', required=True, size=60)
    date_release = fields.Date('Data de Liberação', required=True)
    type_transportation = fields.Selection([
        ('1', '1 - Marítima'),
        ('2', '2 - Fluvial'),
        ('3', '3 - Lacustre'),
        ('4', '4 - Aérea'),
        ('5', '5 - Postal'),
        ('6', '6 - Ferroviária'),
        ('7', '7 - Rodoviária'),
        ('8', '8 - Conduto / Rede Transmissão'),
        ('9', '9 - Meios Próprios'),
        ('10', '10 - Entrada / Saída ficta'),
    ], 'Transporte Internacional', required=True, default="1")
    afrmm_value = fields.Float(
        'Valor da AFRMM', digits='Account', default=0.00)
    type_import = fields.Selection([
        ('1', '1 - Importação por conta própria'),
        ('2', '2 - Importação por conta e ordem'),
        ('3', '3 - Importação por encomenda'),
    ], 'Tipo de Importação', default='1', required=True)
    thirdparty_cnpj = fields.Char('CNPJ', size=18)
    thirdparty_state_id = fields.Many2one(
        'res.country.state', 'Estado Parceiro',
        domain="[('country_id.code', '=', 'BR')]")
    exporting_code = fields.Char(
        'Código do Exportador', required=True, size=60)
    line_ids = fields.One2many(
        'nfe.import.declaration.line',
        'import_declaration_id', 'Linhas da DI')


class ImportDeclarationLine(models.Model):
    _name = 'nfe.import.declaration.line'
    _description = "Linha da declaração de importação"

    import_declaration_id = fields.Many2one(
        'nfe.import.declaration', 'DI', ondelete='cascade')
    sequence = fields.Integer('Sequência', default=1, required=True)
    name = fields.Char('Adição', size=3, required=True)
    manufacturer_code = fields.Char(
        'Código do Fabricante', size=60, required=True)
    amount_discount = fields.Float(
        string='Valor', digits='Account', default=0.00)
    drawback_number = fields.Char('Número Drawback', size=11)