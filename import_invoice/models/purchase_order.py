from odoo import models

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def action_create_invoice(self):
        super(PurchaseOrder, self).action_create_invoice()
        invoice = max([inv.id for inv in self.invoice_ids])
        return invoice