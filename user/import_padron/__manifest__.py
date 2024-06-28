{
    'name': 'Importar Padron de Alicuotas',
    'version': '1.0',
    'category': 'Accounting',
    'sequence': 15,
    'summary': 'Importar padron',
    'depends': [
        'base',
        'account',
    ],
    'data': [
        'security/ir.model.access.csv',

        'views/account_padron_import.xml',
    ],
    'demo': [
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
