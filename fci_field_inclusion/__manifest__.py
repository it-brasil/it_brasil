# Copyright 2022 IT Brasil ((https://www.itbrasil.com.br).)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': "Inclusão do campo FCI",
    'license': 'Other proprietary',
    'author': 'IT Brasil',
    'website': 'https://www.itbrasil.com.br',
    'category': 'Extra Tools',
    'summary': 'Inclui o campo FCI no cadastro de produto, fatura e documentos fiscais',
    'depends': ['l10n_br_fiscal','l10n_br_nfe','l10n_br_account','sale_management'],
    'qweb': [],
    'data': [
		#'views/account_move_views.xml',
        #'views/l10n_br_account_fiscal_invoice_form_views.xml',
        'views/l10n_br_fiscal_document_views.xml',
        'views/l10n_br_fiscal_product_product_views.xml',
		'views/product_template_views.xml',
		#'views/sale_order_views.xml',
	],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}
