#
#    Copyright © 2021–; Brasil; IT Brasil; Todos os direitos reservados
#    Copyright © 2021–; Brazil; IT Brasil; All rights reserved
#

{
    'name': "Aviso Prévio: Data de Expiração",
    'license': 'Other proprietary',
    'author': 'IT Brasil',
    'website': 'https://www.itbrasil.com.br',
    'category': 'Extra Tools',
    'summary': 'Exibe uma notificação prévia de vencimento ao confirmar uma fatura durante os 30 dias anteriores a data de expiração do certificado.',
    'depends': ['l10n_br_fiscal','account'],
    'qweb': [],
    'data': [
		'security/ir_model_acess_wizard_certificate_message.xml',
		'wizard/wizard_certificate_message_views.xml',
	],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}
