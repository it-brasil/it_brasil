# See LICENSE file for full copyright and licensing details.

{
    'name': 'Partner Credit Limit Stock',
    'version': '14.0.1.0.0',
    'category': 'Partner',
    'license': 'AGPL-3',
    'author': 'Carlos, ATSTi Soluções e João Bernardes (IT Brasil)',
    'website': 'http://www.atsti.com.br',
    'summary': 'Estabelece limite de crédito para aprovar Entregas',
    'depends': [
        'stock', 'sale_management'
    ],
    'data': [
        #security
        'security/res_groups_data.xml',
        #views
        'views/partner_view.xml',
        'views/sale_order_views.xml',
        'views/stock_picking_views.xml',
    ],
    'installable': True,
    'auto_install': False,
}
