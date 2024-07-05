{
    'name': 'Importar Padron de Alicuotas',
    'version': '1.0',
    'category': 'Accounting',
    'sequence': 15,
    'summary': 'Importar padron',
    'depends': [
        'base',
        'account',
        'l10n_ar_account_withholding',
    ],
    'data': [
        'security/ir.model.access.csv',

        'views/account_padron_import.xml',
        'views/account_padron.xml',
        'views/res_config_settings_views.xml',
    ],
    'demo': [
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
