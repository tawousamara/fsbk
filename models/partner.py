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
    representant = fields.Char(string='Representant')
    forme_jur = fields.Many2one('crm.forme.juridique', string='Forme Juridique')

    '''def update_company(self, partner_name='', street='', state_id=False, forme_jur=False, representant='', secteur=False, activity=False ):
        for rec in self:
            vals = {'street': street,
                    'state_id': state_id,
                    'forme_jur': forme_jur,
                    'representant': representant,
                    'secteur': secteur,
                    'activity': activity}
            if rec.parent_id:
                rec.parent_id.write(vals)
            else:
                vals['name'] = partner_name
                rec.parent_id = self.env['res.partner'].create(vals)
       '''

    def update_company(self, post):
        for rec in self:
            print(post)
            company_name = post['company_name']
            post.pop('company_name')
            if rec.parent_id:
                rec.parent_id.write(post)
            else:
                post['name'] = company_name
                rec.parent_id = self.env['res.partner'].create(post)

class User(models.Model):
    _inherit = 'res.users'

    forme_jur = fields.Many2one('crm.forme.juridique', string='Forme Juridique')
