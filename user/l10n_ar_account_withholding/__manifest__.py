{
    'name': 'Contabilidad Extendida - Argentina',
    'version': '1.0',
    'category': 'Accounting',
    'sequence': 15,
    'summary': 'Contabilidad Extendida - Argentina',
    'depends': [
        'base',
        'account',
    ],
    'data': [
        'security/ir.model.access.csv',

        'views/res.partner.xml',
        'views/arba_alicuot.xml'
    ],
    'demo': [
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
