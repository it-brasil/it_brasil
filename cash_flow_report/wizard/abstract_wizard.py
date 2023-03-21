# Copyright 2019 Lorenzo Battistini @ TAKOBI
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
from odoo import fields, models

_logger = logging.getLogger(__name__)


class AbstractWizard(models.AbstractModel):
    _name = "account_financial_report_abstract_wizard"
    _description = "Abstract Wizard"

    company_id = fields.Many2one(
        comodel_name="res.company",
        default=lambda self: self._default_company_id(),
        domain=lambda self: [
            ("id", "in", self.env.context.get("allowed_company_ids", []))],
    )

    def _default_company_id(self):
        companies = self.env.context.get("allowed_company_ids")
        if companies:
            return companies[0]
        return self.env.user.company_id

    def _get_account_ids_domain(self, company_id=None):
        company_id = self._default_company_id() if company_id is None else company_id
        domain = ["&",
                  ("company_id", "=", company_id),
                  ("deprecated", "=", False),
                  "|",
                  ("reconcile", "=", True),
                  ("internal_type", "in", ["receivable", "payable", "liquidity"])]
        return domain

    def button_export_html(self):
        self.ensure_one()
        report_type = "qweb-html"
        return self._export(report_type)

    def button_export_pdf(self):
        self.ensure_one()
        report_type = "qweb-pdf"
        return self._export(report_type)

    def button_export_xlsx(self):
        self.ensure_one()
        report_type = "xlsx"
        return self._export(report_type)
