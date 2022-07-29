from odoo import _, fields, models


class Cnae(models.Model):
    _name = "cnae.cnpj"
    _inherit = "cnpj.data.abstract"
    _description = "CNAE"

    code = fields.Char(size=16)

    version = fields.Char(string="Version", size=16, required=True)

    parent_id = fields.Many2one(
        comodel_name="cnae.cnpj", string="Parent CNAE"
    )

    child_ids = fields.One2many(
        comodel_name="cnae.cnpj",
        inverse_name="parent_id",
        string="Children CNAEs",
    )

    internal_type = fields.Selection(
        selection=[("view", "View"), ("normal", "Normal")],
        string="Internal Type",
        required=True,
        default="normal",
    )

    _sql_constraints = [
        (
            "cnae_cnpj_code_uniq",
            "unique (code)",
            _("CNAE already exists with this code !"),
        )
    ]