import datetime

from odoo import models, fields, api, _

from odoo import http
from odoo.http import request
import json
import string
import random
import base64
import datetime
import logging

Doc_List = [
    ('1', 'Bilans fiscal N, N-1'),
    ('2', 'Bilan fiscal N-2'),
    ('3', 'Registre de commerce'),
    ('4', 'NIF'),
    ('5', 'NIS'),
    ('6', 'Statut de création'),
    ('7', 'Dernier statut modificatif'),
    ('8', 'Contrat de location / acte de propriété du siège social'),
    ('9', 'Autorisation de consultation CDR'),
]
_logger = logging.getLogger(__name__)


class CreditReq(http.Controller):

    @http.route('/credit-request', type='http', auth="user", website=True, csrf=True)
    def demande_form(self, **kwargs):
        _logger.info('Form submitted with data: %s', kwargs)
        print(kwargs)
        # Store the data in the session
        request.session['form_data'] = kwargs
        step = kwargs.get('step', 'step1')
        demande_type = kwargs.get('demande_type', '0')
        opportunity_id = kwargs.get('opportunity_id', 0)
        print(opportunity_id)
        activities = request.env['crm.activity'].search([])
        secteurs = request.env['crm.secteur'].search([])
        branches = request.env['crm.branch'].search([])
        banques = request.env['crm.banque'].search([])
        pays_ids = request.env['res.country'].search([])
        payments = request.env['crm.payment.mode'].search([])
        payment_types = request.env['crm.type.payment'].search([])
        fin_types = request.env['crm.type.financement'].search([])
        type_marches = request.env['crm.type.marche'].search([])
        credits_type = request.env['crm.product'].search([])
        confrere_ids = request.env['crm.confrere'].search([('lead_id', '=', int(opportunity_id))])
        importation_ids = request.env['crm.importation'].search([('lead_id', '=', int(opportunity_id))])
        appro_ids = request.env['crm.appro'].search([('lead_id', '=', int(opportunity_id))])
        plan_ids = request.env['crm.plan'].search([('lead_id', '=', int(opportunity_id))])
        financement_ids = request.env['crm.financement'].search([('lead_id', '=', int(opportunity_id))])
        demandes = [('0', 'Entrer en relation (nouvelle demande)'),
                    ('1', 'Renouvellement des lignes')
                    ]
        if request.env.user:
            partner = request.env.user.partner_id.parent_id
            if not partner:
                create_company = request.env.user.partner_id.create_company()
                print('create_company', create_company)
                partner = request.env.user.partner_id.parent_id
                print('partner', partner)
        else:
            partner = False

        if opportunity_id != 0:
            opportunity = request.env['crm.lead'].browse(int(opportunity_id))

        else:
            opportunity = False

        values = {
            'step': opportunity.stage if opportunity else 'step1',
            'opportunity_id': opportunity_id if opportunity_id else 0,
            'demande_type': opportunity.demande_type if opportunity else '0',
            'street': partner.street or '',
            'partner_name': partner.name or '',
            'branch': partner.branch or '',
            'web_site': partner.website or '',
            'phone': partner.phone or '',
            'email_from': partner.email or '',
            'secteur': partner.secteur or '',
            'activity': partner.activity or '',
            'payment_types': payment_types,
            'fin_types': fin_types,
            'type_marches': type_marches,
            'payments': payments,
            'answers': [('oui', 'Oui'),
                        ('non', 'Non')],
            'pays_ids': pays_ids,
            'branches': branches,
            'secteurs': secteurs,
            'activities': activities,
            'demandes': demandes,
            'banques': banques,
            'document_list': Doc_List,
            'credits_type': credits_type,
            'confrere_ids': confrere_ids,
            'importation_ids': importation_ids,
            'appro_ids': appro_ids,
            'plan_ids': plan_ids,
            'financement_ids': financement_ids,
        }
        return request.render("crm_portal.create_credit_request", values)

    @http.route('/credit-request/getActivities', type='http', auth="public", website=True, csrf=True)
    def _getActivities(self, **kwargs):
        print('*******************heeeereeee1111******************')
        print(kwargs)
        secteur_id = kwargs['secteur_id']
        activities = request.env['crm.activity'].search([('secteur', '=', int(secteur_id))])
        activities_list = []
        for act in activities:
            activities_list.append((act.id, act.name))
        return json.dumps(dict(activities_list))


    @http.route('/create/request', type='http', auth='user', methods=['POST'], website=True, csrf=True)
    def opportunity_submit(self, **post):
        # Handle form submission and move to the next step
        print(post)
        opportunity_id = post.get('opportunity_id', 0)
        step = post.get('step', 'step1')
        if opportunity_id:
            opportunity = request.env['crm.lead'].browse(int(opportunity_id))
        else:
            opportunity = False
        if step == 'step1':
            if not opportunity:
                post['stage'] = post.get('step')
                print(post['step'])
                post.pop('step')
                post.pop('opportunity_id')
                post['name'] = post['partner_name']
                if post['demande_type'] == '1':
                    post['name'] = 'Renouvellement ' + post['partner_name']
                    post['type'] = 'opportunity'
                opportunity = request.env['crm.lead'].create(post)
            opportunity.write({
                'stage': 'step2'
            })
        elif step == 'step2':
            opportunity.write({
                'stage': 'step3'
            })
        else:
            documents = []
            document_dict = {item[0]: item[1] for item in Doc_List}
            # Parcourir toutes les clés dans 'post'
            for key, value in post.items():
                if key.startswith('document_'):
                    try:
                        # Extraire l'ID de la clé
                        document_id = int(key.split('_')[1])
                        file = value
                        documents.append({'lead_id': opportunity.id,
                                                 'list_doc':  str(document_id),
                                                 'datas': base64.b64encode(file.read()) if file else False,
                                                  'create_uid': request.env.user,
                                                  'name': document_dict.get(str(document_id), '')})


                    except ValueError:
                        continue
            if documents:
                # Créer les enregistrements dans le modèle cible
                if not opportunity.document_ids:
                    request.env['ir.attachment'].create(documents)
                else:
                    for doc in documents:
                        exist_doc = opportunity.document_ids.filtered(lambda l: l.name == doc['list_doc'])
                        exist_doc.write(doc)
            opportunity.write({
                'stage': 'step4'
            })
        return request.redirect('/credit-request?opportunity_id=%d&step=%s&demande_type=%s' % (opportunity.id,
                                                                                               opportunity.stage,
                                                                                               opportunity.demande_type))

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

    @http.route('/create/confrere', type='http', auth='user', methods=['POST'], website=True, csrf=True)
    def create_confrere(self, **post):
        print('hoo')
        # Handle form submission and move to the next step
        opportunity_id = int(post.get('opportunity_id', 0))
        step = post.get('step', 'step1')
        post['lead_id'] = opportunity_id  # Ensure that the opportunity ID is correctly set
        vals = post
        vals.pop('opportunity_id')
        vals.pop('step')
        apropos_line = request.env['crm.confrere'].create(vals)
        opportunity = request.env['crm.lead'].browse(int(opportunity_id))
        return request.redirect('/credit-request?opportunity_id=%d&step=%s' % (opportunity_id, opportunity.stage))

    @http.route('/create/importation', type='http', auth='user', methods=['POST'], website=True, csrf=True)
    def create_importation(self, **post):
        print('hoo')
        # Handle form submission and move to the next step
        opportunity_id = int(post.get('opportunity_id', 0))
        step = post.get('step', 'step1')
        post['lead_id'] = opportunity_id  # Ensure that the opportunity ID is correctly set
        vals = post
        selected_garanties = post.get('payment')

        selected_garanties = []
        delete_keys = []
        for key, value in post.items():
            if key.startswith('payment_'):
                try:
                    # Extraire l'ID de la clé
                    delete_keys.append(key)
                    garantie_id = int(key.split('_')[1])
                    selected_garanties.append(garantie_id)
                except ValueError:
                    # Ignorer les clés qui ne peuvent pas être converties en entier
                    continue
        for item in delete_keys:
            vals.pop(item)
        if selected_garanties:
            vals['payment'] = [(6, 0, selected_garanties)]
        vals.pop('opportunity_id')
        vals.pop('step')
        print(type(vals['programme_importation']))
        vals['programme_importation'] = vals['programme_importation']+ '-01'
        apropos_line = request.env['crm.importation'].create(vals)
        opportunity = request.env['crm.lead'].browse(int(opportunity_id))
        return request.redirect('/credit-request?opportunity_id=%d&step=%s' % (opportunity_id, opportunity.stage))

    @http.route('/create/appro', type='http', auth='user', methods=['POST'], website=True, csrf=True)
    def create_appro(self, **post):
        print('hoo')
        # Handle form submission and move to the next step
        opportunity_id = int(post.get('opportunity_id', 0))
        step = post.get('step', 'step1')
        post['lead_id'] = opportunity_id  # Ensure that the opportunity ID is correctly set
        vals = post
        selected_garanties = post.get('payment')

        selected_garanties = []
        delete_keys = []
        for key, value in post.items():
            if key.startswith('payment_'):
                try:
                    # Extraire l'ID de la clé
                    delete_keys.append(key)
                    garantie_id = int(key.split('_')[1])
                    selected_garanties.append(garantie_id)
                except ValueError:
                    # Ignorer les clés qui ne peuvent pas être converties en entier
                    continue
        for item in delete_keys:
            vals.pop(item)
        if selected_garanties:
            vals['payment'] = [(6, 0, selected_garanties)]
        vals.pop('opportunity_id')
        vals.pop('step')
        print(type(vals['programme_importation']))
        vals['programme_importation'] = vals['programme_importation']+ '-01'
        apropos_line = request.env['crm.appro'].create(vals)
        opportunity = request.env['crm.lead'].browse(int(opportunity_id))
        return request.redirect('/credit-request?opportunity_id=%d&step=%s' % (opportunity_id, opportunity.stage))

    @http.route('/create/plan', type='http', auth='user', methods=['POST'], website=True, csrf=True)
    def create_plan(self, **post):
        # Handle form submission and move to the next step
        opportunity_id = int(post.get('opportunity_id', 0))
        step = post.get('step', 'step1')
        post['lead_id'] = opportunity_id  # Ensure that the opportunity ID is correctly set
        vals = post
        vals.pop('opportunity_id')
        vals.pop('step')
        apropos_line = request.env['crm.plan'].create(vals)
        opportunity = request.env['crm.lead'].browse(int(opportunity_id))
        return request.redirect('/credit-request?opportunity_id=%d&step=%s' % (opportunity_id, opportunity.stage))
    



    @http.route('/create/financement', type='http', auth='user', methods=['POST'], website=True, csrf=True)
    def create_financement(self, **post):
        # Handle form submission and move to the next step
        opportunity_id = int(post.get('opportunity_id', 0))
        step = post.get('step', 'step1')
        post['lead_id'] = opportunity_id  # Ensure that the opportunity ID is correctly set
        vals = post
        vals.pop('opportunity_id')
        vals.pop('step')
        apropos_line = request.env['crm.financement'].create(vals)
        opportunity = request.env['crm.lead'].browse(int(opportunity_id))
        return request.redirect('/credit-request?opportunity_id=%d&step=%s' % (opportunity_id, opportunity.stage))
    


    @http.route('/delete_imp', type='http', auth='user', website=True, methods=['POST'], csrf=True)
    def delete_confrere(self, **post):
       
        _logger.info('----------here-----------------')
        
        return request.redirect('/credit-request')
    

    @http.route('/delete/confrere', type='http', auth='user', website=True, methods=['POST'], csrf=True)
    def delete_confrere(self, **post):
        _logger.info('access done')
        confrere_id = post.get('confrere_id')
        opportunity_id = int(post.get('opportunity_id'))
        opportunity = request.env['crm.lead'].browse(opportunity_id)

        _logger.info(confrere_id)
        step = post.get('step')
        
        try:
            confrere = request.env['crm.confrere'].browse(int(confrere_id))
            if confrere.exists():
                confrere.unlink()
            return request.redirect('/credit-request?opportunity_id=%d&step=%s' % (opportunity_id, opportunity.stage))
        except Exception as e:
            _logger.error("Erreur lors de la suppression du confrere: %s", str(e))
            return request.redirect('/credit-request?opportunity_id=%d&step=%s&error=delete_failed' % (opportunity_id, step))
        

    @http.route('/delete_importation', type='http', auth='user', website=True, methods=['POST'], csrf=True)
    def delete_importation(self, **post):
        _logger.info('Suppression importation accédée')
        importation_id = post.get('importation_id')
        opportunity_id = int(post.get('opportunity_id'))
        opportunity = request.env['crm.lead'].browse(opportunity_id)

        _logger.info(f"ID Importation à supprimer: {importation_id}")
        step = post.get('step')
        
        try:
            importation = request.env['crm.importation'].browse(int(importation_id))
            if importation.exists():
                importation.unlink()
            return request.redirect('/credit-request?opportunity_id=%d&step=%s' % (opportunity_id, opportunity.stage))
        except Exception as e:
            _logger.error(f"Erreur lors de la suppression de l'importation: {str(e)}")
            return request.redirect('/credit-request?opportunity_id=%d&step=%s&error=delete_failed' % (opportunity_id, step))

    @http.route('/delete_appro', type='http', auth='user', website=True, methods=['POST'], csrf=True)
    def delete_appro(self, **post):
        appro_id = post.get('appro_id')
        opportunity_id = int(post.get('opportunity_id'))
        opportunity = request.env['crm.lead'].browse(opportunity_id)
        step = post.get('step')
        
        try:
            appro = request.env['crm.appro'].browse(int(appro_id))
            if appro.exists():
                appro.unlink()
            return request.redirect('/credit-request?opportunity_id=%d&step=%s' % (opportunity_id, opportunity.stage))
        except Exception as e:
            _logger.error(f"Erreur lors de la suppression de l'approvisionnement: {str(e)}")
            return request.redirect('/credit-request?opportunity_id=%d&step=%s&error=delete_failed' % (opportunity_id, step))


    @http.route('/delete_plan', type='http', auth='user', website=True, methods=['POST'], csrf=True)
    def delete_plan(self, **post):
        plan_id = post.get('plan_id')
        opportunity_id = int(post.get('opportunity_id'))
        opportunity = request.env['crm.lead'].browse(opportunity_id)
        step = post.get('step')
        
        try:
            plan = request.env['crm.plan'].browse(int(plan_id))
            if plan.exists():
                plan.unlink()
            return request.redirect('/credit-request?opportunity_id=%d&step=%s' % (opportunity_id, opportunity.stage))
        except Exception as e:
            _logger.error(f"Erreur lors de la suppression du plan: {str(e)}")
            return request.redirect('/credit-request?opportunity_id=%d&step=%s&error=delete_failed' % (opportunity_id, step))

    @http.route('/delete_financement', type='http', auth='user', website=True, methods=['POST'], csrf=True)
    def delete_financement(self, **post):
        _logger.info("Route /delete_financement appelée avec post: %s", post)
        financement_id = post.get('financement_id')
        opportunity_id = int(post.get('opportunity_id'))
        opportunity = request.env['crm.lead'].browse(opportunity_id)
        step = post.get('step')
        
        try:
            financement = request.env['crm.financement'].browse(int(financement_id))
            if financement.exists():
                financement.unlink()
            return request.redirect('/credit-request?opportunity_id=%d&step=%s' % (opportunity_id, opportunity.stage))
        except Exception as e:
            _logger.error(f"Erreur lors de la suppression du financement: {str(e)}")
            return request.redirect('/credit-request?opportunity_id=%d&step=%s&error=delete_failed' % (opportunity_id, step))

    

    

def create_random_password():
    characters = string.ascii_letters + string.digits
    password = ""
    for i in range(8):
        randomchar = random.choice(characters)

        password += randomchar
    return password
