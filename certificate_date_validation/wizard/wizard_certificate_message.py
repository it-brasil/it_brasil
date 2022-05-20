#
#    Copyright © 2021–; Brasil; IT Brasil; Todos os direitos reservados
#    Copyright © 2021–; Brazil; IT Brasil; All rights reserved
#

from odoo import _, fields, models

class WizardCertificateMessage(models.TransientModel):
    _name = 'wizard.certificate.message'
    _description = "Mensagem Sobre a data de Expiração do Certificado A1"

    account_move_id = fields.Many2one(comodel_name="account.move")
    dias_restantes = fields.Char()