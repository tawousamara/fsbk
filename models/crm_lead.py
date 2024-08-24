from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from io import BytesIO
import numpy as np
import matplotlib
import base64
import json

from odoo.exceptions import UserError

matplotlib.use('Agg')
from matplotlib import pyplot as plt

list_ratio = [

    ('1', 'CA'),
    ('2', 'EBE'),
    ('3', 'EBE%'),
    ('4', 'RNC'),
    ('5', 'RNC%'),
    ('6', 'CAF'),
    ('7', 'CAF%'),
    ('8', 'Client en jours de CA'),
    ('9', 'Stock en jours d`achat'),
    ('10', 'Founisseur en jours de CA'),
    ('11', 'BFR'),
    ('12', 'BFR en jours de CA'),
    ('13', 'Endettement / TB'),
    ('14', 'FP / TB'),
]

type_name = {
    'eer_exploitation': 'EER Exploitation',
    'eer_investment': 'EER Investisement',
    'eer_mix': 'EER Mixte',
    'eer_saving': 'EER Epargne',
    'eer_credit_saving': 'EER Crédit/épargne'
}

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

class Lead(models.Model):
    _inherit = 'crm.lead'

    nrc = fields.Char(string='N.RC')
    nif = fields.Char(string='NIF')
    nis = fields.Char(string='NIS')
    date_creation = fields.Date(string='Date de création')
    branch = fields.Many2one('fsbk.branch', string='Agence')
    secteur = fields.Many2one('fsbk.secteur', string='Secteur d\'activité')
    activity = fields.Many2one('fsbk.activity', string='Activité en détails')
    demande_type = fields.Selection([('0', 'Entrer en relation (nouvelle demande)'),
                                     ('1', 'Renouvellement des lignes')], string='Type de demande')
    product = fields.Selection([('0', 'Exploitation'),
                                ('1', 'Investissement'),
                                ('2', 'Leasing')], string='Type de ligne de credit')
    product_ids = fields.Many2many('fsbk.product', string='Lignes de credit')
    num_compte = fields.Char(string='N. Compte')
    montant_sollicite = fields.Float(string='Montant sollicité')
    file_tcr = fields.Binary(string='TCR N, N-1')
    file_tcr1 = fields.Binary(string='TCR N, N-1')
    file_actif = fields.Binary(string='Actif N, N-1')
    file_passif = fields.Binary(string='Passif N, N-1')
    tcr_id = fields.Many2one('import.ocr.tcr', 'TCR N ET N-1')
    passif_id = fields.Many2one('import.ocr.passif', 'Passif N ET N-1')
    actif_id = fields.Many2one('import.ocr.actif', 'Actif N ET N-1')

    tcr1_id = fields.Many2one('import.ocr.tcr', string='TCR N-2 ET N-3')
    passif1_id = fields.Many2one('import.ocr.passif', string='Passif N-2 ET N-3')
    actif1_id = fields.Many2one('import.ocr.actif', string='Actif N-2 ET N-3')


    ratio_ids = fields.One2many('crm.ratio', 'lead', 'Ratio')
    visualisation = fields.Binary()

    resultat = fields.Float(string='Resultat Scoring')
    stage = fields.Selection([
        ('step1', 'Step 1'),
        ('step2', 'Step 2'),
        ('step3', 'Step 3'),
        ('step4', 'Step 4')], string='Stage', default='step1')


    # new relation
    has_account = fields.Boolean(string='Vous avez un compte?')
    rib = fields.Char(string='RIB')
    company_description = fields.Html(string='Description de votre activité')
    nbr_employees = fields.Integer(string='Nombre de salariés')
    date_debut = fields.Date(string='Date de début d`activité')
    has_confrere = fields.Boolean(string='Avez-vous des crédit bancaire auprès des confrères ?')
    confrere_ids = fields.One2many('fsbk.confrere', 'lead_id', string='Confrere')
    has_importation = fields.Boolean(string='Faites-vous de l`importation ?')
    importation_ids = fields.One2many('fsbk.importation', 'lead_id')
    has_appro = fields.Boolean(string='Approvisionnement auprès du marché local')
    appro_ids = fields.One2many('fsbk.appro', 'lead_id')
    plan_ids = fields.One2many('fsbk.plan', 'lead_id')
    financement_ids = fields.One2many('fsbk.financement', 'lead_id')
    document_ids = fields.One2many('ir.attachment', 'lead_id')

    garanties = fields.Html(string='Garanties proposées')
    geographic_area = fields.Selection([('center', 'Centre'),
                                        ('east', 'Est'),
                                        ('west', 'Ouest')], string="Zone géographique")
    turnover = fields.Monetary("Chiffre d'affaire", currency_field='company_currency')
    total_engagement = fields.Monetary("Total Engangement", currency_field='company_currency')
    comex = fields.Selection([('yes', 'Oui'), ('no', 'Non')], string="Commerce Exterieur", default='no')
    team_lead = fields.Many2one('res.users', string="Chef d'équipe")
    domain_team_lead = fields.Char(compute="_compute_domain_team_lead")
    domain_user_id = fields.Char(compute="_compute_domain_team_lead")
    category = fields.Selection([('retail', 'Retail'),
                                  ('corporate', 'Corporate')], string="Catégorie")
    type_name = fields.Selection([('eer_exploitation', 'EER Exploitation'),
                                  ('eer_investment', 'EER Investisement'),
                                  ('eer_mix', 'EER Mixte'),
                                  ('eer_saving', 'EER Epargne'),
                                  ('eer_credit_saving', 'EER Crédit/épargne')], string="Type", required=True)

    state_conversion = fields.Selection([('in_lead', 'En Piste'),
                                         ('in_conversion', 'En conversion'),
                                         ('converted', 'Converté')], string="Etat de conversion", default="in_lead")

    ca = fields.Monetary(string='CA', currency_field='company_currency')
    capital = fields.Char(string='Capital')
    rnc = fields.Char(string='RNC')
    ebe = fields.Char(string='EBE')
    fp = fields.Char(string='FP')
    tb = fields.Char(string='TB')
    reference = fields.Char(string="Référence")

    bilan_id = fields.One2many('fsbk.bilan', 'lead_id')
    bilan1_id = fields.One2many('fsbk.bilan.cat1', 'lead_id')
    comment_cat1 = fields.Html(string='Commentaire')
    bilan2_id = fields.One2many('fsbk.bilan.cat2', 'lead_id')
    comment_cat2 = fields.Html(string='Commentaire')
    bilan3_id = fields.One2many('fsbk.bilan.cat3', 'lead_id')
    comment_cat3 = fields.Html(string='Commentaire')
    bilan4_id = fields.One2many('fsbk.bilan.cat4', 'lead_id')
    comment_cat4 = fields.Html(string='Commentaire')
    bilan5_id = fields.One2many('fsbk.bilan.cat5', 'lead_id')
    comment_cat5 = fields.Html(string='Commentaire')

    @api.model
    def create(self, vals):
        res = super(Lead, self).create(vals)
        for index, item in Doc_List:
            self.env['ir.attachment'].create({'lead_id': res.id,
                                              'list_doc': index,
                                              'name': item,
                                              'type': 'binary'
                                              })
        return res

    @api.depends('type_name')
    def _compute_name(self):
        for lead in self:
            if not lead.name and lead.type_name:
                lead.name = type_name.get(lead.type_name)

    @api.depends('geographic_area')
    def _compute_domain_team_lead(self):
        for rec in self:
            if rec.geographic_area:
                lead_team_ids = self.env['crm.team'].search([('geographic_area', '=', rec.geographic_area)])
                rec.domain_team_lead = json.dumps([('id', 'in', lead_team_ids.mapped('user_id').ids)])
                rec.domain_user_id = json.dumps([('id', 'in', list(set(lead_team_ids.mapped('member_ids').ids + lead_team_ids.mapped('user_id').ids)))])
            else:
                rec.domain_team_lead = json.dumps([])
                rec.domain_user_id = json.dumps([])

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        if self.partner_id:
            self.geographic_area = self.partner_id.geographic_area

    @api.onchange('geographic_area')
    def _onchange_geographic_area(self):
        team_id = False
        if self.geographic_area:
            team_id = self.env['crm.team'].search([('geographic_area', '=', self.geographic_area)], limit=1)

        self.team_lead = team_id and team_id.user_id or False

    @api.onchange('team_lead')
    def _onchange_team_lead(self):
        self.user_id = False

    def _convert_opportunity_data(self, customer, team_id=False):
        res_values = super(Lead, self)._convert_opportunity_data(customer, team_id)
        res_values.update({'state_conversion': 'in_conversion',
                           'type': 'lead'})

        geographic_area, team_lead = self.env.context.get('geographic_area', False), self.env.context.get('team_lead', False)
        if geographic_area and team_lead:
            res_values.update({'geographic_area': geographic_area,
                               'team_lead': team_lead})
        return res_values

    def accept_lead_conversion(self):
        self.write({'type': 'opportunity',
                    'reference': _('Opportunité/%s' % self.id),
                    'state_conversion': 'converted'})

    def decline_lead_conversion(self):
        self.write({'state_conversion': 'in_lead'})

    def convert_dossier(self):
        for rec in self:
            print('hi')
            final_stage = self.env['crm.stage'].search([('is_won', '=', True)])
            rec.stage_id = final_stage.id

    def calcul_ratio(self):
        for rec in self:
            if rec.tcr_id.state != 'valide' or rec.actif_id.state != 'valide' or rec.passif_id.state != 'valide':
                raise UserError('Vous devriez valider les bilans')
            else:
                if not rec.ratio_ids:
                    for index, item in list_ratio:
                        self.env['crm.ratio'].create({'lead': rec.id,
                                                      'ratio': index,
                                                      'name': item,
                                                      'montant_n': 0,
                                                      'montant_n1': 0,
                                                      })
                ratio_1 = rec.ratio_ids.filtered(lambda l: l.ratio == '1')
                tcr_7 = rec.tcr_id.tcr_lines.filtered(lambda r: r.rubrique.sequence == 7)
                ratio_1.montant_n = tcr_7.montant_n
                ratio_1.montant_n1 = tcr_7.montant_n1

                ratio_2 = rec.ratio_ids.filtered(lambda l: l.ratio == '2')
                tcr_33 = rec.tcr_id.tcr_lines.filtered(lambda r: r.rubrique.sequence == 33)
                ratio_2.montant_n = tcr_33.montant_n
                ratio_2.montant_n1 = tcr_33.montant_n1

                ratio_3 = rec.ratio_ids.filtered(lambda l: l.ratio == '3')
                ratio_3.montant_n = (tcr_33.montant_n / tcr_7.montant_n) * 100 if tcr_7.montant_n != 0 else 0
                ratio_3.montant_n1 = (tcr_33.montant_n1 / tcr_7.montant_n1) * 100 if tcr_7.montant_n1 != 0 else 0

                ratio_4 = rec.ratio_ids.filtered(lambda l: l.ratio == '4')
                tcr_50 = rec.tcr_id.tcr_lines.filtered(lambda r: r.rubrique.sequence == 50)
                ratio_4.montant_n = tcr_50.montant_n
                ratio_4.montant_n1 = tcr_50.montant_n1

                ratio_5 = rec.ratio_ids.filtered(lambda l: l.ratio == '5')
                ratio_5.montant_n = (tcr_50.montant_n / tcr_7.montant_n) * 100 if tcr_7.montant_n != 0 else 0
                ratio_5.montant_n1 = (tcr_50.montant_n / tcr_7.montant_n) * 100 if tcr_7.montant_n1 != 0 else 0

                ratio_6 = rec.ratio_ids.filtered(lambda l: l.ratio == '6')
                tcr_36 = rec.tcr_id.tcr_lines.filtered(lambda r: r.rubrique.sequence == 36)
                ratio_6.montant_n = tcr_50.montant_n + tcr_36.montant_n
                ratio_6.montant_n1 = tcr_50.montant_n1 + tcr_36.montant_n1

                ratio_7 = rec.ratio_ids.filtered(lambda l: l.ratio == '7')
                ratio_7.montant_n = (ratio_6.montant_n / tcr_36.montant_n) * 100
                ratio_7.montant_n1 = (ratio_6.montant_n1 / tcr_36.montant_n1) * 100

                ratio_8 = rec.ratio_ids.filtered(lambda l: l.ratio == '8')
                actif_20 = rec.actif_id.actif_lines.filtered(lambda r: r.rubrique.sequence == 20)
                ratio_8.montant_n = (actif_20.montant_n * 360) / tcr_7.montant_n if tcr_7.montant_n != 0 else 0
                ratio_8.montant_n1 = (actif_20.montant_n1 * 360) / tcr_7.montant_n1 if tcr_7.montant_n1 != 0 else 0

                ratio_9 = rec.ratio_ids.filtered(lambda l: l.ratio == '9')
                tcr_12 = rec.tcr_id.tcr_lines.filtered(lambda r: r.rubrique.sequence == 12)
                actif_18 = rec.actif_id.actif_lines.filtered(lambda r: r.rubrique.sequence == 18)
                ratio_9.montant_n = (actif_18.montant_n * 360) / tcr_12.montant_n if tcr_12.montant_n != 0 else 0
                ratio_9.montant_n1 = (actif_18.montant_n1 * 360) / tcr_12.montant_n1 if tcr_12.montant_n1 != 0 else 0

                ratio_10 = rec.ratio_ids.filtered(lambda l: l.ratio == '10')
                passif_20 = rec.passif_id.passif_lines.filtered(lambda r: r.rubrique.sequence == 20)
                ratio_10.montant_n = (passif_20.montant_n * 360) / tcr_7.montant_n if tcr_7.montant_n != 0 else 0
                ratio_10.montant_n1 = (passif_20.montant_n1 * 360) / tcr_7.montant_n1 if tcr_7.montant_n1 != 0 else 0

                ratio_11 = rec.ratio_ids.filtered(lambda l: l.ratio == '11')
                ratio_11.montant_n = actif_20.montant_n + actif_18.montant_n - passif_20.montant_n
                ratio_11.montant_n1 = actif_20.montant_n1 + actif_18.montant_n1 - passif_20.montant_n1

                ratio_12 = rec.ratio_ids.filtered(lambda l: l.ratio == '12')
                ratio_12.montant_n = (ratio_11.montant_n * 360) / tcr_7.montant_n if tcr_7.montant_n != 0 else 0
                ratio_12.montant_n1 = (ratio_11.montant_n1 * 360) / tcr_7.montant_n1 if tcr_7.montant_n1 != 0 else 0

                ratio_13 = rec.ratio_ids.filtered(lambda l: l.ratio == '13')
                passif_14 = rec.passif_id.passif_lines.filtered(lambda r: r.rubrique.sequence == 14)
                passif_23 = rec.passif_id.passif_lines.filtered(lambda r: r.rubrique.sequence == 23)
                passif_25 = rec.passif_id.passif_lines.filtered(lambda r: r.rubrique.sequence == 25)
                ratio_13.montant_n = ((passif_14.montant_n + passif_23.montant_n) / passif_25.montant_n) * 100 if passif_25.montant_n != 0 else 0
                ratio_13.montant_n1 = ((passif_14.montant_n1 + passif_23.montant_n1) / passif_25.montant_n1) * 100 if passif_25.montant_n1 != 0 else 0

                ratio_14 = rec.ratio_ids.filtered(lambda l: l.ratio == '14')
                passif_12 = rec.passif_id.passif_lines.filtered(lambda r: r.rubrique.sequence == 12)
                ratio_14.montant_n = (passif_12.montant_n / passif_25.montant_n) * 100 if passif_25.montant_n != 0 else 0
                ratio_14.montant_n1 = (passif_12.montant_n1 / passif_25.montant_n1) * 100 if passif_25.montant_n1 != 0 else 0
                rec.create_viz3()

    def create_viz3(self):
        for rec in self:
            line1 = rec.ratio_ids.filtered(lambda r: r.ratio == '1')
            line2 = rec.ratio_ids.filtered(lambda r: r.ratio == '2')
            line3 = rec.ratio_ids.filtered(lambda r: r.ratio == '4')
            data1 = [line1.montant_n, line1.montant_n1]
            data2 = [line2.montant_n, line2.montant_n1]
            data3 = [line3.montant_n, line3.montant_n1]
            label1 = 'CA'
            label2 = 'EBE'
            label3 = 'RNC'
            year = ["N", "N-1"]
            fig, ax = plt.subplots()
            width = 0.12
            X_axis = np.arange(len(year))
            rects1 = ax.bar(X_axis - width, data1, width, color="yellow", label=label1)
            rects2 = ax.bar(X_axis, data2, width, color="orange", label=label2)
            rects3 = ax.bar(X_axis + width, data3, width, color="red", label=label3)
            ax.set_ylabel('Montant')
            ax.set_title('Montant par année')
            ax.set_xticks(X_axis + width, year)
            ax.legend(loc="lower left", bbox_to_anchor=(0.8, 1.0))
            fig.tight_layout()
            buf = BytesIO()
            plt.savefig(buf, format='jpeg', dpi=100)
            buf.seek(0)
            rec.visualisation = base64.b64encode(buf.getvalue())
            buf.close()

    def open_crv(self):
        for rec in self:
            view_id = self.env.ref('crm_portal.compte_rendu_views_wizard_form').id
            res_id = self.env['crm.compte.rendu'].search([('lead_id', '=', rec.id)])
            if not res_id:
                res_id = self.env['crm.compte.rendu'].create({'lead_id': rec.id})
            return {
                'name': 'Compte rendu de visite',
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'crm.compte.rendu',
                'res_id': res_id.id,
                'view_id': view_id,
                'target': 'current',
            }

    def action_create_tcr(self):
        for rec in self:
            view_id = self.env.ref('financial_modeling.import_ocr_tcr_view_form').id
            return {
                'name': 'TCR',
                'domain': [('lead_parent_id', '=', rec.id)],
                'res_model': 'import.ocr.tcr',
                'view_mode': 'form',
                'view_id': view_id,
                'type': 'ir.actions.act_window',
                'context': {'lead_parent_id': rec.id, 'year': 1}
            }
    def action_create_tcr1(self):
        for rec in self:
            view_id = self.env.ref('financial_modeling.import_ocr_tcr_view_form').id
            return {
                'name': 'TCR',
                'domain': [('lead_parent_id', '=', rec.id)],
                'res_model': 'import.ocr.tcr',
                'view_mode': 'form',
                'view_id': view_id,
                'type': 'ir.actions.act_window',
                'context': {'lead_parent_id': rec.id, 'year': 2}
            }

    def action_create_actif(self):
        for rec in self:
            view_id = self.env.ref('financial_modeling.import_ocr_actif_view_form').id
            return {
                'name': 'Actif',
                'domain': [('lead_parent_id', '=', rec.id)],
                'res_model': 'import.ocr.actif',
                'view_mode': 'form',
                'view_id': view_id,
                'type': 'ir.actions.act_window',
                'context': {'lead_parent_id': rec.id, 'year': 1}
            }

    def action_create_actif1(self):
        for rec in self:
            view_id = self.env.ref('financial_modeling.import_ocr_actif_view_form').id
            return {
                'name': 'Actif',
                'domain': [('lead_parent_id', '=', rec.id)],
                'res_model': 'import.ocr.actif',
                'view_mode': 'form',
                'view_id': view_id,
                'type': 'ir.actions.act_window',
                'context': {'lead_parent_id': rec.id, 'year': 2}
            }
    def action_create_passif(self):
        for rec in self:
            view_id = self.env.ref('financial_modeling.import_ocr_passif_view_form').id
            return {
                'name': 'Passif',
                'domain': [('lead_parent_id', '=', rec.id)],
                'res_model': 'import.ocr.passif',
                'view_mode': 'form',
                'view_id': view_id,
                'type': 'ir.actions.act_window',
                'context': {'lead_parent_id': rec.id, 'year': 1}
            }

    def action_create_passif1(self):
        for rec in self:
            view_id = self.env.ref('financial_modeling.import_ocr_passif_view_form').id
            return {
                'name': 'Passif',
                'domain': [('lead_parent_id', '=', rec.id)],
                'res_model': 'import.ocr.passif',
                'view_mode': 'form',
                'view_id': view_id,
                'type': 'ir.actions.act_window',
                'context': {'lead_parent_id': rec.id, 'year': 2}
            }


    def import_data(self):
        for rec in self:
            if rec.tcr_id.state not in ['valide', 'modified'] or rec.actif_id.state not in ['valide',
                                                                                            'modified'] or rec.passif_id.state not in [
                'valide', 'modified']:
                raise ValidationError("Vous devriez d'abord valider les bilans")
            else:
                to_delete = rec.bilan_id.filtered(lambda r: r.declaration in ['ACTIF NET IMMOBILISE CORPOREL',
                                                                              'الات ومعدات و عتاد نقل',
                                                                              'إهتلاكات المعدات',
                                                                              'اهتلاكات / آلات و معدات و عتاد نقل'])
                if to_delete:
                    to_delete1 = rec.bilan1_id.filtered(lambda r: r.sequence in [6, 7, 8, 9])
                    to_delete.unlink()
                    to_delete1.unlink()
                    other_bilan = rec.bilan_id.filtered(lambda r: r.sequence >= 6)
                    count = 6
                    for item in other_bilan:
                        in_view = self.env[f'fsbk.bilan.cat{item.categorie}'].search([('bilan', '=', item.id)])
                        item.sequence = in_view.sequence = count
                        count += 1

                bilan_1 = rec.bilan_id.filtered(lambda r: r.sequence == 1)
                # total I حقوق الملكية
                passif_1 = rec.passif_id.passif_lines.filtered(lambda r: r.rubrique.sequence == 12)
                passif1_1 = rec.passif1_id.passif_lines.filtered(lambda r: r.rubrique.sequence == 12)
                bilan_1.write({'year_4': passif_1.montant_n,
                               'year_3': passif_1.montant_n1,
                               'year_2': passif1_1.montant_n,
                               'year_1': passif1_1.montant_n1})

                # capital emis رأس المال
                bilan_2 = rec.bilan_id.filtered(lambda r: r.sequence == 2)
                passif_2 = rec.passif_id.passif_lines.filtered(lambda r: r.rubrique.sequence == 2)
                passif1_2 = rec.passif1_id.passif_lines.filtered(lambda r: r.rubrique.sequence == 2)
                bilan_2.write({'year_4': passif_2.montant_n,
                               'year_3': passif_2.montant_n1,
                               'year_2': passif1_2.montant_n,
                               'year_1': passif1_2.montant_n1,
                               })

                # Passif - Autres capitaux propres - report à nouveau الاحتياطات
                bilan_3 = rec.bilan_id.filtered(lambda r: r.sequence == 3)
                passif_3 = rec.passif_id.passif_lines.filtered(lambda r: r.rubrique.sequence == 4)
                passif1_3 = rec.passif1_id.passif_lines.filtered(lambda r: r.rubrique.sequence == 4)
                bilan_3.write({'year_4': passif_3.montant_n,
                               'year_3': passif_3.montant_n1,
                               'year_2': passif1_3.montant_n,
                               'year_1': passif1_3.montant_n1})

                # الارباح المتراكمة
                bilan_4 = rec.bilan_id.filtered(lambda r: r.sequence == 4)
                passif_3 = rec.passif_id.passif_lines.filtered(lambda r: r.rubrique.sequence == 8)
                passif1_3 = rec.passif1_id.passif_lines.filtered(lambda r: r.rubrique.sequence == 8)
                tcr_3 = rec.tcr_id.tcr_lines.filtered(lambda r: r.rubrique.sequence == 50)
                tcr1_3 = rec.tcr1_id.tcr_lines.filtered(lambda r: r.rubrique.sequence == 50)
                bilan_4.write({'year_4': passif_3.montant_n + tcr_3.montant_n,
                               'year_3': passif_3.montant_n1 + tcr_3.montant_n1,
                               'year_2': passif1_3.montant_n + tcr1_3.montant_n,
                               'year_1': passif1_3.montant_n1 + tcr1_3.montant_n1})

                # حقوق الملكية / مجموع الميزانية
                bilan_5 = rec.bilan_id.filtered(lambda r: r.sequence == 5)
                passif_12 = rec.passif_id.passif_lines.filtered(lambda r: r.rubrique.sequence == 25)
                passif1_12 = rec.passif1_id.passif_lines.filtered(lambda r: r.rubrique.sequence == 25)
                bilan_5.write(
                    {'year_4': (passif_1.montant_n / passif_12.montant_n) * 100 if passif_12.montant_n != 0 else 0,
                     'year_3': (passif_1.montant_n1 / passif_12.montant_n1) * 100 if passif_12.montant_n1 != 0 else 0,
                     'year_2': (passif1_1.montant_n / passif1_12.montant_n) * 100 if passif1_12.montant_n != 0 else 0,
                     'year_1': (
                                           passif1_1.montant_n1 / passif1_12.montant_n1) * 100 if passif1_12.montant_n1 != 0 else 0})
                if passif_12.montant_n == 0:
                    bilan_5.is_null_4 = True
                if passif_12.montant_n1 == 0:
                    bilan_5.is_null_3 = True
                if passif1_12.montant_n == 0:
                    bilan_5.is_null_2 = True
                if passif1_12.montant_n1 == 0:
                    bilan_5.is_null_1 = True
                '''# Actif net immobilisé corporel
                bilan_6 = rec.bilan_id.filtered(lambda r: r.sequence == 6)
                actif_1 = rec.actif_id.actif_lines.filtered(lambda r: r.rubrique.sequence == 4)
                actif1_1 = rec.actif1_id.actif_lines.filtered(lambda r: r.rubrique.sequence == 4)
                bilan_6.write({'year_4': actif_1.montant_n,
                               'year_3': actif_1.montant_n1,
                               'year_2': actif1_1.montant_n,
                               'year_1': actif1_1.montant_n1})

                # الات ومعدات وعتاد نقل
                bilan_7 = rec.bilan_id.filtered(lambda r: r.sequence == 7)
                actif_7 = rec.actif_id.actif_lines.filtered(lambda r: r.rubrique.sequence == 7)
                actif1_7 = rec.actif1_id.actif_lines.filtered(lambda r: r.rubrique.sequence == 7)
                bilan_7.write({'year_4': actif_7.montant_n,
                               'year_3': actif_7.montant_n1,
                               'year_2': actif1_7.montant_n,
                               'year_1': actif1_7.montant_n1})

                #اهتلاكات المعدات
                bilan_8 = rec.bilan_id.filtered(lambda r: r.sequence == 8)
                bilan_8.write({'year_4': actif_7.montant_2n,
                               'year_3': 0,
                               'year_2': 0,
                               'year_1': 0})
                # اهتلاكات / الات ومعدات وعتاد نقل
                bilan_9 = rec.bilan_id.filtered(lambda r: r.sequence == 9)
                bilan_9.write({'year_4': (bilan_8.year_4 / bilan_7.year_4) * 100 if bilan_7.year_4 != 0 else 0,
                               'year_3': (bilan_8.year_3 / bilan_7.year_3) * 100 if bilan_7.year_3 != 0 else 0,
                               'year_2': (bilan_8.year_2 / bilan_7.year_2) * 100 if bilan_7.year_2 != 0 else 0,
                               'year_1': (bilan_8.year_1 / bilan_7.year_1) * 100 if bilan_7.year_1 != 0 else 0})
                if bilan_7.year_4 == 0:
                    bilan_9.is_null_4 = True
                if bilan_7.year_3 == 0:
                    bilan_9.is_null_3 = True
                if bilan_7.year_2 == 0:
                    bilan_9.is_null_2 = True
                if bilan_7.year_1 == 0:
                    bilan_9.is_null_1 = True'''
                # Passif (Total I + Total II) - Total actif non courant   صافي رأس المال العامل
                actif_2 = rec.actif_id.actif_lines.filtered(lambda r: r.rubrique.sequence == 16)
                actif1_2 = rec.actif1_id.actif_lines.filtered(lambda r: r.rubrique.sequence == 16)
                actif_27 = rec.actif_id.actif_lines.filtered(lambda r: r.rubrique.sequence == 27)
                actif1_27 = rec.actif1_id.actif_lines.filtered(lambda r: r.rubrique.sequence == 27)
                passif_24 = rec.passif_id.passif_lines.filtered(lambda r: r.rubrique.sequence == 24)
                passif1_24 = rec.passif1_id.passif_lines.filtered(lambda r: r.rubrique.sequence == 24)
                bilan_10 = rec.bilan_id.filtered(lambda r: r.sequence == 6)
                print(bilan_10.declaration)
                bilan_10.write({'year_4': actif_27.montant_n - passif_24.montant_n,
                                'year_3': actif_27.montant_n1 - passif_24.montant_n1,
                                'year_2': actif1_27.montant_n - passif1_24.montant_n,
                                'year_1': actif1_27.montant_n1 - passif1_24.montant_n1,
                                })

                # احتياجات رأس المال العامل
                passif_4_1 = rec.passif_id.passif_lines.filtered(lambda r: r.rubrique.sequence == 24)
                passif1_4_1 = rec.passif1_id.passif_lines.filtered(lambda r: r.rubrique.sequence == 24)
                actif_3 = rec.actif_id.actif_lines.filtered(lambda r: r.rubrique.sequence == 27)
                actif1_3 = rec.actif1_id.actif_lines.filtered(lambda r: r.rubrique.sequence == 27)

                passif_5 = rec.passif_id.passif_lines.filtered(lambda r: r.rubrique.sequence == 23)
                passif1_5 = rec.passif1_id.passif_lines.filtered(lambda r: r.rubrique.sequence == 23)
                bilan_11 = rec.bilan_id.filtered(lambda r: r.sequence == 7)
                passif_20 = rec.passif_id.passif_lines.filtered(lambda r: r.rubrique.sequence == 20)
                passif1_20 = rec.passif1_id.passif_lines.filtered(lambda r: r.rubrique.sequence == 20)
                actif_18 = rec.actif_id.actif_lines.filtered(lambda r: r.rubrique.sequence == 18)
                actif1_18 = rec.actif1_id.actif_lines.filtered(lambda r: r.rubrique.sequence == 18)
                actif_20 = rec.actif_id.actif_lines.filtered(lambda r: r.rubrique.sequence == 20)
                actif1_20 = rec.actif1_id.actif_lines.filtered(lambda r: r.rubrique.sequence == 20)
                actif_126 = rec.actif_id.actif_lines.filtered(lambda r: r.rubrique.sequence == 26)
                actif1_126 = rec.actif1_id.actif_lines.filtered(lambda r: r.rubrique.sequence == 26)
                bilan_11.write(
                    {'year_4': actif_27.montant_n - actif_126.montant_n - (passif_24.montant_n - passif_5.montant_n),
                     'year_3': actif_27.montant_n1 - actif_126.montant_n1 - (
                                 passif_24.montant_n1 - passif_5.montant_n1),
                     'year_2': actif1_27.montant_n - actif1_126.montant_n - (
                                 passif1_24.montant_n - passif1_5.montant_n),
                     'year_1': actif1_27.montant_n1 - actif1_126.montant_n1 - (
                                 passif1_24.montant_n1 - passif1_5.montant_n1),
                     })

                # FR / BFR Passif (Total I + Total II) - Actif (Total actif non courant)  / Actif (Stock et encours + Créances et emploi assimili + Disponibilité et assimilé) - Passif (Total III)
                bilan_12 = rec.bilan_id.filtered(lambda r: r.sequence == 8)
                actif_4 = rec.actif_id.actif_lines.filtered(lambda r: r.rubrique.sequence == 18)
                actif1_4 = rec.actif1_id.actif_lines.filtered(lambda r: r.rubrique.sequence == 18)
                actif_12 = rec.actif_id.actif_lines.filtered(lambda r: r.rubrique.sequence == 19)
                actif1_12 = rec.actif1_id.actif_lines.filtered(lambda r: r.rubrique.sequence == 19)
                actif_13 = rec.actif_id.actif_lines.filtered(lambda r: r.rubrique.sequence == 24)
                actif1_13 = rec.actif1_id.actif_lines.filtered(lambda r: r.rubrique.sequence == 24)

                if bilan_11.year_4 == 0:
                    bilan_12.is_null_4 = True
                if bilan_11.year_4 == 0:
                    bilan_12.is_null_3 = True
                if bilan_11.year_4 == 0:
                    bilan_12.is_null_2 = True
                if bilan_11.year_4 == 0:
                    bilan_12.is_null_1 = True
                bilan_12.write({'year_4': (bilan_10.year_4 / bilan_11.year_4) * 100 if bilan_11.year_4 != 0 else 0,
                                'year_3': (bilan_10.year_3 / bilan_11.year_3) * 100 if bilan_11.year_3 != 0 else 0,
                                'year_2': (bilan_10.year_2 / bilan_11.year_2) * 100 if bilan_11.year_2 != 0 else 0,
                                'year_1': (bilan_10.year_1 / bilan_11.year_1) * 100 if bilan_11.year_1 != 0 else 0,
                                })
                # مجموع المطلوبات Passif - Total II + Total III
                bilan_13 = rec.bilan_id.filtered(lambda r: r.sequence == 9)
                passif_5 = rec.passif_id.passif_lines.filtered(lambda r: r.rubrique.sequence == 23)
                passif1_5 = rec.passif1_id.passif_lines.filtered(lambda r: r.rubrique.sequence == 23)
                passif_6 = rec.passif_id.passif_lines.filtered(lambda r: r.rubrique.sequence == 14)
                passif1_6 = rec.passif1_id.passif_lines.filtered(lambda r: r.rubrique.sequence == 14)
                passif_22 = rec.passif_id.passif_lines.filtered(lambda r: r.rubrique.sequence == 22)
                passif1_22 = rec.passif1_id.passif_lines.filtered(lambda r: r.rubrique.sequence == 22)
                bilan_13.write(
                    {'year_4': passif_5.montant_n + passif_6.montant_n + passif_20.montant_n + passif_22.montant_n,
                     'year_3': passif_5.montant_n1 + passif_6.montant_n1 + passif_20.montant_n1 + passif_22.montant_n1,
                     'year_2': passif1_5.montant_n + passif1_6.montant_n + passif1_20.montant_n + passif1_22.montant_n,
                     'year_1': passif1_5.montant_n1 + passif1_6.montant_n1 + passif1_20.montant_n1 + passif1_22.montant_n1,
                     })

                # التزامات بنكية
                bilan_14 = rec.bilan_id.filtered(lambda r: r.sequence == 10)
                passif_5 = rec.passif_id.passif_lines.filtered(lambda r: r.rubrique.sequence == 23)
                passif1_5 = rec.passif1_id.passif_lines.filtered(lambda r: r.rubrique.sequence == 23)
                passif_6 = rec.passif_id.passif_lines.filtered(lambda r: r.rubrique.sequence == 14)
                passif1_6 = rec.passif1_id.passif_lines.filtered(lambda r: r.rubrique.sequence == 14)
                bilan_14.write({'year_4': passif_5.montant_n + passif_6.montant_n,
                                'year_3': passif_5.montant_n1 + passif_6.montant_n1,
                                'year_2': passif1_5.montant_n + passif1_6.montant_n,
                                'year_1': passif1_5.montant_n1 + passif1_6.montant_n1,
                                })
                # تسهيلات الموردين
                bilan_15 = rec.bilan_id.filtered(lambda r: r.sequence == 11)
                passif_7 = rec.passif_id.passif_lines.filtered(lambda r: r.rubrique.sequence == 20)
                passif1_7 = rec.passif1_id.passif_lines.filtered(lambda r: r.rubrique.sequence == 20)
                var_5 = rec.var_ids.filtered(lambda r: r.sequence == 5)
                bilan_15.write({'year_4': passif_7.montant_n,
                                'year_3': passif_7.montant_n1,
                                'year_2': passif1_7.montant_n,
                                'year_1': passif1_7.montant_n1})

                var_5.write({'montant': passif_7.montant_n})

                # Passif - Impôts مستحقات ضرائب
                bilan_16 = rec.bilan_id.filtered(lambda r: r.sequence == 12)
                passif_8 = rec.passif_id.passif_lines.filtered(lambda r: r.rubrique.sequence == 21)
                passif1_8 = rec.passif1_id.passif_lines.filtered(lambda r: r.rubrique.sequence == 21)
                bilan_16.write({'year_4': passif_8.montant_n,
                                'year_3': passif_8.montant_n1,
                                'year_2': passif1_8.montant_n,
                                'year_1': passif1_8.montant_n1,
                                })

                # Passif - Autres dettes + fournisseur  مطلوبات أخرى متداولة
                bilan_17 = rec.bilan_id.filtered(lambda r: r.sequence == 13)
                passif_8 = rec.passif_id.passif_lines.filtered(lambda r: r.rubrique.sequence == 22)
                passif1_8 = rec.passif1_id.passif_lines.filtered(lambda r: r.rubrique.sequence == 22)
                bilan_17.write({'year_4': passif_8.montant_n,
                                'year_3': passif_8.montant_n1,
                                'year_2': passif1_8.montant_n,
                                'year_1': passif1_8.montant_n1,
                                })

                # (Emprunts et dettes financières passif + Trésorerie passif - Trésorerie coté actif ) / Total I coté passif نسبة المديونية Leverage
                bilan_18 = rec.bilan_id.filtered(lambda r: r.sequence == 14)
                passif_18 = rec.passif_id.passif_lines.filtered(lambda r: r.rubrique.sequence == 18)
                passif1_18 = rec.passif1_id.passif_lines.filtered(lambda r: r.rubrique.sequence == 18)
                passif_24 = rec.passif_id.passif_lines.filtered(lambda r: r.rubrique.sequence == 24)
                passif1_24 = rec.passif1_id.passif_lines.filtered(lambda r: r.rubrique.sequence == 24)
                bilan_18.write({'year_4': (
                                                      passif_18.montant_n + passif_24.montant_n) / passif_1.montant_n if passif_1.montant_n != 0 else 0,
                                'year_3': (
                                                      passif_18.montant_n1 + passif_24.montant_n1) / passif_1.montant_n1 if passif_1.montant_n1 != 0 else 0,
                                'year_2': (
                                                      passif1_18.montant_n + passif1_24.montant_n) / passif1_1.montant_n if passif1_1.montant_n != 0 else 0,
                                'year_1': (
                                                      passif1_18.montant_n1 + passif1_24.montant_n1) / passif1_1.montant_n1 if passif1_1.montant_n1 != 0 else 0,
                                })
                if passif_1.montant_n == 0:
                    bilan_18.is_null_4 = True
                if passif_1.montant_n1 == 0:
                    bilan_18.is_null_3 = True
                if passif1_1.montant_n == 0:
                    bilan_18.is_null_2 = True
                if passif1_1.montant_n1 == 0:
                    bilan_18.is_null_1 = True

                # الالتزامات اتجاه البنوك / الحقوق
                bilan_19 = rec.bilan_id.filtered(lambda r: r.sequence == 15)
                bilan_19.write({'year_4': bilan_14.year_4 / passif_1.montant_n if passif_1.montant_n != 0 else 0,
                                'year_3': bilan_14.year_3 / passif_1.montant_n1 if passif_1.montant_n1 != 0 else 0,
                                'year_2': bilan_14.year_2 / passif1_1.montant_n if passif1_1.montant_n != 0 else 0,
                                'year_1': bilan_14.year_1 / passif1_1.montant_n1 if passif1_1.montant_n1 != 0 else 0,
                                })

                if passif_1.montant_n == 0:
                    bilan_19.is_null_4 = True
                if passif_1.montant_n1 == 0:
                    bilan_19.is_null_3 = True
                if passif1_1.montant_n == 0:
                    bilan_19.is_null_2 = True
                if passif1_1.montant_n1 == 0:
                    bilan_19.is_null_1 = True

                # مجموع الميزانية
                bilan_20 = rec.bilan_id.filtered(lambda r: r.sequence == 16)
                bilan_20.write({'year_4': passif_12.montant_n,
                                'year_3': passif_12.montant_n1,
                                'year_2': passif1_12.montant_n,
                                'year_1': passif1_12.montant_n1
                                })
                # المبيعات ، الايرادات
                bilan_21 = rec.bilan_id.filtered(lambda r: r.sequence == 17)
                tcr_1 = rec.tcr_id.tcr_lines.filtered(lambda r: r.rubrique.sequence == 7)
                tcr1_1 = rec.tcr1_id.tcr_lines.filtered(lambda r: r.rubrique.sequence == 7)
                var_1 = rec.var_ids.filtered(lambda r: r.sequence == 1)
                bilan_21.write({'year_4': tcr_1.montant_n,
                                'year_3': tcr_1.montant_n1,
                                'year_2': tcr1_1.montant_n,
                                'year_1': tcr1_1.montant_n1
                                })
                var_1.write({'montant': tcr_1.montant_n})
                # TCR- Excédent brut d`exploitation   EBITDA
                bilan_22 = rec.bilan_id.filtered(lambda r: r.sequence == 18)
                tcr_2 = rec.tcr_id.tcr_lines.filtered(lambda r: r.rubrique.sequence == 33)
                tcr1_2 = rec.tcr1_id.tcr_lines.filtered(lambda r: r.rubrique.sequence == 33)
                bilan_22.write({'year_4': tcr_2.montant_n,
                                'year_3': tcr_2.montant_n1,
                                'year_2': tcr1_2.montant_n,
                                'year_1': tcr1_2.montant_n1})

                # TCR - Résultat net de l`exercice   صافي الأرباح
                bilan_23 = rec.bilan_id.filtered(lambda r: r.sequence == 19)
                tcr_3 = rec.tcr_id.tcr_lines.filtered(lambda r: r.rubrique.sequence == 50)
                tcr1_3 = rec.tcr1_id.tcr_lines.filtered(lambda r: r.rubrique.sequence == 50)
                bilan_23.write({'year_4': tcr_3.montant_n,
                                'year_3': tcr_3.montant_n1,
                                'year_2': tcr1_3.montant_n,
                                'year_1': tcr1_3.montant_n1})

                bilan_24 = rec.bilan_id.filtered(lambda r: r.sequence == 20)
                # صافي الأرباح/المبيعات
                bilan_24.write({'year_4': (tcr_3.montant_n / tcr_1.montant_n) * 100 if tcr_1.montant_n != 0 else 0,
                                'year_3': (tcr_3.montant_n1 / tcr_1.montant_n1) * 100 if tcr_1.montant_n1 != 0 else 0,
                                'year_2': (tcr1_3.montant_n / tcr1_1.montant_n) * 100 if tcr1_1.montant_n != 0 else 0,
                                'year_1': (
                                                      tcr1_3.montant_n1 / tcr1_1.montant_n1) * 100 if tcr1_1.montant_n1 != 0 else 0})

                if tcr_1.montant_n == 0:
                    bilan_24.is_null_4 = True
                if tcr_1.montant_n1 == 0:
                    bilan_24.is_null_3 = True
                if tcr1_1.montant_n == 0:
                    bilan_24.is_null_2 = True
                if tcr1_1.montant_n1 == 0:
                    bilan_24.is_null_1 = True
                # معدل العائد على الموجودات ROA
                bilan_25 = rec.bilan_id.filtered(lambda r: r.sequence == 21)
                bilan_25.write({'year_4': (tcr_3.montant_n / actif_2.montant_n) * 100 if actif_2.montant_n != 0 else 0,
                                'year_3': (
                                                      tcr_3.montant_n1 / actif_2.montant_n1) * 100 if actif_2.montant_n1 != 0 else 0,
                                'year_2': (
                                                      tcr1_3.montant_n / actif1_2.montant_n) * 100 if actif1_2.montant_n != 0 else 0,
                                'year_1': (
                                                      tcr1_3.montant_n1 / actif1_2.montant_n1) * 100 if actif1_2.montant_n1 != 0 else 0})

                if actif_2.montant_n == 0:
                    bilan_25.is_null_4 = True
                if actif_2.montant_n1 == 0:
                    bilan_25.is_null_3 = True
                if actif1_2.montant_n == 0:
                    bilan_25.is_null_2 = True
                if actif1_2.montant_n1 == 0:
                    bilan_25.is_null_1 = True
                # معدل العائد على حقوق الملكية ROE
                bilan_26 = rec.bilan_id.filtered(lambda r: r.sequence == 22)
                bilan_26.write(
                    {'year_4': (tcr_3.montant_n / passif_1.montant_n) * 100 if passif_1.montant_n != 0 else 0,
                     'year_3': (tcr_3.montant_n1 / passif_1.montant_n1) * 100 if passif_1.montant_n1 != 0 else 0,
                     'year_2': (tcr1_3.montant_n / passif1_1.montant_n) * 100 if passif1_1.montant_n != 0 else 0,
                     'year_1': (tcr1_3.montant_n1 / passif1_1.montant_n1) * 100 if passif1_1.montant_n1 != 0 else 0})

                if passif_1.montant_n == 0:
                    bilan_26.is_null_4 = True
                if passif_1.montant_n1 == 0:
                    bilan_26.is_null_3 = True
                if passif1_1.montant_n == 0:
                    bilan_26.is_null_2 = True
                if passif1_1.montant_n1 == 0:
                    bilan_26.is_null_1 = True
                # التدفقات النقدية التشغيلية
                bilan_27 = rec.bilan_id.filtered(lambda r: r.sequence == 23)
                tcr_36 = rec.tcr_id.tcr_lines.filtered(lambda r: r.rubrique.sequence == 36)
                tcr1_36 = rec.tcr1_id.tcr_lines.filtered(lambda r: r.rubrique.sequence == 36)
                bilan_27.write(
                    {'year_4': tcr_3.montant_n + tcr_36.montant_n,
                     'year_3': tcr_3.montant_n1 + tcr_36.montant_n1,
                     'year_2': tcr1_3.montant_n + tcr1_36.montant_n,
                     'year_1': tcr1_3.montant_n1 + tcr1_36.montant_n1})

                # نسبة التداول (السيولة)
                actif_26 = rec.actif_id.actif_lines.filtered(lambda r: r.rubrique.sequence == 26)
                actif1_26 = rec.actif1_id.actif_lines.filtered(lambda r: r.rubrique.sequence == 26)
                bilan_28 = rec.bilan_id.filtered(lambda r: r.sequence == 24)
                bilan_28.write({'year_4': (actif_26.montant_n + actif_18.montant_n + actif_20.montant_n) / (
                            passif_5.montant_n + passif_20.montant_n) if passif_5.montant_n + passif_20.montant_n != 0 else 0,
                                'year_3': (actif_26.montant_n1 + actif_18.montant_n1 + actif_20.montant_n1) / (
                                            passif_5.montant_n1 + passif_20.montant_n1) if passif_5.montant_n1 + passif_20.montant_n1 != 0 else 0,
                                'year_2': (actif1_26.montant_n + actif1_18.montant_n + actif1_20.montant_n) / (
                                            passif1_5.montant_n + passif1_20.montant_n) if passif1_5.montant_n + passif1_20.montant_n != 0 else 0,
                                'year_1': (actif1_26.montant_n1 + actif1_18.montant_n1 + actif1_20.montant_n1) / (
                                            passif1_5.montant_n1 + passif1_20.montant_n1) if passif1_5.montant_n1 + passif1_20.montant_n1 != 0 else 0})

                # نسبة السيولة السريعة
                bilan_29 = rec.bilan_id.filtered(lambda r: r.sequence == 25)
                bilan_29.write({'year_4': (actif_26.montant_n) / (
                            passif_5.montant_n + passif_20.montant_n) if passif_5.montant_n + passif_20.montant_n != 0 else 0,
                                'year_3': (actif_26.montant_n) / (
                                            passif_5.montant_n1 + passif_20.montant_n1) if passif_5.montant_n1 + passif_20.montant_n1 != 0 else 0,
                                'year_2': (actif1_26.montant_n) / (
                                            passif1_5.montant_n + passif1_20.montant_n) if passif1_5.montant_n + passif1_20.montant_n != 0 else 0,
                                'year_1': (actif1_26.montant_n1) / (
                                            passif1_5.montant_n1 + passif1_20.montant_n1) if passif1_5.montant_n1 + passif1_20.montant_n1 != 0 else 0,
                                })

                if (passif_5.montant_n + passif_20.montant_n) == 0:
                    bilan_28.is_null_4 = True
                    bilan_29.is_null_4 = True
                if (passif_5.montant_n1 + passif_20.montant_n1) == 0:
                    bilan_28.is_null_3 = True
                    bilan_29.is_null_3 = True
                if (passif1_5.montant_n + passif1_20.montant_n) == 0:
                    bilan_28.is_null_2 = True
                    bilan_29.is_null_2 = True
                if (passif1_5.montant_n1 + passif1_20.montant_n1) == 0:
                    bilan_28.is_null_1 = True
                    bilan_29.is_null_1 = True
                # حقوق عند الزبائن
                bilan_30 = rec.bilan_id.filtered(lambda r: r.sequence == 26)
                actif_5 = rec.actif_id.actif_lines.filtered(lambda r: r.rubrique.sequence == 20)
                actif1_5 = rec.actif1_id.actif_lines.filtered(lambda r: r.rubrique.sequence == 20)
                var_3 = rec.var_ids.filtered(lambda r: r.sequence == 3)
                bilan_30.write({'year_4': actif_5.montant_n,
                                'year_3': actif_5.montant_n1,
                                'year_2': actif1_5.montant_n,
                                'year_1': actif1_5.montant_n1,
                                })
                var_3.write({'montant': actif_5.montant_n})

                # المخزون
                bilan_31 = rec.bilan_id.filtered(lambda r: r.sequence == 27)
                bilan_31.write({'year_4': actif_4.montant_n,
                                'year_3': actif_4.montant_n1,
                                'year_2': actif1_4.montant_n,
                                'year_1': actif1_4.montant_n1,
                                })
                var_4 = rec.var_ids.filtered(lambda r: r.sequence == 4)
                var_4.write({'montant': actif_4.montant_n})

                # متوسط دوران المخزون (يوم)
                bilan_32 = rec.bilan_id.filtered(lambda r: r.sequence == 28)
                tcr_5 = rec.tcr_id.tcr_lines.filtered(lambda r: r.rubrique.sequence == 12)
                tcr1_5 = rec.tcr1_id.tcr_lines.filtered(lambda r: r.rubrique.sequence == 12)
                tcr_6 = rec.tcr_id.tcr_lines.filtered(lambda r: r.rubrique.sequence == 13)
                tcr1_6 = rec.tcr1_id.tcr_lines.filtered(lambda r: r.rubrique.sequence == 13)
                tcr_14 = rec.tcr_id.tcr_lines.filtered(lambda r: r.rubrique.sequence == 14)
                tcr1_14 = rec.tcr1_id.tcr_lines.filtered(lambda r: r.rubrique.sequence == 14)
                var_2 = rec.var_ids.filtered(lambda r: r.sequence == 2)
                bilan_32.write({'year_4': (actif_4.montant_n * 360) / (
                            tcr_5.montant_n + tcr_6.montant_n + tcr_14.montant_n) if (
                                                                                                 tcr_5.montant_n + tcr_6.montant_n + tcr_14.montant_n) != 0 else 0,
                                'year_3': (actif_4.montant_n1 * 360) / (
                                            tcr_5.montant_n1 + tcr_6.montant_n1 + tcr_14.montant_n1) if (
                                                                                                                    tcr_5.montant_n1 + tcr_6.montant_n1 + tcr_14.montant_n1) != 0 else 0,
                                'year_2': (actif1_4.montant_n * 360) / (
                                            tcr1_5.montant_n + tcr1_6.montant_n + tcr1_14.montant_n) if (
                                                                                                                    tcr1_5.montant_n + tcr1_6.montant_n + tcr1_14.montant_n) != 0 else 0,
                                'year_1': (actif1_4.montant_n1 * 360) / (
                                            tcr1_5.montant_n1 + tcr1_6.montant_n1 + tcr1_14.montant_n1) if (
                                                                                                                       tcr1_5.montant_n1 + tcr1_6.montant_n1 + tcr1_14.montant_n1) != 0 else 0,
                                })

                if (tcr_5.montant_n + tcr_6.montant_n + tcr_14.montant_n) == 0:
                    bilan_32.is_null_4 = True
                if (tcr_5.montant_n1 + tcr_6.montant_n1 + tcr_14.montant_n1) == 0:
                    bilan_32.is_null_3 = True
                if (tcr1_5.montant_n + tcr1_6.montant_n + tcr1_14.montant_n) == 0:
                    bilan_32.is_null_2 = True
                if (tcr1_5.montant_n1 + tcr1_6.montant_n1 + tcr1_14.montant_n1) == 0:
                    bilan_32.is_null_1 = True

                var_2.write({'montant': (tcr_5.montant_n + tcr_6.montant_n)})

                # متوسط فترة التحصيل (يوم)

                bilan_33 = rec.bilan_id.filtered(lambda r: r.sequence == 29)
                bilan_33.write({'year_4': (actif_5.montant_n * 360) / tcr_1.montant_n if tcr_1.montant_n != 0 else 0,
                                'year_3': (actif_5.montant_n1 * 360) / tcr_1.montant_n1 if tcr_1.montant_n1 != 0 else 0,
                                'year_2': (actif1_5.montant_n * 360) / tcr1_1.montant_n if tcr1_1.montant_n != 0 else 0,
                                'year_1': (
                                                      actif1_5.montant_n1 * 360) / tcr1_1.montant_n1 if tcr1_1.montant_n1 != 0 else 0})
                if tcr_1.montant_n == 0:
                    bilan_33.is_null_4 = True
                if tcr_1.montant_n1 == 0:
                    bilan_33.is_null_3 = True
                if tcr1_1.montant_n == 0:
                    bilan_33.is_null_2 = True
                if tcr1_1.montant_n1 == 0:
                    bilan_33.is_null_1 = True

                # متوسط مدة تسهيلات الموردين (يوم)
                bilan_34 = rec.bilan_id.filtered(lambda r: r.sequence == 30)
                bilan_34.write({'year_4': (passif_7.montant_n * 360) / (tcr_5.montant_n + tcr_6.montant_n) if (
                                                                                                                          tcr_5.montant_n + tcr_6.montant_n) != 0 else 0,
                                'year_3': (passif_7.montant_n1 * 360) / (tcr_5.montant_n1 + tcr_6.montant_n1) if (
                                                                                                                             tcr_5.montant_n1 + tcr_6.montant_n1) != 0 else 0,
                                'year_2': (passif1_7.montant_n * 360) / (tcr1_5.montant_n + tcr1_6.montant_n) if (
                                                                                                                             tcr1_5.montant_n + tcr1_6.montant_n) != 0 else 0,
                                'year_1': (passif1_7.montant_n1 * 360) / (tcr1_5.montant_n1 + tcr1_6.montant_n1) if (
                                                                                                                                tcr1_5.montant_n1 + tcr1_6.montant_n1) != 0 else 0,
                                })
                if (tcr_5.montant_n + tcr_6.montant_n) == 0:
                    bilan_34.is_null_4 = True
                if (tcr_5.montant_n1 + tcr_6.montant_n1) == 0:
                    bilan_34.is_null_3 = True
                if (tcr1_5.montant_n + tcr1_6.montant_n) == 0:
                    bilan_34.is_null_2 = True
                if (tcr1_5.montant_n1 + tcr1_6.montant_n1) == 0:
                    bilan_34.is_null_1 = True


