# Copyright 2022 Lucas Avila
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Importar Faturas",
    "description": """Importar Faturas""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "Lucas Avila",
    "depends": [
            "base", 
            "l10n_br_nfe",
            "l10n_br_purchase",
            "l10n_br_stock_account", 
        ],
    "data": [
        "security/ir.model.access.csv",
        "wizard/purchase_order.xml",
        "wizard/account_import_nfe.xml",
        "views/l10n_br_layout.xml",
    ],
    "demo": [],
    "sequence": 5,
    "application": True,
}
