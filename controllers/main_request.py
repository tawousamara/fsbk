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
import html
from odoo.tools import html2plaintext
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
        wilayas = request.env['res.country.state'].search([('country_id', '=', 62)])
        banques = request.env['crm.banque'].search([])
        pays_ids = request.env['res.country'].search([])
        payments = request.env['crm.payment.mode'].search([])
        payment_types = request.env['crm.type.payment'].search([])
        forme_juridiques = request.env['crm.forme.juridique'].search([])
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
            user = request.env.user.partner_id
            partner = request.env.user.partner_id.parent_id
            if not partner:
                vals = {
                    'street': user.street or '',
                    'company_name': user.company_name or '',
                    'branch': user.branch or '',
                    'website': user.website or '',
                    'phone': user.phone or '',
                    'email': user.email or '',
                    'secteur': user.secteur or '',
                    'activity': user.activity or '',
                }
                create_company = request.env.user.partner_id.update_company(vals)
                print('create_company', create_company)
                partner = request.env.user.partner_id.parent_id
                print('partner', partner)
        else:
            partner = False
        description = ''
        garanties = ''
        if opportunity_id != 0:
            opportunity = request.env['crm.lead'].browse(int(opportunity_id))
            description = html.unescape(
                html2plaintext(opportunity.company_description)) if opportunity.company_description else ''
            garanties = html.unescape(html2plaintext(opportunity.garanties)) if opportunity.garanties else ''
        else:
            opportunity = False
        values = {
            'step': opportunity.stage if opportunity else 'step1',
            'opportunity_id': opportunity_id if opportunity_id else 0,
            'demande_type': opportunity.demande_type if opportunity else '0',
            'street': partner.street or '',
            'state_id': partner.state_id or '',
            'forme_jur': partner.forme_jur or '',
            'representant': partner.representant or '',
            'company_name': partner.name or '',
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
            'wilayas': wilayas,
            'secteurs': secteurs,
            'activities': activities,
            'demandes': demandes,
            'banques': banques,
            'forme_juridiques': forme_juridiques,
            'document_list': Doc_List,
            'credits_type': credits_type,
            'has_confrere': opportunity.has_confrere if opportunity else False,
            'has_appro': opportunity.has_appro if opportunity else False,
            'has_importation': opportunity.has_importation if opportunity else False,
            'has_account': opportunity.has_account if opportunity else False,
            'num_compte': opportunity.num_compte if opportunity else '',
            'company_description': description,
            'garanties': garanties,
            'nbr_employees': opportunity.nbr_employees if opportunity else '',
            'date_debut': opportunity.date_debut if opportunity else '',
            'branch': opportunity.branch if opportunity else '',
            'confrere_ids': confrere_ids,
            'importation_ids': importation_ids,
            'appro_ids': appro_ids,
            'plan_ids': plan_ids,
            'financement_ids': financement_ids,
        }
        print(values['has_confrere'])
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

    @http.route('/credit-request/hasAccount', type='http', auth="public", website=True, csrf=True)
    def _hasAccount(self, **kwargs):
        opportunity_id = kwargs['opportunity_id']
        try:
            opportunity_id = int(kwargs.get('opportunity_id', 0))
            has_account = kwargs.get('hasAccount') == 'true'  # Convert string 'true'/'false' to boolean
            print('hasAccount', has_account)
            opportunity = request.env['crm.lead'].browse(opportunity_id)
            if opportunity.exists():
                opportunity.has_account = has_account
                return json.dumps({'success': True})
            else:
                return json.dumps({'success': False, 'error': 'Opportunity not found'})
        except Exception as e:
            return json.dumps({'success': False, 'error': str(e)})

    @http.route('/credit-request/hasConfrere', type='http', auth="public", website=True, csrf=True)
    def _hasConfrere(self, **kwargs):
        try:
            opportunity_id = int(kwargs.get('opportunity_id', 0))
            has_confrere = kwargs.get('hasConfrere') == 'true'  # Convert string 'true'/'false' to boolean
            print('hasConfrere', has_confrere)
            opportunity = request.env['crm.lead'].browse(opportunity_id)
            if opportunity.exists():
                opportunity.has_confrere = has_confrere
                return json.dumps({'success': True})
            else:
                return json.dumps({'success': False, 'error': 'Opportunity not found'})
        except Exception as e:
            return json.dumps({'success': False, 'error': str(e)})

    @http.route('/credit-request/hasImportation', type='http', auth="public", website=True, csrf=True)
    def _hasImportation(self, **kwargs):
        try:
            opportunity_id = int(kwargs.get('opportunity_id', 0))
            has_importation = kwargs.get('hasImportation') == 'true'  # Convert string 'true'/'false' to boolean
            print('hasImportation', has_importation)
            opportunity = request.env['crm.lead'].browse(opportunity_id)
            if opportunity.exists():
                opportunity.has_importation = has_importation
                return json.dumps({'success': True})
            else:
                return json.dumps({'success': False, 'error': 'Opportunity not found'})
        except Exception as e:
            return json.dumps({'success': False, 'error': str(e)})

    @http.route('/credit-request/hasAppro', type='http', auth="public", website=True, csrf=True)
    def _hasAppro(self, **kwargs):
        try:
            opportunity_id = int(kwargs.get('opportunity_id', 0))
            has_appro = kwargs.get('hasAppro') == 'true'  # Convert string 'true'/'false' to boolean
            print('hasAppro', has_appro)
            opportunity = request.env['crm.lead'].browse(opportunity_id)
            if opportunity.exists():
                opportunity.has_appro = has_appro
                return json.dumps({'success': True})
            else:
                return json.dumps({'success': False, 'error': 'Opportunity not found'})
        except Exception as e:
            return json.dumps({'success': False, 'error': str(e)})


    @http.route('/credit-request/numcompteChanged', type='http', auth="public", website=True, csrf=True)
    def _compteChanged(self, **kwargs):
        try:
            opportunity_id = int(kwargs.get('opportunity_id', 0))
            num_compte = kwargs.get('num_compte', 0)
            opportunity = request.env['crm.lead'].browse(opportunity_id)
            if opportunity.exists():
                opportunity.num_compte = num_compte
                return json.dumps({'success': True})
            else:
                return json.dumps({'success': False, 'error': 'Opportunity not found'})
        except Exception as e:
            return json.dumps({'success': False, 'error': str(e)})


    @http.route('/credit-request/companydescriptionChanged', type='http', auth="public", website=True, csrf=True)
    def _descriptionChanged(self, **kwargs):
        try:
            opportunity_id = int(kwargs.get('opportunity_id', 0))
            company_description = kwargs.get('company_description', 0)
            opportunity = request.env['crm.lead'].browse(opportunity_id)
            if opportunity.exists():
                opportunity.company_description = company_description
                return json.dumps({'success': True})
            else:
                return json.dumps({'success': False, 'error': 'Opportunity not found'})
        except Exception as e:
            return json.dumps({'success': False, 'error': str(e)})



    @http.route('/credit-request/garantiesChanged', type='http', auth="public", website=True, csrf=True)
    def _garantiesChanged(self, **kwargs):
        try:
            opportunity_id = int(kwargs.get('opportunity_id', 0))
            garanties = kwargs.get('garanties', 0)
            opportunity = request.env['crm.lead'].browse(opportunity_id)
            if opportunity.exists():
                opportunity.garanties = garanties
                return json.dumps({'success': True})
            else:
                return json.dumps({'success': False, 'error': 'Opportunity not found'})
        except Exception as e:
            return json.dumps({'success': False, 'error': str(e)})


    @http.route('/credit-request/nbremployeesChanged', type='http', auth="public", website=True, csrf=True)
    def _employeeChanged(self, **kwargs):
        try:
            opportunity_id = int(kwargs.get('opportunity_id', 0))
            nbr_employees = int(kwargs.get('nbr_employees', 0))
            opportunity = request.env['crm.lead'].browse(opportunity_id)
            if opportunity.exists():
                opportunity.nbr_employees = nbr_employees
                return json.dumps({'success': True})
            else:
                return json.dumps({'success': False, 'error': 'Opportunity not found'})
        except Exception as e:
            return json.dumps({'success': False, 'error': str(e)})

    @http.route('/credit-request/branchChanged', type='http', auth="public", website=True, csrf=True)
    def _branchChanged(self, **kwargs):
        try:
            opportunity_id = int(kwargs.get('opportunity_id', 0))
            branch = int(kwargs.get('branch', 0))
            opportunity = request.env['crm.lead'].browse(opportunity_id)
            if opportunity.exists():
                opportunity.branch = branch
                return json.dumps({'success': True})
            else:
                return json.dumps({'success': False, 'error': 'Opportunity not found'})
        except Exception as e:
            return json.dumps({'success': False, 'error': str(e)})


    @http.route('/credit-request/datedebutChanged', type='http', auth="public", website=True, csrf=True)
    def _datedebutChanged(self, **kwargs):
        try:
            opportunity_id = int(kwargs.get('opportunity_id', 0))
            date_debut = kwargs.get('date_debut', '')
            opportunity = request.env['crm.lead'].browse(opportunity_id)
            if opportunity.exists():
                opportunity.write({'date_debut': date_debut})
                return json.dumps({'success': True})
            else:
                return json.dumps({'success': False, 'error': 'Opportunity not found'})
        except Exception as e:
            return json.dumps({'success': False, 'error': str(e)})

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
                post['name'] = post['company_name']
                forme_jur = post['forme_jur']
                representant = post['representant']
                if post['demande_type'] == '1':
                    post['name'] = 'Renouvellement ' + post['company_name']
                    post['type'] = 'opportunity'
                post['partner_name'] = post['company_name']

                print(post)
                post.pop('company_name')
                opportunity = request.env['crm.lead'].sudo().create(post)
                vals = {
                    'street': post['street'] or '',
                    'state_id': post['state_id'] or '',
                    'company_name': post['partner_name'] or '',
                    'website': post['website'] or '',
                    'phone': post['phone'] or '',
                    'email': post['email_from'] or '',
                    'secteur': post['secteur'] or '',
                    'activity': post['activity'] or '',
                    'representant': representant,
                    'forme_jur': forme_jur,
                }
                partner = request.env.user.partner_id
                partner.update_company(vals)
                partner.write(vals)
                opportunity.partner_id = partner.parent_id
            opportunity.write({
                'stage': 'step2'
            })
        elif step == 'step2':
            if 'confrere_file' in post:
                post['confrere_file'] = base64.b64encode(post['confrere_file'].read())
            if 'importation_file' in post:
                post['importation_file'] = base64.b64encode(post['importation_file'].read())
            if 'appro_file' in post:
                post['appro_file'] = base64.b64encode(post['appro_file'].read())
            if 'plan_file' in post:
                post['plan_file'] = base64.b64encode(post['plan_file'].read())
            post['stage'] = 'step3'
            post.pop('opportunity_id')
            post.pop('step')
            opportunity.write(post)
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
        if not opportunity.has_confrere:
            opportunity.has_confrere = True
        return request.redirect('/credit-request?opportunity_id=%d&step=%s#confrere_section' % (opportunity_id, opportunity.stage))

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
        if not opportunity.has_importation:
            opportunity.has_importation = True
        return request.redirect('/credit-request?opportunity_id=%d&step=%s#import_section' % (opportunity_id, opportunity.stage))

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
        if not opportunity.has_appro:
            opportunity.has_appro = True
        return request.redirect('/credit-request?opportunity_id=%d&step=%s#appro_section' % (opportunity_id, opportunity.stage))

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
        return request.redirect('/credit-request?opportunity_id=%d&step=%s#plan_section' % (opportunity_id, opportunity.stage))
    



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
        return request.redirect('/credit-request?opportunity_id=%d&step=%s#finance_section' % (opportunity_id, opportunity.stage))
    


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
            return request.redirect('/credit-request?opportunity_id=%d&step=%s#confrere_section' % (opportunity_id, opportunity.stage))
        except Exception as e:
            _logger.error("Erreur lors de la suppression du confrere: %s", str(e))
            return request.redirect('/credit-request?opportunity_id=%d&step=%s&error=delete_failed#confrere_section' % (opportunity_id, step))
        

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
            return request.redirect('/credit-request?opportunity_id=%d&step=%s#import_section' % (opportunity_id, opportunity.stage))
        except Exception as e:
            _logger.error(f"Erreur lors de la suppression de l'importation: {str(e)}")
            return request.redirect('/credit-request?opportunity_id=%d&step=%s&error=delete_failed#import_section' % (opportunity_id, step))

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
            return request.redirect('/credit-request?opportunity_id=%d&step=%s#appro_section' % (opportunity_id, opportunity.stage))
        except Exception as e:
            _logger.error(f"Erreur lors de la suppression de l'approvisionnement: {str(e)}")
            return request.redirect('/credit-request?opportunity_id=%d&step=%s&error=delete_failed#appro_section' % (opportunity_id, step))


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
            return request.redirect('/credit-request?opportunity_id=%d&step=%s#plan_section' % (opportunity_id, opportunity.stage))
        except Exception as e:
            _logger.error(f"Erreur lors de la suppression du plan: {str(e)}")
            return request.redirect('/credit-request?opportunity_id=%d&step=%s&error=delete_failed#plan_section' % (opportunity_id, step))

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
            return request.redirect('/credit-request?opportunity_id=%d&step=%s#finance_section' % (opportunity_id, opportunity.stage))
        except Exception as e:
            _logger.error(f"Erreur lors de la suppression du financement: {str(e)}")
            return request.redirect('/credit-request?opportunity_id=%d&step=%s&error=delete_failed#finance_section' % (opportunity_id, step))

    

    

def create_random_password():
    characters = string.ascii_letters + string.digits
    password = ""
    for i in range(8):
        randomchar = random.choice(characters)

        password += randomchar
    return password
