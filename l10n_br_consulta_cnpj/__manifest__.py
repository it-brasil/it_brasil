# Copyright (C) 2022 - TODAY Renan Teixeira - IT Brasil / Danimar - Trust Code
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    "name": "Consulta CNPJ no SEFAZ",
    "summary": "Consulta na base do SEFAZ os dados cadastrais das empresas que possuem Inscrição Estadual",
    "category": "Localization",
    "license": "AGPL-3",
    "author": "IT Brasil",
    "maintainers": ["renanteixeira", "it-brasil"],
    "website": "https://github.com/it-brasil/it_brasil",
    "version": "14.0.1.1.0",
    "depends": ["l10n_br_base"],
    "data": [
        'views/res_partner.xml'
    ],
    "demo": [],
    "installable": True,
    "development_status": "Beta",
    "external_dependencies": {"python": ["pytrustnfe3"]},
}
