from odoo import models, fields, api, _

from datetime import datetime
from io import BytesIO
import numpy as np
import matplotlib
import base64

from odoo.http import request
from odoo.exceptions import UserError,ValidationError

matplotlib.use('Agg')
from matplotlib import pyplot as plt
import xlsxwriter
import openpyxl

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

Doc_List = [
    ('1', 'Bilans fiscal N, N-1'),
    ('2', 'Bilan fiscal N-2'),
    ('3', 'Registre de commerce'),
    ('4', 'NIF'),
    ('5', 'NIS'),
    ('6', 'Statut de création'),
    ('7', 'Dernier statut modificatif'),
    ('8', 'Contrat de location / acte de propriété du siège social'),
    ('9', 'Autorisation de consultation CDR')]
class Lead(models.Model):
    _inherit = 'crm.lead'

    nrc = fields.Char(string='N.RC')
    nif = fields.Char(string='NIF')
    nis = fields.Char(string='NIS')
    date_creation = fields.Date(string='Date de création')
    branch = fields.Many2one('crm.branch', string='Agence')
    secteur = fields.Many2one('crm.secteur', string='Secteur d\'activité')
    activity = fields.Many2one('crm.activity', string='Activité en détails', domain="[('secteur', '=', secteur)]")
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
    confrere_file = fields.Binary(string='Fichier des crédit bancaire auprès des confrères')
    importation_file = fields.Binary(string='Fichier d\'importation')
    appro_file = fields.Binary(string='Fichier d\'Approvisionnement auprès du marché local')
    plan_file = fields.Binary(string='Fichier de plan des charges')
    has_importation = fields.Boolean(string='Faites-vous de l`importation ?')
    importation_ids = fields.One2many('crm.importation', 'lead_id')
    has_appro = fields.Boolean(string='Approvisionnement auprès du marché local')
    appro_ids = fields.One2many('crm.appro', 'lead_id')
    plan_ids = fields.One2many('crm.plan', 'lead_id')
    financement_ids = fields.One2many('crm.financement', 'lead_id')
    document_ids = fields.One2many('ir.attachment', 'lead_id')
    garanties = fields.Html(string='Garanties proposées')
    crv_nbr = fields.Char(string='CRV', compute='compute_nbr_crv')
    representant = fields.Char(string='Representant')
    forme_jur = fields.Many2one('crm.forme.juridique', string='Forme Juridique')
    expected_revenue = fields.Monetary('PNB espéré', currency_field='company_currency', tracking=True)
    demande_description = fields.Html(string='Description de la demande')
    activity_description = fields.Html(string='Description d\'activité')
    product_service = fields.Html(string='Produit / Service')
    client_market = fields.Html(string='Marché du client')
    concurrent = fields.Html(string='Principaux concurrents')
    cycle_expoitation = fields.Html(string='Cycle d\'exploitation')
    avis_ca = fields.Html(string='Avis CA')
    avis_dmc = fields.Html(string='Avis DMC')


    @api.model
    def create(self, vals):
        res = super(Lead, self).create(vals)
        document_dict = {item[0]: item[1] for item in Doc_List}
        for item in document_dict:
            document = {'lead_id': res.id,
                         'list_doc': item,
                         'datas': False,
                         'type': 'binary',
                          'create_uid': self.env.user,
                          'name': document_dict.get(item, '')}
            self.env['ir.attachment'].create(document)
        return res
    def compute_nbr_crv(self):
        for rec in self:
            has_crv = self.env['crm.compte.rendu'].search([('lead_id', '=', rec.id)])
            if not has_crv:
                rec.crv_nbr = 'Aucun CRV'
            else:
                rec.crv_nbr = str(len(has_crv)) + 'CRV'
    def convert_dossier(self):
        for rec in self:
            if self.env.user.has_group('crm_portal.crm_portal_group_validator'):
                final_stage = self.env['crm.stage'].search([('is_won', '=', True)])
                rec.stage_id = final_stage.id
            else:
                raise ValidationError(_('Vous n\'etes pas autorisé à valider le dossier'))

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


    def open_calcul_mecanisme(self):
        for rec in self:
            print('mecanisme')
            view_id = self.env.ref('crm_portal.crm_calcul_views_wizard_form').id
            res_id = self.env['crm.wizard.calcul'].search([('lead_id', '=', rec.id)])
            if not res_id:
                res_id = self.env['crm.wizard.calcul'].create({'lead_id': rec.id})
            for line in rec.financement_ids:
                line.write({'wizard_id': res_id.id})
            return {
                'name': 'Information',
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'crm.wizard.calcul',
                'res_id': res_id.id,
                'view_id': view_id,
                'target': 'new',
            }
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

    def upload_confrere(self):
        self.ensure_one()
        wb = openpyxl.load_workbook(filename=BytesIO(base64.b64decode(self.confrere_file)), read_only=True)
        ws = wb.active
        search = self.confrere_ids.unlink()
        count = 0
        for record in ws.iter_rows(min_row=2, max_row=None, min_col=None, max_col=None, values_only=True):
            count += 1
            try:
                print(record)
                self.env['crm.confrere'].create({
                    'lead_id': self.id,
                    'banque': self.env['crm.banque'].search([('name', '=', record[0])]).id,
                    'credit': self.env['crm.product'].search([('name', '=', record[1])]).id,
                    'montant': record[2],
                    'condition': record[3],
                    'date_echeance': record[4],
                    'garantie': record[5],
                })
            except:
                UserError('Veuillez verifier le fichier attaché')

    def download_confrere(self):
        self.ensure_one()

        # Générer le fichier Excel
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet()

        # Ajout des en-têtes des colonnes
        headers = ['Banque', 'Type de crédit', 'Montant', 'Condition', 'Échéance ligne', 'Garanties']
        for i, header in enumerate(headers):
            worksheet.write(0, i, header)

        # Ajout des données du champ one2many
        row = 1
        for line in self.confrere_ids:
            worksheet.write(row, 0, line.banque.name)
            worksheet.write(row, 1, line.credit.name)
            worksheet.write(row, 2, line.montant)
            worksheet.write(row, 3, line.condition)
            worksheet.write(row, 4, line.date_echeance.strftime('%d-%m-%Y'))
            worksheet.write(row, 5, line.garantie)
            row += 1

        # Clôture du fichier Excel
        workbook.close()
        output.seek(0)

        # Encoder le fichier en base64
        result = base64.b64encode(output.read())

        # Obtenir l'URL de base
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')

        # Créer une pièce jointe
        attachment_obj = self.env['ir.attachment']
        attachment_id = attachment_obj.create({
            'name': "confrere_report.xlsx",
            'datas': result,
            'res_model': self._name,
            'res_id': self.id,
            'type': 'binary',
        })

        # Préparer l'URL de téléchargement
        download_url = '/web/content/' + str(attachment_id.id) + '?download=true'

        # Retourner l'action pour télécharger le fichier
        return {
            "type": "ir.actions.act_url",
            "url": str(base_url) + str(download_url),
            "target": "new",
        }

    def upload_importation(self):
        self.ensure_one()
        wb = openpyxl.load_workbook(filename=BytesIO(base64.b64decode(self.importation_file)), read_only=True)
        ws = wb.active
        search = self.importation_ids.unlink()
        count = 0
        for record in ws.iter_rows(min_row=2, max_row=None, min_col=None, max_col=None, values_only=True):
            count += 1
            print(record)
            if isinstance(record[2], str) and record[2] is not None:
                if '/' in record[2]:
                    payment_types_list = [ptype.strip() for ptype in record[2].split(' / ')]
                    payment_type_records = self.env['crm.payment.mode'].search([('name', 'in', payment_types_list)])
                else:
                    payment_type_records = self.env['crm.payment.mode'].search([('name', '=', record[2])])
            else:
                payment_type_records = False
            if isinstance(record[5], str) and record[5] is not None:
                date = datetime.strptime(record[5], '%d-%m-%Y')
            else:
                date = False
            importation = self.env['crm.importation'].create({
                'lead_id': self.id,
                'fournisseur': record[0],
                'pays': self.env['res.country'].search([('name', '=', record[1])]).id,
                'payment': [(6, 0, payment_type_records.ids)] if payment_type_records else False,
                'delai': record[3],
                'montant': record[4],
                'programme_importation': date,
                'delai_livraison': record[6],
            })

    def download_importation(self):
        self.ensure_one()

        # Générer le fichier Excel
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet()

        # Ajout des en-têtes des colonnes
        headers = ['Fournisseur', 'Pays', 'Mode de paiement', 'Délai de paiement (en jours)', 'Montant prévisionnel en DA', 'Programme d\'importation', 'Délais de livraison (entre le lancement de la commande et le dédouanement de la marchandise) en jours']
        for i, header in enumerate(headers):
            worksheet.write(0, i, header)
        # Ajout des données du champ one2many
        row = 1
        for line in self.importation_ids:
            payment_type_names = line.payment.mapped('name')
            worksheet.write(row, 0, line.fournisseur or '')
            worksheet.write(row, 1, line.pays.name or '')
            worksheet.write(row, 2, ' / '.join(payment_type_names) or '')
            worksheet.write(row, 3, line.delai or '')
            worksheet.write(row, 4, line.montant or '')
            worksheet.write(row, 5, line.programme_importation.strftime('%d-%m-%Y') if line.programme_importation else '')
            worksheet.write(row, 6, line.delai_livraison or '')
            row += 1

        # Clôture du fichier Excel
        workbook.close()
        output.seek(0)

        # Encoder le fichier en base64
        result = base64.b64encode(output.read())

        # Obtenir l'URL de base
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')

        # Créer une pièce jointe
        attachment_obj = self.env['ir.attachment']
        attachment_id = attachment_obj.create({
            'name': "importation_report.xlsx",
            'datas': result,
            'res_model': self._name,
            'res_id': self.id,
            'type': 'binary',
        })

        # Préparer l'URL de téléchargement
        download_url = '/web/content/' + str(attachment_id.id) + '?download=true'

        # Retourner l'action pour télécharger le fichier
        return {
            "type": "ir.actions.act_url",
            "url": str(base_url) + str(download_url),
            "target": "new",
        }
    def upload_appro(self):
        self.ensure_one()
        wb = openpyxl.load_workbook(filename=BytesIO(base64.b64decode(self.appro_file)), read_only=True)
        ws = wb.active
        search = self.appro_ids.unlink()
        count = 0
        for record in ws.iter_rows(min_row=2, max_row=None, min_col=None, max_col=None, values_only=True):

            try:
                count += 1
                payment_types_list = [ptype.strip() for ptype in record[2].split(' / ')]
                payment_type_records = self.env['crm.type.payment'].search([('name', 'in', payment_types_list)])
                payment = [(4, 0, payment) for payment in payment_type_records.ids]
                if isinstance(record[5], str) and record[5] is not None:
                    date = datetime.strptime(record[5], '%d-%m-%Y')
                else:
                    date = False
                importation = self.env['crm.appro'].create({
                    'lead_id': self.id,
                    'marchandise': record[0],
                    'fournisseur': record[1],
                    'payment': [(6, 0, payment_type_records.ids)],
                    'delai': record[3],
                    'montant': record[4],
                    'programme_importation': date,
                })
            except:
                UserError('Veuillez verifier le fichier attaché')

    def download_appro(self):
        self.ensure_one()

        # Générer le fichier Excel
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet()

        # Ajout des en-têtes des colonnes
        headers = ['Designation de marchandises / MP', 'Fournisseur', 'Mode de paiement', 'Délai de paiement (en jours)', 'Montant prévisionnel', 'Approvisionnement auprès du marché local']
        for i, header in enumerate(headers):
            worksheet.write(0, i, header)
        # Ajout des données du champ one2many
        row = 1
        for line in self.appro_ids:
            payment_type_names = line.payment.mapped('name')
            worksheet.write(row, 0, line.marchandise)
            worksheet.write(row, 1, line.fournisseur)
            worksheet.write(row, 2, ' / '.join(payment_type_names))
            worksheet.write(row, 3, line.delai)
            worksheet.write(row, 4, line.montant)
            worksheet.write(row, 5, line.programme_importation.strftime('%d-%m-%Y'))
            row += 1

        # Clôture du fichier Excel
        workbook.close()
        output.seek(0)

        # Encoder le fichier en base64
        result = base64.b64encode(output.read())

        # Obtenir l'URL de base
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')

        # Créer une pièce jointe
        attachment_obj = self.env['ir.attachment']
        attachment_id = attachment_obj.create({
            'name': "appro_report.xlsx",
            'datas': result,
            'res_model': self._name,
            'res_id': self.id,
            'type': 'binary',
        })

        # Préparer l'URL de téléchargement
        download_url = '/web/content/' + str(attachment_id.id) + '?download=true'

        # Retourner l'action pour télécharger le fichier
        return {
            "type": "ir.actions.act_url",
            "url": str(base_url) + str(download_url),
            "target": "new",
        }
    def upload_plan(self):
        self.ensure_one()
        wb = openpyxl.load_workbook(filename=BytesIO(base64.b64decode(self.plan_file)), read_only=True)
        ws = wb.active
        search = self.plan_ids.unlink()
        count = 0
        for record in ws.iter_rows(min_row=2, max_row=None, min_col=None, max_col=None, values_only=True):
                count += 1
                if isinstance(record[6], str) and record[6] is not None:
                    date = datetime.strptime(record[6], '%d-%m-%Y')
                else:
                    date = False
                importation = self.env['crm.plan'].create({
                    'lead_id': self.id,
                    'type_marche': self.env['crm.type.marche'].search([('name', '=', record[0])]).id,
                    'client': record[1],
                    'dom_bancaire':  self.env['crm.banque'].search([('name', '=', record[2])]).id,
                    'natissement':  'oui' if record[3] in ['oui', 'Oui'] else 'non',
                    'montant':  record[4],
                    'objet':  record[5],
                    'date_obs':  date,
                    'delai':  record[7],
                    'taux':  record[8],
                    'montant_facture':  record[9],
                    'montant_encaisse':  record[10],
                    'montant_fact_no_encaisse':  record[11],
                    'montant_no_fact_realise':  record[12],
                })

    def download_plan(self):
        self.ensure_one()

        # Générer le fichier Excel
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet()

        # Ajout des en-têtes des colonnes
        headers = ['Type de marché', 'Client',
                   'Dom. Bancaire', 'Natissement',
                   'Montant H.T DA', 'Objet du marché',
                   'Date ODS', 'Délai d`excution (en jours)',
                   'Taux d`avancement', 'Montant facturé H.T',
                   'Montant encaissé H.T', 'Montant facturé non-encaissé H.T',
                   'Montant réalisé non-facturé H.T']
        for i, header in enumerate(headers):
            worksheet.write(0, i, header)
        # Ajout des données du champ one2many
        row = 1
        for line in self.plan_ids:
            payment_type_names = line.payment.mapped('name')
            worksheet.write(row, 0, line.type_marche.name)
            worksheet.write(row, 1, line.client)
            worksheet.write(row, 2, line.dom_bancaire.name)
            worksheet.write(row, 3, line.natissement)
            worksheet.write(row, 4, line.montant)
            worksheet.write(row, 5, line.objet)
            worksheet.write(row, 6, line.date_obs.strftime('%d-%m-%Y'))
            worksheet.write(row, 7, line.delai)
            worksheet.write(row, 8, line.taux)
            worksheet.write(row, 9, line.montant_facture)
            worksheet.write(row, 10, line.montant_encaisse)
            worksheet.write(row, 11, line.montant_fact_no_encaisse)
            worksheet.write(row, 12, line.montant_no_fact_realise)
            row += 1

        # Clôture du fichier Excel
        workbook.close()
        output.seek(0)

        # Encoder le fichier en base64
        result = base64.b64encode(output.read())

        # Obtenir l'URL de base
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')

        # Créer une pièce jointe
        attachment_obj = self.env['ir.attachment']
        attachment_id = attachment_obj.create({
            'name': "plan_report.xlsx",
            'datas': result,
            'res_model': self._name,
            'res_id': self.id,
            'type': 'binary',
        })

        # Préparer l'URL de téléchargement
        download_url = '/web/content/' + str(attachment_id.id) + '?download=true'

        # Retourner l'action pour télécharger le fichier
        return {
            "type": "ir.actions.act_url",
            "url": str(base_url) + str(download_url),
            "target": "new",
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
