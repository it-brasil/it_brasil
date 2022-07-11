# See LICENSE file for full copyright and licensing details.

{
    'name': 'Partner Credit',
    'version': '14.0.2.0.0',
    'category': 'Partner',
    'license': 'AGPL-3',
    'author': 'Carlos, ATSTi Soluções, João Bernardes, Renan Teixeira (IT Brasil)',
    'website': 'https://itbrasil.com.br',
    'summary': 'Limite de crédito com regras avançadas',
    'depends': [
        'stock', 'sale_management', 'account_followup'
    ],
    'data': [
        #data
        'data/mail_activity_data.xml',
        #security
        'security/res_groups_data.xml',
        #views
        'views/partner_view.xml',
        'views/sale_order_views.xml',
        'views/stock_picking_views.xml',
        'views/account_payment_views.xml',
    ],
    'installable': True,
    'auto_install': False,
}
