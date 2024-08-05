from odoo import models, fields, api, _


class FormeJuridique(models.Model):
    _name = 'crm.forme.juridique'
    _description = 'Liste des forme juridique'

    name = fields.Char(string='Forme Juridique')


class Secteur(models.Model):
    _name = 'crm.secteur'
    _description = 'Liste des secteurs'

    name = fields.Char(string='Secteur d\'activité')
    activity_ids = fields.One2many('crm.activity', 'secteur', string='Liste des activités')


class Activity(models.Model):
    _name = 'crm.activity'
    _description = 'Liste des activités'

    name = fields.Char(string='Activité en détails')
    secteur = fields.Many2one('crm.secteur', string='Secteur')


class Branch(models.Model):
    _name = 'crm.branch'
    _description = 'Liste des agence'

    name = fields.Char(string='Nom')
    wilaya = fields.Many2one('res.country.state', string='Wilaya')


class Product(models.Model):
    _name = 'crm.product'

    name = fields.Char(string='Type')

original = [
    ['Mixte ou appartenant a un grand groupe',10],
    ['National', 7],
    ['Etranger', 6]
]

forme = [
    ['SNC et personne physique',10],
    ['SPA',8],
    ['SARL & EURL',6]
]

actiona = [
    ['Familiale',15],
    ['Autre',10]
]

bool_list = [
    ['Assurée',5],
    ['Non assurée',0]
]

comp_list = [
    ['Compétence avérée',15],
    ['Moyenne',8],
    ['Non avéré',0]
]
exp_list = [
    ['Bonne',15],
    ['Moyenne',8],
    ['Faible',3]
]

activite_list = [
    ['En expansion',30],
    ['En stagnation',10],
    ['En régression',5]
]

influence_list = [
    ['Forte',15],
    ['Moyenne',8],
    ['Faible',5]
]

anciente_list = [
    ['Plus de 10 ans', 20],
    ['Entre 05 et 10 ans', 15],
    ['De 02 a 5 ans', 10],
    ['Moins de 02 ans', 5]
]

concurrence_list = [
    ['Faible',20],
    ['Modérée',10],
    ['Rude',5]
]

source_appro_list = [
    ['Diversifées',15],
    ['Restreintes',5]
]

produit_list = [
    ['Production diversifées', 10],
    ['Production restreintes', 5]
]

flexibilite_list = [
    ['Réelle', 15],
    ['Possible', 5],
    ['Inexistante', 0]
]
solicitude_list = [
    ['Bonne', 30],
    ['Moyenne', 15],
    ['Absente', 5]
]
situation_list = [
    ['Appréciable',30],
    ['Moyenne', 15],
    ['Faible', 5]
]

mouv_list = [
    ['Bons (> = 60%)', 60],
    ['De 40% a 60%', 40],
    ['De 25% a 40%', 30],
    ['De 10 % a 25%', 20],
    ['Médiocres', 5]
]

garanties_list = [
    ['Financière/immobilière 1er rang', 50],
    ['Immobilière sup a 1er rang', 45],
    ['Bancaire', 40],
    ['Organisme de garantie', 40],
    ['Caution personnelle', 25],
    ['Pas de proposition', 0]
]

incident_list = [
    ['Inexistants', 30],
    ['01 incident par an', 20],
    ['02 incidents par an', 15],
    ['03 incidents par an',10],
    ['Fréquents', 0]
]

conduite_list = [
    ['Client très respectueux', 30],
    ['Client correct', 20],
    ['Client incorrect', 0]
]

dette_fisc = [
    ['Apurée', 40],
    ['Echelonnée (échéancier respecté)', 20],
    ['Echelonnée (échéancier non respecté)', 5],
    ['Non apurée', 0]
]
dette_parafisc = [
    ['Apurée', 30],
    ['Echelonnée (échéancier respecté)', 20],
    ['Echelonnée (échéancier non respecté)', 5],
    ['Non apurée', 0]
]
position_list = [
    ['Harmonieuse', 30],
    ['Conflictuelle. Sans incidence activité', 10],
    ['Conflictuelle. Avec incidence activité', 0]

]

source_remb = [
    ['A partir de l\'activité courante de l\'entreprise', 40],
    ['Source de remboursement hors activité', 20],
    ['Mise en jeu des garanties', 5]
]

part_profit = [
    ['Moins de 0.01%', 15],
    ['Entre 0.01% et 0.1%', 20],
    ['Entre 0.1% et 0.5%', 25],
    ['Plus de 0.5%', 30]
]


