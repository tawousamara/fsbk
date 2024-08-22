from odoo import models, fields, api, _


class CrmTeam(models.Model):
    _inherit = 'crm.team'

    geographic_area = fields.Selection([('center', 'Centre'),
                                        ('east', 'Est'),
                                        ('west', 'Ouest')], string="Zone géographique")

    total_engagement_amount = fields.Monetary(
        string='Opportunities Total Engagement', compute='_compute_total_engagement_amount')


    def _compute_total_engagement_amount(self):
        opportunity_data = self.env['crm.lead']._read_group([
            ('team_id', 'in', self.ids),
            ('probability', '<', 100),
            ('type', '=', 'opportunity'),
        ], ['team_id'], ['total_engagement:sum'])
        counts_amounts = {team.id: total_engagement_sum for team, total_engagement_sum in opportunity_data}
        for team in self:
            team.total_engagement_amount = counts_amounts.get(team.id, 0.0)
