# See LICENSE file for full copyright and licensing details.


from odoo import _, api, models
from odoo.exceptions import UserError


class Picking(models.Model):
    _inherit = "stock.picking"


    def button_validate(self):
        # TODO validar se o usuario é gerente se for executar somente o return ultima linha
        if self.partner_id:
            gerente = self.env.user.has_group("sales_team.group_sale_manager")
            limite_disponivel = self.partner_id._check_limit()
            bool_credit_limit = self.partner_id.enable_credit_limit
            if bool_credit_limit:
                if limite_disponivel == 0:
                    if not gerente:
                        msg = 'Your available credit limit' \
                            ' Amount = %s \nCheck "%s" Accounts or Credit ' \
                            'Limits.' % (limite_disponivel,
                            self.partner_id.name)
                        raise UserError(_('You can not confirm Sale '
                                            'Order. \n' + msg))
        return super(Picking, self).button_validate()