class originalCapital(models.Model):
    _name = 'risk.original.capital'
    _description = 'original du capital et sa ponderation'

    name = fields.Char(string='Original du capital')
    ponderation = fields.Integer(string='Pondération')
    critere = fields.Many2one('risk.critere.qualitatif', string='critere')

class Actionnariat(models.Model):
    _name = 'risk.actionnariat'
    _description = 'actionnariat et sa ponderation'

    name = fields.Char(string='Actionnariat')
    ponderation = fields.Integer(string='Pondération')
    critere = fields.Many2one('risk.critere.qualitatif', string='critere')

class FormeJur(models.Model):
    _name = 'risk.forme.jur'
    _description = 'forme juridique et sa ponderation'

    name = fields.Char(string='Forme juridique')
    ponderation = fields.Integer(string='Pondération')
    critere = fields.Many2one('risk.critere.qualitatif', string='critere')


class RempSuccession(models.Model):
    _name = 'risk.remplacement.succession'
    _description = 'Remplacement et succession et sa ponderation'

    name = fields.Char(string='Remplacement et succession')
    ponderation = fields.Integer(string='Pondération')
    critere = fields.Many2one('risk.critere.qualitatif', string='critere')


class Competence(models.Model):
    _name = 'risk.competence'
    _description = 'Compétence et sa ponderation'

    name = fields.Char(string='Compétence')
    ponderation = fields.Integer(string='Pondération')
    critere = fields.Many2one('risk.critere.qualitatif', string='critere')


class Experience(models.Model):
    _name = 'risk.experience'
    _description = 'Expérience et sa ponderation'

    name = fields.Char(string='Expérience')
    ponderation = fields.Integer(string='Pondération')
    critere = fields.Many2one('risk.critere.qualitatif', string='critere')


class SoutienEtatique(models.Model):
    _name = 'risk.soutien.etatique'
    _description = 'Soutien étatique et sa ponderation'

    name = fields.Char(string='Soutien étatique')
    ponderation = fields.Integer(string='Pondération')
    critere = fields.Many2one('risk.critere.qualitatif', string='critere')


class Activite(models.Model):
    _name = 'risk.activite'
    _description = 'Activité et sa ponderation'

    name = fields.Char(string='Activité')
    ponderation = fields.Integer(string='Pondération')
    critere = fields.Many2one('risk.critere.qualitatif', string='critere')


class InfluenceTech(models.Model):
    _name = 'risk.influence.tech'
    _description = 'Influence technologique et sa ponderation'

    name = fields.Char(string='Influence technologique')
    ponderation = fields.Integer(string='Pondération')
    critere = fields.Many2one('risk.critere.qualitatif', string='critere')


class Anciennete(models.Model):
    _name = 'risk.anciennete'
    _description = 'Ancienneté et sa ponderation'

    name = fields.Char(string='Ancienneté')
    ponderation = fields.Integer(string='Pondération')
    critere = fields.Many2one('risk.critere.qualitatif', string='critere')


class Concurrence(models.Model):
    _name = 'risk.concurrence'
    _description = 'Concurrence et sa ponderation'

    name = fields.Char(string='Concurrence')
    ponderation = fields.Integer(string='Pondération')
    critere = fields.Many2one('risk.critere.qualitatif', string='critere')


class SourceAppro(models.Model):
    _name = 'risk.source.appro'
    _description = 'Sources d\'approvisionnement et sa ponderation'

    name = fields.Char(string='Sources d\'approvisionnement')
    ponderation = fields.Integer(string='Pondération')
    critere = fields.Many2one('risk.critere.qualitatif', string='critere')


class Produit(models.Model):
    _name = 'risk.produit'
    _description = 'Produit de l\'entreprise et sa ponderation'

    name = fields.Char(string='Produit de l\'entreprise')
    ponderation = fields.Integer(string='Pondération')
    critere = fields.Many2one('risk.critere.qualitatif', string='critere')


class Flexibilite(models.Model):
    _name = 'risk.flexibilite'
    _description = 'Flexibilité et sa ponderation'

    name = fields.Char(string='Flexibilité')
    ponderation = fields.Integer(string='Pondération')
    critere = fields.Many2one('risk.critere.qualitatif', string='critere')


