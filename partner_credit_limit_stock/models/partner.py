# See LICENSE file for full copyright and licensing details.

from datetime import datetime, timedelta

from odoo import api, fields, models, _
import logging

_logger = logging.getLogger(__name__)

notification = {
    "type": "ir.actions.client",
    "tag": "display_notification",
    "params": {"next": {"type": "ir.actions.act_window_close"}},
}


class ResPartner(models.Model):
    _inherit = 'res.partner'

    credit_limit = fields.Float(
        string='Limite de Crédito',
        default=0.0,
        tracking=True,
    )
    credit_rest = fields.Float(
        string='Valor Disponível',  # antigo valor faturado
        readonly=True,
        compute='_check_limit',
    )
    credit_negative_margin = fields.Float(
        string='Margem Negativa',  # antigo valor faturado
        readonly=True,
        compute='_check_limit',
    )

    enable_credit_limit = fields.Boolean(
        string='Tem limite de crédito?',
        tracking=True,
    )

    @api.model
    def create(self, vals):
        new = super().create(vals)
        ref = self.env.ref
        vals_activity = {
            "res_id": new.id,
            "res_model_id": self.env["ir.model"].search([("model", "=", "res.partner")]).id,
            "user_id": 1,
            "summary": f"Analisar limite de crédito",
            'activity_type_id': ref('partner_credit_limit_stock.mail_activity_data_credit_limit').id,
            "note": f"Um novo contato foi adicionado, verifique se é preciso definir um limite de crédito.",
            "date_deadline": datetime.today(),
        }
        self.env["mail.activity"].create(vals_activity)
        return new

    # def write(self, vals):
    #     if "credit_limit" in vals or "enable_credit_limit" in vals:
    #         check_pending_quotation = self.env['sale.order'].search([
    #             ('partner_id', '=', self.id),
    #             ('state', 'not in', ['cancel', 'done']),
    #             ('status_bloqueio', '=', 'credit')
    #         ])

    #         if check_pending_quotation:
    #             _logger.warning(len(check_pending_quotation))
    #             if len(check_pending_quotation) > 1:
    #                 notification["params"].update(
    #                     {
    #                         "title": _("Atenção"),
    #                         "message": _("O cliente possúi %s cotações/pedidos em aberto, é precisar entrar em cada ítem e confirmar manualmente.", len(check_pending_quotation)),
    #                         "type": "warning",
    #                     }
    #                 )
    #                 return notification

    #         else:
    #             notification["params"].update(
    #                 {
    #                     "title": _("Informação"),
    #                     "message": _("O cliente não possúi pedidos em aberto, o limite de crédito é de %s", self.credit_limit),
    #                     "type": "info",
    #                 }
    #             )
                
    #             return notification

    #     return super().write(vals)

    def _check_limit(self):
        vendas = self.env['sale.order'].search([
            ('partner_id', '=', self.id),
            ('state', 'in', ['sale', 'done'])],
            order='id desc'
        )
        if self.enable_credit_limit and vendas:  # (vendas or faturas):
            vendas[0].limite_credito()
        else:
            self.credit_rest = self.credit_limit
            self.credit_negative_margin = 0.0
