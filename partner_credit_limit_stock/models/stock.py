# See LICENSE file for full copyright and licensing details.


from odoo import _, api, models
from odoo.exceptions import UserError


class Picking(models.Model):
    _inherit = "stock.picking"


    def button_validate(self):
        # TODO validar se o usuario é gerente se for executar somente o return ultima linha
        self.ensure_one()
        if self.partner_id:
            gerente = self.env.user.has_group("partner_credit_limit_stock.group_credit_limit_manager")
            limite_disponivel = self.partner_id.parent_id._check_limit()
            bool_credit_limit = self.partner_id.parent_id.enable_credit_limit
            if bool_credit_limit:
                if limite_disponivel == 0:
                    if not gerente:
                        msg = 'Your available credit limit' \
                            ' Amount = %s \nCheck "%s" Accounts or Credit ' \
                            'Limits.' % (limite_disponivel,
                            self.partner_id.name)
                        raise UserError(_('You can not confirm Delivery Order (PICK and OUT)'
                                            'Order. \n' + msg))
        return super(Picking, self).button_validate()