class Sollicitude(models.Model):
    _name = 'risk.sollicitude'
    _description = 'Sollicitude des confrères et sa ponderation'

    name = fields.Char(string='Sollicitude des confrères')
    ponderation = fields.Integer(string='Pondération')
    critere = fields.Many2one('risk.critere.qualitatif', string='critere')


class Situation(models.Model):
    _name = 'risk.situation'
    _description = 'Situation patrimoniale des actionnaires et sa ponderation'

    name = fields.Char(string='Situation patrimoniale des actionnaires')
    ponderation = fields.Integer(string='Pondération')
    critere = fields.Many2one('risk.critere.qualitatif', string='critere')


class Mouvement(models.Model):
    _name = 'risk.mouvement'
    _description = 'Mouvements confiés et sa ponderation'

    name = fields.Char(string='Mouvements confiés')
    ponderation = fields.Integer(string='Pondération')
    critere = fields.Many2one('risk.critere.qualitatif', string='critere')


class Garanties(models.Model):
    _name = 'risk.garanties'
    _description = 'Garanties proposées et sa ponderation'

    name = fields.Char(string='Garanties proposées')
    ponderation = fields.Integer(string='Pondération')
    critere = fields.Many2one('risk.critere.qualitatif', string='critere')


class incident(models.Model):
    _name = 'risk.incident'
    _description = 'Incidents de paiement et sa ponderation'

    name = fields.Char(string='Incidents de paiement')
    ponderation = fields.Integer(string='Pondération')
    critere = fields.Many2one('risk.critere.qualitatif', string='critere')


class conduite(models.Model):
    _name = 'risk.conduite'
    _description = 'Conduite du client et sa ponderation'

    name = fields.Char(string='Conduite du client')
    ponderation = fields.Integer(string='Pondération')
    critere = fields.Many2one('risk.critere.qualitatif', string='critere')


class DetteFisc(models.Model):
    _name = 'risk.dette.fisc'
    _description = 'Dette fiscale et sa ponderation'

    name = fields.Char(string='Dette fiscale')
    ponderation = fields.Integer(string='Pondération')
    critere = fields.Many2one('risk.critere.qualitatif', string='critere')


class DetteParafisc(models.Model):
    _name = 'risk.dette.parafisc'
    _description = 'Dette parafiscale et sa ponderation'

    name = fields.Char(string='Dette parafiscale')
    ponderation = fields.Integer(string='Pondération')
    critere = fields.Many2one('risk.critere.qualitatif', string='critere')


class PositionAdmin(models.Model):
    _name = 'risk.position.admin'
    _description = 'Position envers autres administrations et sa ponderation'

    name = fields.Char(string='Position envers autres administrations')
    ponderation = fields.Integer(string='Pondération')
    critere = fields.Many2one('risk.critere.qualitatif', string='critere')


class SourceRemb(models.Model):
    _name = 'risk.source.remb'
    _description = 'Sources de remboursement et sa ponderation'

    name = fields.Char(string='Sources de remboursement')
    ponderation = fields.Integer(string='Pondération')
    critere = fields.Many2one('risk.critere.qualitatif', string='critere')


class PartProfil(models.Model):
    _name = 'risk.part.profil'
    _description = 'Part du profit de la contrepartie au total PNB et sa ponderation'

    name = fields.Char(string='Part du profit de la contrepartie au total PNB')
    ponderation = fields.Integer(string='Pondération')
    critere = fields.Many2one('risk.critere.qualitatif', string='critere')


