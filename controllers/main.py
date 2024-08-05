import datetime

from odoo import models, fields, api, _

from odoo import http
from odoo.http import request
import json
import string
import random
import base64
import datetime

class CreditRequest(http.Controller):

    @http.route('/funding-request', type='http', auth="public", website=True, csrf=True)
    def demande_form(self, **kwargs):
        activities = request.env['crm.activity'].search([])
        secteurs = request.env['crm.secteur'].search([])
        branches = request.env['crm.branch'].search([])
        demandes = [('0', 'Entrer en relation'),
                    ('1', 'Renouvellement'),
                    ('2', 'Ponctuel'),
                    ]
        products = [('0', 'Exploitation'),
                    ('1', 'Investissement'),
                    ('2', 'Leasing')]
        values = {
            'products': products,
            'branches': branches,
            'secteurs': secteurs,
            'activities': activities,
            'demandes': demandes
        }
        return request.render("crm_portal.create_funding_request", values)

    @http.route('/funding-request/getActivities', type='http', auth="public", website=True, csrf=True)
    def _getActivities(self, **kwargs):
        print('*******************heeeereeee1111******************')
        print(kwargs)
        secteur_id = kwargs['secteur_id']
        activities = request.env['crm.activity'].search([('secteur', '=', int(secteur_id))])
        activities_list = []
        for act in activities:
            activities_list.append((act.id, act.name))
        return json.dumps(dict(activities_list))

    @http.route(['/create/funding', '/demande-thank-you'], type='http', auth="public", website=True)
    def create_webscoring(self, **kwargs):
        print(kwargs)
        #kwargs['password'] = create_random_password()
        kwargs['name'] = 'Demande ' + kwargs['partner_name']
        kwargs['file_tcr'] = base64.b64encode(kwargs['file_tcr'].read())
        kwargs['file_tcr1'] = base64.b64encode(kwargs['file_tcr1'].read())
        kwargs['file_actif'] = base64.b64encode(kwargs['file_actif'].read())
        kwargs['file_passif'] = base64.b64encode(kwargs['file_passif'].read())
        request_created = request.env['crm.lead'].sudo().create(kwargs)
        print(request_created)
        passif_id = request.env['import.ocr.passif'].create({'date': datetime.datetime.today(),
                                                             'file_import': kwargs['file_passif']})
        actif_id = request.env['import.ocr.actif'].create({'date': datetime.datetime.today(),
                                                           'file_import': kwargs['file_actif']})
        tcr_id = request.env['import.ocr.tcr'].create({'date': datetime.datetime.today(),
                                                       'file_import': kwargs['file_tcr'],
                                                       'file_import2': kwargs['file_tcr1']})
        request_created.tcr_id = tcr_id
        request_created.actif_id = actif_id
        request_created.passif_id = passif_id

        return request.render("crm_portal.request_thanks", {})


    @http.route('/funding-request/getProducts', type='http', auth="public", website=True, csrf=True)
    def _getProducts(self, **kwargs):
        print('*******************heeeereeee1111******************')
        activities = request.env['crm.product'].search([])
        activities_list = []
        for act in activities:
            activities_list.append((act.id, act.name))
        print(activities_list)
        value = json.dumps(dict(activities_list))
        print(value)
        return json.dumps(dict(activities_list))


def create_random_password():
    characters = string.ascii_letters + string.digits
    password = ""
    for i in range(8):
        randomchar = random.choice(characters)

        password += randomchar
    return password
