# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    date_due = fields.Date(string="Due Dates", compute="_compute_date_due", store=True)

    @api.depends("date", "date_maturity")
    def _compute_date_due(self):
        for record in self:
            if record.date_maturity:
                record.date_due = record.date_maturity
            else:
                record.date_due = record.date