class Ratio(models.Model):
    _name = 'crm.ratio'

    name = fields.Char(string='Ratio')
    ratio = fields.Selection(list_ratio, string='Ratio')
    montant_n = fields.Float(string='N')
    montant_n1 = fields.Float(string='N-1')
    lead = fields.Many2one('crm.lead')

class Compterendu(models.Model):
    _name = 'crm.compte.rendu'

    lead_id = fields.Many2one('crm.lead')
    visit_date = fields.Date(string='Date de la visite')
    address = fields.Char(string='Adresse')
    participant_ids = fields.Many2many('res.users', string='Personnes ayant effectuées la visite')
    attachment_ids = fields.Many2many('ir.attachment', string='Photos')
    resume = fields.Text(string='Résumé')


class CrmLead2opportunityPartner(models.TransientModel):
    _inherit = 'crm.lead2opportunity.partner'

    team_lead = fields.Many2one('res.users', string="Chef d'équipe")

    @api.onchange('team_id')
    def _onchange_team_id(self):
        if self.team_id:
            self.team_lead = self.team_id.user_id
            self.user_id = False

    def action_apply(self):
        ctx = self.env.context.copy()
        ctx.update({'geographic_area': self.team_id.geographic_area, 'team_lead': self.team_lead.id})
        self = self.with_context(ctx)
        return super(CrmLead2opportunityPartner, self).action_apply()