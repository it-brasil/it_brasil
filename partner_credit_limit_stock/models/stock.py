# See LICENSE file for full copyright and licensing details.


from odoo import _, api, fields, models
from odoo.exceptions import UserError


class Picking(models.Model):
    _inherit = "stock.picking"

    msg_error = fields.Char()

    def button_validate(self):
        self.ensure_one()
        self.msg_error = False
        # Verifica se o stock.picking é OUT ou PICK
        if (self.picking_type_code == 'outgoing') or ((self.picking_type_code == 'internal') and self.sale_id):
            if self.partner_id:
                gerente = self.env.user.has_group("partner_credit_limit_stock.group_credit_limit_manager")
                #limite_disponivel = 0
                bool_credit_limit = False
                if self.partner_id.parent_id:
                    bool_credit_limit = self.partner_id.parent_id.enable_credit_limit
                else:
                    bool_credit_limit = self.partner_id.enable_credit_limit
                status_bloqueio = self.sale_id.status_bloqueio
                #Verificação de requisitos para a aprovação do OUT ou do PICK    
                if bool_credit_limit:
                    self.sale_id.limite_credito()
                    limite_disponivel = self.sale_id.partner_id.credit_rest
                    if limite_disponivel == 0:
                        if not gerente:
                            if (status_bloqueio != 'unblocked') and (status_bloqueio != 'cleared'):
                                self.sale_id.status_bloqueio = 'credit'
                                self.sale_id.passou_limite = True
                                self.msg_error = 'O Cliente não possui crédito disponivel para a confirmação de ambas as etapas da ordem de entrega (Pick e Out). Necessária aprovação de Usuário com acesso financeiro correspondente (Gerente de Limite de Crédito).'
                                return None 
                        else:
                            self.sale_id.status_bloqueio = 'unblocked'
        return super(Picking, self).button_validate()
