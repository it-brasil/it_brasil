# Author: Damien Crier
# Author: Julien Coux
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.osv import expression
import logging
_logger = logging.getLogger(__name__)


class CashFlowReportWizard(models.TransientModel):
    """Open items report wizard."""

    _name = "cash.flow.report.wizard"
    _description = "Cash Flow Report Wizard"
    _inherit = "account_financial_report_abstract_wizard"

    date_at = fields.Date(string="Data final", required=True,
                          default=fields.Date.context_today)
    date_from = fields.Date(string="Data inicio", required=True)
    target_move = fields.Selection(
        [("posted", "Todas entradas postadas"), ("all", "Todas Entradas")],
        string="Movimentos",
        required=True,
        default="posted",
    )
    account_ids = fields.Many2many(
        comodel_name="account.account",
        string="Contas a receber e pagar",
        domain=lambda self: self._get_account_ids_domain(),
    )
    liquidity_accounts_ids = fields.Many2many(
        comodel_name="account.account",
        string="Contas de liquidez",
        domain=lambda self: self._get_account_ids_domain(),
        relation="cash_flow_report_wizard_liquidity_accounts_rel",
    )
    

    hide_account_at_0 = fields.Boolean(
        string="Ocultar saldo zerado",
        default=True,
        help="Use this filter to hide an account or a partner "
        "with an ending balance at 0. "
        "If partners are filtered, "
        "debits and credits totals will not match the trial balance.",
    )
    receivable_accounts_only = fields.Boolean()
    payable_accounts_only = fields.Boolean()
    bank_accounts_only = fields.Boolean()
    partner_ids = fields.Many2many(
        comodel_name="res.partner",
        string="Filtro parceiros"
    )
    foreign_currency = fields.Boolean(
        string="Mostrar moeda estrangeira",
        help="Display foreign currency for move lines, unless "
        "account currency is not setup through chart of accounts "
        "will display initial and final balance in that currency.",
        default=lambda self: self._default_foreign_currency(),
    )
    show_partner_details = fields.Boolean(
        string="Mostrar detalhe parceiros",
        default=False,
    )
    account_code_from = fields.Many2one(
        comodel_name="account.account",
        string="Conta inicial",
        help="Starting account in a range",
        domain=lambda self: self._get_account_ids_domain(),
    )
    account_code_to = fields.Many2one(
        comodel_name="account.account",
        string="Conta final",
        help="Ending account in a range",
        domain=lambda self: self._get_account_ids_domain(),
    )

    @api.onchange("account_code_from", "account_code_to")
    def on_change_account_range(self):
        if (
            self.account_code_from
            and self.account_code_from.code.isdigit()
            and self.account_code_to
            and self.account_code_to.code.isdigit()
        ):
            start_range = int(self.account_code_from.code)
            end_range = int(self.account_code_to.code)
            self.account_ids = self.env["account.account"].search(
                [
                    ("code", ">=", start_range),
                    ("code", "<=", end_range),
                ]
            )

    def _default_foreign_currency(self):
        return self.env.user.has_group("base.group_multi_currency")

    @api.onchange("company_id")
    def onchange_company_id(self):
        if self.company_id:
            self.account_ids = self.env["account.account"].search(
                self._get_account_ids_domain(self.company_id.id)
            )
            self.account_code_from = None
            self.account_code_to = None
            self.partner_ids = None
            self.receivable_accounts_only = False
            self.payable_accounts_only = False
            self.bank_accounts_only = False
            self.foreign_currency = self._default_foreign_currency()

    @api.onchange("receivable_accounts_only", "payable_accounts_only")
    def onchange_type_accounts_only(self):
        """Handle receivable/payable accounts only change."""
        domain = [("company_id", "=", self.company_id.id),
                  ("deprecated", "=", False)]
        if self.receivable_accounts_only or self.payable_accounts_only:
            self.account_code_from = False
            self.account_code_to = False
            if self.receivable_accounts_only:
                domain += [("internal_type", "=", "receivable")]
            if self.payable_accounts_only:
                domain += [("internal_type", "=", "payable")]
            if self.receivable_accounts_only and self.payable_accounts_only:
                domain = [("internal_type", "in", ("receivable", "payable"))]
            self.account_ids = self.env["account.account"].search(domain)
        else:
            self.account_ids = None
    
    @api.onchange("bank_accounts_only")
    def onchange_bank_accounts_only(self):
        """Handle bank accounts only change."""
        domain = [("company_id", "=", self.company_id.id),
                  ("deprecated", "=", False)]
        if self.bank_accounts_only:
            self.account_code_from = False
            self.account_code_to = False
            domain += [("internal_type", "=", "liquidity")]
            self.liquidity_accounts_ids = self.env["account.account"].search(domain)
        else:
            self.liquidity_accounts_ids = None

    def _print_report(self, report_type):
        self.ensure_one()
        data = self._prepare_report_cash_flow()
        if report_type == "xlsx":
            report_name = "cash_flow_report.cash_flow_report_xlsx"
        else:
            report_name = "cash_flow_report.cash_flow_report"
        report = self.env["ir.actions.report"].search(
            [("report_name", "=", report_name),
             ("report_type", "=", report_type)],
            limit=1,
        )
        return (
            report.report_action(self, data=data)
        )

    def _prepare_report_cash_flow(self):
        self.ensure_one()
        return {
            "wizard_id": self.id,
            "date_at": fields.Date.to_string(self.date_at),
            "date_from": self.date_from or False,
            "only_posted_moves": self.target_move == "posted",
            "hide_account_at_0": self.hide_account_at_0,
            "foreign_currency": self.foreign_currency,
            "show_partner_details": self.show_partner_details,
            "company_id": self.company_id.id,
            "target_move": self.target_move,
            "account_ids": self.account_ids.ids,
            "liquidity_accounts_ids": self.liquidity_accounts_ids.ids,
            "partner_ids": self.partner_ids.ids or [],
            "account_financial_report_lang": self.env.lang,
        }

    def _export(self, report_type):
        return self._print_report(report_type)
