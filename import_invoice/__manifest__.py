# Copyright 2022 Lucas Avila
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Importar Faturas",
    "description": """Importar Faturas""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "Lucas Avila",
    "depends": ["base", "purchase", "account", "l10n_br"],
    "data": [
        "security/ir.model.access.csv",
        "views/purchase_order.xml"
    ],
    "demo": [],
    "sequence": 5,
    "application": True,
}
