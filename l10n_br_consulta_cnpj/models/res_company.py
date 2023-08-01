from odoo import models, _
from odoo.exceptions import UserError

class Company(models.Model):
    _name = "res.company"
    _inherit = [_name, "format.address.mixin", "l10n_br_base.party.mixin"]

    def action_consult_cnpj(self):
        for company in self:
            if not company.cnpj_cpf:
                raise UserError(_("CNPJ não informado para a empresa %s") % company.name)
            else:
                company.partner_id.action_consult_cnpj()