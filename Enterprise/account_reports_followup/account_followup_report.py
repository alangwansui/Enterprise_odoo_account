# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from openerp import models, fields, api
from openerp.tools.translate import _
import time
import math


class account_report_context_followup_all(models.TransientModel):
    _inherit = "account.report.context.followup.all"

    action_contexts = []

    def _get_html_get_partners(self):
        self.partners_data = self.env['res.partner'].get_partners_in_need_of_action_and_update()
        return self.env['res.partner'].browse(self.partners_data.keys()) - self.skipped_partners_ids

    def _get_html_partner_done(self, given_context, partners):
        if given_context['partner_done'] == 'all' and 'action_context_list' in given_context:
            action_context_list = given_context['action_context_list']
            self.action_contexts = self.env['account.report.context.followup'].browse(action_context_list)
            action_partners = self.env['res.partner']
            for context in self.action_contexts:
                action_partners = action_partners | context.partner_id
            partners = partners - action_partners
            self.skip_partner(action_partners)
        return super(account_report_context_followup_all, self)._get_html_partner_done(given_context, partners)

    def _get_html_create_context(self, partner):
        vals = {'partner_id': partner.id}
        if partner.id in self.partners_data:
            vals.update({'level': self.partners_data[partner.id][0]})
        return self.env['account.report.context.followup'].with_context(lang=partner.lang).create(vals)

    def _get_html_build_rcontext(self, reports, emails_not_sent, given_context):
        res = super(account_report_context_followup_all, self)._get_html_build_rcontext(reports, emails_not_sent, given_context)
        res['action_contexts'] = self.action_contexts
        return res

    @api.depends('valuenow')  # Doesn't directly depend on valuenow but when valuenow is updated it means that this should change
    def _compute_pages(self):
        for context in self:
            partners = [x not in context.skipped_partners_ids.ids and x for x in self.env['res.partner'].get_partners_in_need_of_action_and_update().keys()]
            context.last_page = math.ceil(float(len(partners)) / float(self.PAGER_SIZE))


class account_report_context_followup(models.TransientModel):
    _inherit = "account.report.context.followup"

    level = fields.Many2one('account_followup.followup.line')
    summary = fields.Char(default=lambda s: s.level and s.level.description.replace('\n', '<br />') or s.env['res.company'].default_get(['overdue_msg'])['overdue_msg'])

    @api.multi
    def do_manual_action(self):
        for context in self:
            msg = _('Manual action done\n') + context.level.manual_action_note
            context.partner_id.message_post(body=msg, subtype='account_reports.followup_logged_action')

    @api.model
    def create(self, vals):
        if 'level' in vals:
            partner = self.env['res.partner'].browse(vals['partner_id'])
            summary = self.env['account_followup.followup.line'].with_context(lang=partner.lang).browse(vals['level']).description.replace('\n', '<br />')
            vals.update({
                'summary': summary % {
                    'partner_name': partner.name,
                    'date': time.strftime('%Y-%m-%d'),
                    'user_signature': self.env.user.signature or '',
                    'company_name': partner.parent_id.name,
                }
            })
        return super(account_report_context_followup, self).create(vals)
