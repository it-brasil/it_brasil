# Copyright 2022 IT Brasil ((https://www.itbrasil.com.br).)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields
from odoo.addons.spec_driven_model.models import spec_models


class NFeLine(spec_models.StackedModel):
    _inherit = ["l10n_br_fiscal.document.line"]
 
    # DI 
    xml_number_di = fields.Char(related = 'account_line_ids.number_di') # nDI
    xml_date_registration = fields.Date(related = 'account_line_ids.date_registration')  #dDI
    xml_location = fields.Char(related = 'account_line_ids.location')  #xLocDesemb
    xml_state_id = fields.Char(related = 'account_line_ids.state_id.name')  #UFDesemb
    xml_date_release = fields.Date(related = 'account_line_ids.date_release')  #dDesemb
    xml_type_transportation = fields.Selection(related = 'account_line_ids.type_transportation')  #tpViaTransp
    xml_type_import = fields.Selection(related = 'account_line_ids.type_import') # tpIntermedio
    xml_exporting_code = fields.Char( related = 'account_line_ids.exporting_code')  #cExportador

    # ADI
    """ name
    sequence_di
    manufacturer_code
    drawback_number """