from odoo import models, fields, api, _
from io import BytesIO
import numpy as np
import matplotlib
import base64

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




class Lead(models.Model):
    _inherit = 'crm.lead'

    nrc = fields.Char(string='N.RC')
    nif = fields.Char(string='NIF')
    nis = fields.Char(string='NIS')
    date_creation = fields.Date(string='Date de création')
    branch = fields.Many2one('crm.branch', string='Agence')
    secteur = fields.Many2one('crm.secteur', string='Secteur d\'activité')
    activity = fields.Many2one('crm.activity', string='Activité en détails')
    demande_type = fields.Selection([('0', 'Entrer en relation (nouvelle demande)'),
                                     ('1', 'Renouvellement des lignes')], string='Type de demande')
    product = fields.Selection([('0', 'Exploitation'),
                                ('1', 'Investissement'),
                                ('2', 'Leasing')], string='Type de ligne de credit')
    product_ids = fields.Many2many('crm.product', string='Lignes de credit')
    num_compte = fields.Char(string='N. Compte')
    montant_sollicite = fields.Float(string='Montant sollicité')
    file_tcr = fields.Binary(string='TCR N, N-1')
    file_tcr1 = fields.Binary(string='TCR N, N-1')
    file_actif = fields.Binary(string='Actif N, N-1')
    file_passif = fields.Binary(string='Passif N, N-1')
    tcr_id = fields.Many2one('import.ocr.tcr', 'TCR')
    passif_id = fields.Many2one('import.ocr.passif', 'Passif')
    actif_id = fields.Many2one('import.ocr.actif', 'Actif')

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
    confrere_ids = fields.One2many('crm.confrere', 'lead_id', string='Confrere')
    has_importation = fields.Boolean(string='Faites-vous de l`importation ?')
    importation_ids = fields.One2many('crm.importation', 'lead_id')
    has_appro = fields.Boolean(string='Approvisionnement auprès du marché local')
    appro_ids = fields.One2many('crm.appro', 'lead_id')
    plan_ids = fields.One2many('crm.plan', 'lead_id')
    financement_ids = fields.One2many('crm.financement', 'lead_id')
    document_ids = fields.One2many('ir.attachment', 'lead_id')

    garanties = fields.Html(string='Garanties proposées')

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
                'target': 'new',
            }

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
    resume = fields.Text(string='Résumé')