class CritereQualitatif(models.Model):
    _name = 'risk.critere.qualitatif'

    name = fields.Char()
    date = fields.Date(string='Date')
    original_capital = fields.One2many('risk.original.capital', 'critere', string='Original du capital')
    actionnariat = fields.One2many('risk.actionnariat', 'critere', string='Actionnariat')
    forme_jur = fields.One2many('risk.forme.jur', 'critere', string='Forme juridique')
    remp_succession = fields.One2many('risk.remplacement.succession', 'critere', string='Remplacement et succession')
    competence = fields.One2many('risk.competence', 'critere', string='Competence')
    experience = fields.One2many('risk.experience', 'critere', string='Expérience')
    soutien_etatic = fields.One2many('risk.soutien.etatique', 'critere', string='Soutien étatique')
    activite = fields.One2many('risk.activite', 'critere', string='Activité')
    influence_tech = fields.One2many('risk.influence.tech', 'critere', string='Influence technologique')
    anciennete = fields.One2many('risk.anciennete', 'critere', string='Ancienneté')
    concurrence = fields.One2many('risk.concurrence', 'critere', string='Concurrence')
    source_appro = fields.One2many('risk.source.appro', 'critere', string='Sources d\'approvisionnement')
    produit = fields.One2many('risk.produit', 'critere', string='Produit de l\'entreprise')
    flexibilite = fields.One2many('risk.flexibilite', 'critere', string='Flexibilité')
    sollicitude = fields.One2many('risk.sollicitude', 'critere', string='Sollicitude des confrères')
    situation = fields.One2many('risk.situation', 'critere', string='Situation patrimoniale des actionnaires ')
    mouvement = fields.One2many('risk.mouvement', 'critere', string='Mouvements confiés')
    garanties = fields.One2many('risk.garanties', 'critere', string='Garanties proposées')
    incident = fields.One2many('risk.incident', 'critere', string='Incidents de paiement')
    conduite = fields.One2many('risk.conduite', 'critere', string='Conduite du client')
    dette_fisc = fields.One2many('risk.dette.fisc', 'critere', string='Dette fiscale')
    dette_parafisc = fields.One2many('risk.dette.parafisc', 'critere', string='Dette parafiscale')
    position_admin = fields.One2many('risk.position.admin', 'critere', string='Position envers autres administrations')
    source_remb = fields.One2many('risk.source.remb', 'critere', string='Sources de remboursement')
    part_profil = fields.One2many('risk.part.profil', 'critere', string='Part du profit de la contrepartie au total PNB')

    @api.model
    def create(self, vals):
        res = super(CritereQualitatif, self).create(vals)
        for item in original:
            self.env['risk.original.capital'].create({'name': item[0],'ponderation': item[1], 'critere': res.id})
        for item in forme:
            self.env['risk.forme.jur'].create({ 'name': item[0],'ponderation': item[1], 'critere': res.id})
        for item in actiona:
            self.env['risk.actionnariat'].create({ 'name': item[0],'ponderation': item[1], 'critere': res.id})
        for item in bool_list:
            self.env['risk.remplacement.succession'].create({ 'name': item[0],'ponderation': item[1], 'critere': res.id})
            self.env['risk.soutien.etatique'].create({ 'name': item[0],'ponderation': item[1], 'critere': res.id})
        for item in comp_list:
            self.env['risk.competence'].create({ 'name': item[0],'ponderation': item[1], 'critere': res.id})
        for item in exp_list:
            self.env['risk.experience'].create({ 'name': item[0],'ponderation': item[1], 'critere': res.id})
        for item in activite_list:
            self.env['risk.activite'].create({ 'name': item[0],'ponderation': item[1], 'critere': res.id})
        for item in influence_list:
            self.env['risk.influence.tech'].create({ 'name': item[0],'ponderation': item[1], 'critere': res.id})
        for item in anciente_list:
            self.env['risk.anciennete'].create({ 'name': item[0],'ponderation': item[1], 'critere': res.id})
        for item in concurrence_list:
            self.env['risk.concurrence'].create({ 'name': item[0],'ponderation': item[1], 'critere': res.id})
        for item in source_appro_list:
            self.env['risk.source.appro'].create({ 'name': item[0],'ponderation': item[1], 'critere': res.id})
        for item in produit_list:
            self.env['risk.produit'].create({ 'name': item[0],'ponderation': item[1], 'critere': res.id})
        for item in flexibilite_list:
            self.env['risk.flexibilite'].create({ 'name': item[0],'ponderation': item[1], 'critere': res.id})
        for item in solicitude_list:
            self.env['risk.sollicitude'].create({ 'name': item[0],'ponderation': item[1], 'critere': res.id})
        for item in situation_list:
            self.env['risk.situation'].create({ 'name': item[0],'ponderation': item[1], 'critere': res.id})
        for item in mouv_list:
            self.env['risk.mouvement'].create({ 'name': item[0],'ponderation': item[1], 'critere': res.id})
        for item in garanties_list:
            self.env['risk.garanties'].create({ 'name': item[0],'ponderation': item[1], 'critere': res.id})
        for item in incident_list:
            self.env['risk.incident'].create({ 'name': item[0],'ponderation': item[1], 'critere': res.id})
        for item in conduite_list:
            self.env['risk.conduite'].create({ 'name': item[0],'ponderation': item[1], 'critere': res.id})
        for item in dette_fisc:
            self.env['risk.dette.fisc'].create({ 'name': item[0],'ponderation': item[1], 'critere': res.id})
            self.env['risk.dette.parafisc'].create({ 'name': item[0],'ponderation': item[1], 'critere': res.id})
        for item in position_list:
            self.env['risk.position.admin'].create({ 'name': item[0],'ponderation': item[1], 'critere': res.id})
        for item in source_remb:
            self.env['risk.source.remb'].create({ 'name': item[0],'ponderation': item[1], 'critere': res.id})
        for item in part_profit:
            self.env['risk.part.profil'].create({ 'name': item[0],'ponderation': item[1], 'critere': res.id})
        return res


