from odoo import models, fields, api, _


class Partner(models.Model):
    _inherit = 'res.partner'

    nrc = fields.Char(string='N.RC')
    nif = fields.Char(string='NIF')
    nis = fields.Char(string='NIS')
    date_creation = fields.Date(string='Date de création')
    branch = fields.Many2one('crm.branch', string='Agence')
    secteur = fields.Many2one('crm.secteur', string='Secteur d\'activité')
    activity = fields.Many2one('crm.activity', string='Activité en détails')
    rib = fields.Char(string='RIB')


class User(models.Model):
    _inherit = 'res.users'

    forme_jur = fields.Many2one('crm.forme.juridique', string='Forme Juridique')
