# Copyright 2021 Akretion (Renato Lima <renato.lima@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


TPVIATRANSP_DI = [
    ("1", "1 - Maritima"),
    ("2", "2 - Fluvial"),
    ("3", "3 - Lacustre"),
    ("4", "4 - Aerea"),
    ("5", "5 - Postal"),
    ("6", "6 - Ferroviaria"),
    ("7", "7 - Rodoviaria"),
    ("8", "8 - Conduto/Rede Transmissão"),
    ("9", "9 - Meios Próprios"),
    ("10", "10 - Entrada/Saída Ficta"),
    ("11", "11 - Courier"),
    ("12", "12 - Em mãos"),
    ("13", "13 - Por reboque"),
]

TPINTERMEDIO_DI = [
    ("1", "1 - Por conta própria"),
    ("2", "2 - Por conta e ordem"),
    ("3", "3 - Encomenda"),
]


class NFeDI(models.AbstractModel):
    _inherit = "nfe.40.di"
    # _inherits = {"l10n_br_fiscal.document.line": "fiscal_document_line_id"}

    # document_line_id = fields.Many2one(
    #     comodel_name="l10n_br_fiscal.document.line", string="Fiscal Document Line", index=True
    # )

    nfe40_tpViaTransp = fields.Selection(
        TPVIATRANSP_DI,
        string="Via transporte DI",
        # required=True,
        help="Via de transporte internacional informada na DI"
        "\n1-Maritima;2-Fluvial;3-Lacustre;4-Aerea;5-Postal;6-Ferroviaria;7-Ro"
        "\ndoviaria;8-Conduto;9-Meios Proprios;10-Entrada/Saida Ficta;"
        "\n11-Courier;12-Em maos;13-Por reboque.")
    
    nfe40_tpIntermedio = fields.Selection(
        TPINTERMEDIO_DI,
        string="Forma Importação",
        # required=True,
        help="Forma de Importação quanto a intermediação"
        "\n1-por conta propria;2-por conta e ordem;3-encomenda")

    state_clearance_id = fields.Many2one(
        comodel_name="res.country.state",
        string="UF desembaraço aduaneiro",
    )

    nfe40_UFDesemb = fields.Char(
        related="state_clearance_id.code",
        string="UF desembaraço aduaneiro",
    )

    partner_acquirer_id = fields.Many2one(
        comodel_name="res.partner",
        string="Adquirente/Encomendante",
    )

    nfe40_CNPJ = fields.Char(
        related="partner_acquirer_id.nfe40_CNPJ",
        string="CNPJ adquirente/encomendante",
    )

    nfe40_UFTerceiro = fields.Char(
        related="partner_acquirer_id.state_id.code",
        string="UF adquirente/encomendante",
    )
