from odoo import models, fields, api, _


class Partner(models.Model):
    _inherit = 'res.partner'

    nrc = fields.Char(string='N.RC')
    nif = fields.Char(string='NIF')
    nis = fields.Char(string='NIS')
    date_creation = fields.Date(string='Date de création')
    branch = fields.Many2one('fsbk.branch', string='Agence')
    secteur = fields.Many2one('fsbk.secteur', string='Secteur d\'activité')
    activity = fields.Many2one('fsbk.activity', string='Activité en détails')
    rib = fields.Char(string='RIB')
    geographic_area = fields.Selection([('center', 'Centre'),
                                        ('east', 'Est'),
                                        ('west', 'Ouest')], string="Zone géographique", required=True)


class User(models.Model):
    _inherit = 'res.users'

    forme_jur = fields.Many2one('fsbk.forme.juridique', string='Forme Juridique')
