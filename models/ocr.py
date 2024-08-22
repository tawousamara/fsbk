
from odoo import models, fields, api, _

class TCR(models.Model):
    _inherit = 'import.ocr.tcr'

    lead_parent_id = fields.Many2one('crm.lead', string='Opportunity')

    @api.model
    def create(self, vals):
        vals['lead_parent_id'] = self.env.context.get('lead_parent_id', False)
        res = super(TCR, self).create(vals)
        year = self.env.context.get('year')
        group = self.env.context.get('is_group', False)
        if res.lead_parent_id:
            if year != 2 and not group:
                res.lead_parent_id.tcr_id = res.id
            elif year == 2 and not group:
                res.lead_parent_id.tcr1_id = res.id

        return res


class Actif(models.Model):
    _inherit = 'import.ocr.actif'

    lead_parent_id = fields.Many2one('crm.lead', string='Opportunity')

    @api.model
    def create(self, vals):
        vals['lead_parent_id'] = self.env.context.get('lead_parent_id', False)
        year = self.env.context.get('year')
        group = self.env.context.get('is_group', False)
        res = super(Actif, self).create(vals)
        if res.lead_parent_id:
            if year != 2 and not group:
                res.lead_parent_id.actif_id = res.id
            elif year == 2 and not group:
                res.lead_parent_id.actif1_id = res.id

        return res


class Passif(models.Model):
    _inherit = 'import.ocr.passif'

    lead_parent_id = fields.Many2one('crm.lead', string='Opportunity')

    @api.model
    def create(self, vals):
        vals['lead_parent_id'] = self.env.context.get('lead_parent_id', False)
        year = self.env.context.get('year')
        group = self.env.context.get('is_group', False)
        res = super(Passif, self).create(vals)
        if res.lead_parent_id:
            if year != 2 and not group:
                res.lead_parent_id.passif_id = res.id
            elif year == 2 and not group:
                res.lead_parent_id.passif1_id = res.id

        return res


class BilanFisc(models.Model):
    _inherit = 'fsbk.bilan'

    lead_id = fields.Many2one('crm.lead')

class BilanCateg1(models.Model):
    _inherit = 'fsbk.bilan.cat1'

    lead_id = fields.Many2one('crm.lead')

class BilanCateg2(models.Model):
    _inherit = 'fsbk.bilan.cat2'

    lead_id = fields.Many2one('crm.lead')

class BilanCateg3(models.Model):
    _inherit = 'fsbk.bilan.cat3'

    lead_id = fields.Many2one('crm.lead')

class BilanCateg4(models.Model):
    _inherit = 'fsbk.bilan.cat4'

    lead_id = fields.Many2one('crm.lead')

class BilanCateg5(models.Model):
    _inherit = 'fsbk.bilan.cat5'

    lead_id = fields.Many2one('crm.lead')

