# -*- coding: utf-8 -*-
from odoo import models, api, _
import logging
_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = "account.move"

    def action_post(self, invoice=False):
        installments = 1
        result = super().action_post()
        invoice_name = self.document_number if self.document_number else self.payment_reference if self.payment_reference else self.name
        invoice_lines = self.line_ids.filtered(
            lambda l: l.account_id.internal_type in ('receivable', 'payable'))
        payment_term = self.invoice_payment_term_id
        if invoice_lines:
            if payment_term:
                for line in invoice_lines:
                    line.write({
                        'name': _('%s - %s/%s') % (str(invoice_name), str(installments), str(len(invoice_lines)) )
                    })
                    installments += 1
        return result

