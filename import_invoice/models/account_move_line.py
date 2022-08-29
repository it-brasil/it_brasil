
from copy import deepcopy
from lxml import etree
from odoo import models, _, api, fields

class AccountMoveLine(models.AbstractModel):
    _inherit = "l10n_br_fiscal.document.line.mixin"

    number_di = fields.Char()
    date_registration = fields.Date('Data de Registro')
    state_id = fields.Many2one('res.country.state', 'Estado',domain="[('country_id.code', '=', 'BR')]")
    location = fields.Char('Local', size=60)
    date_release = fields.Date('Data de Liberação') 
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
    ], 'Transporte Internacional',default="1")
    afrmm_value = fields.Monetary('Valor da AFRMM')
    tpIntermedio = fields.Selection([
        ('1', '1 - Importação por conta própria'),
        ('2', '2 - Importação por conta e ordem'),
        ('3', '3 - Importação por encomenda'),
    ], 'Tipo de Importação', default='1')
    thirdparty_cnpj = fields.Char('CNPJ', size=18)
    thirdparty_state_id = fields.Many2one(
        'res.country.state', 'Estado Parceiro',
        domain="[('country_id.code', '=', 'BR')]")
    exporting_code = fields.Char('Código do Exportador', size=60)
    di_ids = fields.Many2many(
        'declaration.line',
        string='Linhas da DI',
        store=True, check_company=True, copy=True,
        )

class AccountMoveLineMethods(models.AbstractModel):
    _inherit = "l10n_br_fiscal.document.line.mixin.methods"
    
    @api.depends('journal_id')
    def _compute_company_id(self):
        for move in self:
            move.company_id = move.journal_id.company_id or move.company_id or self.env.company

    @api.model
    def inject_fiscal_fields(
        self,
        view_arch,
        view_ref="import_invoice.document_fiscal_line_mixin_form",
        xpath_mappings=None,
    ):
        """
        Injects common fiscal fields into view placeholder elements.
        Used for invoice line, sale order line, purchase order line...
        """
        fiscal_view = self.env.ref(
            "import_invoice.document_fiscal_line_mixin_form"
        ).sudo()
        fsc_doc = etree.fromstring(fiscal_view["arch"])
        doc = etree.fromstring(view_arch)

        if xpath_mappings is None:
            xpath_mappings = (
                # (placeholder_xpath, fiscal_xpath)
                (".//group[@name='fiscal_fields']", "//group[@name='fiscal_fields']"),
                (".//page[@name='fiscal_taxes']", "//page[@name='fiscal_taxes']"),
                (
                    ".//page[@name='fiscal_line_extra_info']",
                    "//page[@name='fiscal_line_extra_info']",
                ),
                # these will only collect (invisible) fields for onchanges:
                (
                    ".//control[@name='fiscal_taxes_fields']...",
                    "//page[@name='fiscal_taxes']//field",
                ),
                (
                    ".//control[@name='fiscal_line_extra_info_fields']...",
                    "//page[@name='fiscal_line_extra_info']//field",
                ),
            )
        for placeholder_xpath, fiscal_xpath in xpath_mappings:
            fiscal_nodes = fsc_doc.xpath(fiscal_xpath)
            for target_node in doc.findall(placeholder_xpath):
                if len(fiscal_nodes) == 1:
                    # replace unique placeholder
                    # (deepcopy is required to inject fiscal nodes in possible
                    # next places)
                    replace_node = deepcopy(fiscal_nodes[0])
                    target_node.getparent().replace(target_node, replace_node)
                else:
                    # append multiple fields to placeholder container
                    for fiscal_node in fiscal_nodes:
                        field = deepcopy(fiscal_node)
                        if not field.attrib.get("optional"):
                            field.attrib["invisible"] = "1"
                        target_node.append(field)
        return doc