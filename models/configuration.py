from odoo import models, fields, api, _



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
    is_printed = fields.Boolean(string='Afficher dans le rapport', default=True)