class Bank(models.Model):
    _name = 'crm.banque'

    name = fields.Char()
    code = fields.Char()


class TypeCredit(models.Model):
    _name = 'crm.credit'

    name = fields.Char()
    code = fields.Char()


class Payment(models.Model):
    _name = 'crm.payment.mode'

    name = fields.Char()


class PaymentType(models.Model):
    _name = 'crm.type.payment'

    name = fields.Char()


class MarcheType(models.Model):
    _name = 'crm.type.marche'

    name = fields.Char()


class FinType(models.Model):
    _name = 'crm.type.financement'

    name = fields.Char()


class Confrere(models.Model):
    _name = 'crm.confrere'

    banque = fields.Many2one('crm.banque', string='Banque')
    credit = fields.Many2one('crm.product', string='Type de crédit')
    montant = fields.Float(string='montant')
    condition = fields.Char(string='Condition')
    date_echeance = fields.Char(string='Échéance ligne')
    garantie = fields.Char(string='Garanties')
    lead_id = fields.Many2one('crm.lead', string='')


class Importation(models.Model):
    _name = 'crm.importation'

    fournisseur = fields.Char(string='Fournisseur')
    pays = fields.Many2one('res.country', string='Pays')
    payment = fields.Many2many('crm.payment.mode', string='Mode de paiement')
    delai = fields.Integer(string='Délai de paiement (en jours)')
    delai_livraison = fields.Integer(string='Délais de livraison (entre le lancement de la commande et le dédouanement de la marchandise) en jours')
    montant = fields.Float(string='Montant prévisionnel en DA')
    programme_importation = fields.Date(string='Programme d\'importation')
    lead_id = fields.Many2one('crm.lead', string='')


class Appro(models.Model):
    _name = 'crm.appro'

    marchandise = fields.Char(string='Designation de marchandises / MP')
    fournisseur = fields.Char(string='Fournisseur')
    payment = fields.Many2many('crm.type.payment', string='Mode de paiement')
    delai = fields.Integer(string='Délai de paiement (en jours)')
    montant = fields.Float(string='Montant prévisionnel')
    programme_importation = fields.Date(string='Approvisionnement auprès du marché local ')
    lead_id = fields.Many2one('crm.lead', string='')


class Plan(models.Model):
    _name = 'crm.plan'

    type_marche = fields.Many2one('crm.type.marche', string='Type de marché')
    client = fields.Char(string='Client')
    dom_bancaire = fields.Many2one('crm.banque', string='Dom. Bancaire')
    natissement = fields.Selection([('oui', 'Oui'),
                                    ('non', 'Non')],string='Natissement')
    montant = fields.Float(string='Montant H.T DA')
    objet = fields.Html(string='Objet du marché')
    date_obs = fields.Date(string='Date ODS')
    delai = fields.Integer(string='Délai d`excution (en jours)')
    taux = fields.Float(string='Taux d`avancement')
    montant_facture = fields.Float(string='Montant facturé H.T')
    montant_encaisse = fields.Float(string='Montant encaissé H.T')
    montant_fact_no_encaisse = fields.Float(string='Montant facturé non-encaissé H.T')
    montant_no_fact_realise = fields.Float(string='Montant réalisé non-facturé H.T')
    lead_id = fields.Many2one('crm.lead', string='')


class Financement(models.Model):
    _name = 'crm.financement'

    type_fin = fields.Many2one('crm.type.financement', string='Type de financement')
    montant = fields.Float(string='Montant')
    utilisation = fields.Html(string='Utilisation')
    autorisation_actuel = fields.Char(string='Autorisation actuelle')
    validite = fields.Date(string='Validité de la ligne')
    new_plafond = fields.Float(string='Plafond demandé')
    lead_id = fields.Many2one('crm.lead', string='')

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

class Doc(models.Model):
    _inherit = 'ir.attachment'

    list_doc = fields.Selection(selection=Doc_List)
    lead_id = fields.Many2one('crm.lead', string='')