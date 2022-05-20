# Copyright 2022 IT Brasil ((https://www.itbrasil.com.br).)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields
from odoo.addons.spec_driven_model.models import spec_models


class NFeLine(spec_models.StackedModel):
    _inherit = ["l10n_br_fiscal.document.line"]

    nfe40_nFCI = fields.Char(
        string = 'FCI',
        related = 'product_id.fci'
    )
