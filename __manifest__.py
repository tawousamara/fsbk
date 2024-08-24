# -*- coding: utf-8 -*-
{
    'name': "Portal CRM",
    'sequence': 0,
    'summary': """""",

    'description': """
        Ce module introduit de nouveaux champs dans le modèle res.partner, customization de nouveaux rapports""",

    'author': "FINOUTSOURCE",
    'website': "",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'website', 'crm', 'financial_modeling'],

    # always loaded
    'data': [
        'data/bank_list.xml',
        'data/data_list.xml',
        'data/wilaya_data.xml',
        'security/ir.model.access.csv',
        'security/security.xml',
        #'views/portal_page.xml',
        'views/request_page.xml',
        'views/lead_inherit.xml',
        'views/partner_inherit.xml',
        'views/configuration.xml',
    ],
    'assets': {
            'web.assets_frontend':[
                'crm_portal/static/src/js/controller_js.js',
            ],
        'web.assets_backend': [
            'crm_portal/static/src/css/custom_styles.css',
        ],
        },

    'application': True,
    'license': 'LGPL-3',
}
