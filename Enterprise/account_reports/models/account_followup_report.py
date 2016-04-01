# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from openerp import models, fields, api, tools
from datetime import datetime
from hashlib import md5
from openerp.tools.misc import formatLang
from openerp.tools.translate import _
import time
from openerp.tools.safe_eval import safe_eval
from openerp.tools import append_content_to_html
import math


class report_account_followup_report(models.AbstractModel):
    _name = "account.followup.report"
    _description = "Followup Report"

    @api.model
    def get_lines(self, context_id, line_id=None, public=False):
        lines = []
        res = {}
        today = datetime.today().strftime('%Y-%m-%d')
        line_num = 0
        for l in context_id.partner_id.unreconciled_aml_ids:
            if public and l.blocked:
                continue
            currency = l.currency_id or l.company_id.currency_id
            if currency not in res:
                res[currency] = []
            res[currency].append(l)
        for currency, aml_recs in res.items():
            total = 0
            total_issued = 0
            aml_recs = sorted(aml_recs, key=lambda aml: aml.blocked)
            for aml in aml_recs:
                amount = aml.currency_id and aml.amount_residual_currency or aml.amount_residual
                date_due = aml.date_maturity or aml.date
                total += not aml.blocked and amount or 0
                is_overdue = today > aml.date_maturity if aml.date_maturity else today > aml.date
                is_payment = aml.payment_id
                if is_overdue or is_payment:
                    total_issued += not aml.blocked and amount or 0
                if is_overdue:
                    date_due = (date_due, 'color: red;')
                if is_payment:
                    date_due = ''
                amount = formatLang(self.env, amount, currency_obj=currency)
                line_num += 1
                lines.append({
                    'id': aml.id,
                    'name': aml.move_id.name,
                    'action': aml.get_model_id_and_name(),
                    'move_id': aml.move_id.id,
                    'type': is_payment and 'payment' or 'unreconciled_aml',
                    'footnotes': {},
                    'unfoldable': False,
                    'columns': [aml.date, date_due, aml.invoice_id.reference] + (not public and [aml.expected_pay_date and (aml.expected_pay_date, aml.internal_note) or ('', ''), aml.blocked] or []) + [amount],
                    'blocked': aml.blocked,
                })
            total = formatLang(self.env, total, currency_obj=currency)
            line_num += 1
            lines.append({
                'id': line_num,
                'name': '',
                'type': 'total',
                'footnotes': {},
                'unfoldable': False,
                'level': 0,
                'columns': (not public and ['', ''] or []) + ['', '', total >= 0 and _('Total Due') or ''] + [total],
            })
            if total_issued > 0:
                total_issued = formatLang(self.env, total_issued, currency_obj=currency)
                line_num += 1
                lines.append({
                    'id': line_num,
                    'name': '',
                    'type': 'total',
                    'footnotes': {},
                    'unfoldable': False,
                    'level': 0,
                    'columns': (not public and ['', ''] or []) + ['', '', _('Total Overdue')] + [total_issued],
                })
        return lines

    @api.model
    def get_title(self):
        return _('Followup Report')

    @api.model
    def get_name(self):
        return 'followup_report'

    @api.model
    def get_report_type(self):
        return 'custom'

    @api.model
    def get_template(self):
        return 'account_reports.report_followup'


class account_report_context_followup_all(models.TransientModel):
    _name = "account.report.context.followup.all"
    _description = "A progress bar for followup reports"

    PAGER_SIZE = 15

    @api.depends('valuenow', 'valuemax')
    def _compute_percentage(self):
        for progressbar in self:
            if progressbar.valuemax > 0:
                progressbar.percentage = 100 * progressbar.valuenow / progressbar.valuemax

    @api.depends('valuenow')  # Doesn't directly depend on valuenow but when valuenow is updated it means that this should change
    def _compute_pages(self):
        for context in self:
            partners = self.env['res.partner'].get_partners_in_need_of_action() - context.skipped_partners_ids
            context.last_page = math.ceil(float(len(partners)) / float(self.PAGER_SIZE))

    valuenow = fields.Integer('current amount of invoices done', default=0)
    valuemax = fields.Integer('total amount of invoices to do')
    percentage = fields.Integer(compute='_compute_percentage')
    started = fields.Datetime('Starting time', default=lambda self: fields.datetime.now())
    partner_filter = fields.Selection([('all', 'All partners with overdue invoices'), ('action', 'All partners in need of action')], string='Partner Filter', default='action')
    skipped_partners_ids = fields.Many2many('res.partner', 'account_fup_report_skipped_partners', string='Skipped partners')
    last_page = fields.Integer('number of pages', compute='_compute_pages')

    def skip_partner(self, partners):
        self.write({'skipped_partners_ids': [(6, 0, partners.ids + self.skipped_partners_ids.ids)]})
        self.write({'valuenow': self.valuenow + len(partners)})

    def get_total_time(self):
        delta = fields.datetime.now() - datetime.strptime(self.started, tools.DEFAULT_SERVER_DATETIME_FORMAT)
        return delta.seconds

    def get_time_per_report(self):
        return round(self.get_total_time() / self.valuemax, 2)

    def get_alerts(self):
        alerts = []
        if self.valuemax > 4 and self.valuemax / 2 == self.valuenow:
            alerts.append({
                'title': _('Halfway through!'),
                'message': _('The first half took you %ss.') % str(self.get_total_time()),
            })
        if self.valuemax > 50 and round(self.valuemax * 0.9) == self.valuenow:
            alerts.append({
                'title': _('10% remaining!'),
                'message': _("Hang in there, you're nearly done."),
            })
        return alerts

    def _get_html_get_partners(self):
        return self.env['res.partner'].get_partners_in_need_of_action() - self.skipped_partners_ids

    def _get_html_partner_done(self, given_context, partners):
        partners = partners.sorted(key=lambda x: x.name)
        context_obj = self.env['account.report.context.followup']
        emails_not_sent = context_obj.browse()
        processed_partners = False
        if given_context['partner_done'] == 'all':
            if 'email_context_list' in given_context:
                email_context_list = given_context['email_context_list']
                email_contexts = context_obj.browse(email_context_list)
                for email_context in email_contexts:
                    if not email_context.send_email():
                        emails_not_sent = emails_not_sent | email_context
            partners_done = partners[((given_context['page'] - 1) * self.PAGER_SIZE):(given_context['page'] * self.PAGER_SIZE)] - emails_not_sent.partner_id
            processed_partners = partners_done.update_next_action(batch=True)
            self.write({'valuenow': min(self.valuemax, self.valuenow + len(partners_done))})
            partners = partners - partners_done
        else:
            self.write({'valuenow': self.valuenow + 1})
        return [partners, emails_not_sent, processed_partners]

    def _get_html_create_context(self, partner):
        return self.env['account.report.context.followup'].with_context(lang=partner.lang).create({'partner_id': partner.id})

    def _get_html_build_rcontext(self, reports, emails_not_sent, given_context):
        all_partners_done = given_context.get('partner_done') and (self.valuenow == self.valuemax or given_context['partner_done'] == 'all')
        return {
            'reports': not all_partners_done and reports or [],
            'report': self.env['account.followup.report'],
            'mode': 'display',
            'emails_not_sent': emails_not_sent,
            'context_all': self,
            'all_partners_done': all_partners_done,
            'just_arrived': 'partner_done' not in given_context and 'partner_skipped' not in given_context,
            'time': time,
            'today': datetime.today().strftime('%Y-%m-%d'),
            'res_company': self.env.user.company_id,
            'page': given_context.get('page')
        }

    @api.multi
    def get_html(self, given_context=None):
        if given_context is None:
            given_context = {}
        context_obj = self.env['account.report.context.followup']
        report_obj = self.env['account.followup.report']
        reports = []
        emails_not_sent = context_obj.browse()
        processed_partners = False  # The partners that have been processed and for who the context should be deleted
        if 'partner_skipped' in given_context:
            self.skip_partner(self.env['res.partner'].browse(int(given_context['partner_skipped'])))
        partners = self._get_html_get_partners()
        if 'partner_filter' in given_context:
            self.write({'partner_filter': given_context['partner_filter']})
        if 'partner_done' in given_context and 'partner_filter' not in given_context:
            try:
                self.write({'skipped_partners_ids': [(4, int(given_context['partner_done']))]})
            except ValueError:
                pass
            [partners, emails_not_sent, processed_partners] = self._get_html_partner_done(given_context, partners)
        if self.valuemax != self.valuenow + len(partners):
            self.write({'valuemax': self.valuenow + len(partners)})
        if self.partner_filter == 'all':
            partners = self.env['res.partner'].get_partners_in_need_of_action(overdue_only=True)
        partners = partners.sorted(key=lambda x: x.name)
        for partner in partners[((given_context['page'] - 1) * self.PAGER_SIZE):(given_context['page'] * self.PAGER_SIZE)]:
            context_id = context_obj.search([('partner_id', '=', partner.id)], limit=1)
            if not context_id:
                context_id = self._get_html_create_context(partner)
            lines = report_obj.with_context(lang=partner.lang).get_lines(context_id)
            reports.append({
                'context': context_id.with_context(lang=partner.lang),
                'lines': lines,
            })
        rcontext = self._get_html_build_rcontext(reports, emails_not_sent, given_context)
        res = self.env['ir.model.data'].xmlid_to_object('account_reports.report_followup_all').render(rcontext)
        if processed_partners:
            self.env['account.report.context.followup'].search([('partner_id', 'in', processed_partners.ids)]).unlink()
        return res


class account_report_context_followup(models.TransientModel):
    _name = "account.report.context.followup"
    _description = "A particular context for the followup report"
    _inherit = "account.report.context.common"

    @api.depends('partner_id')
    @api.one
    def _get_invoice_address(self):
        if self.partner_id:
            self.invoice_address_id = self.partner_id.address_get(['invoice'])['invoice']
        else:
            self.invoice_address_id = False

    footnotes = fields.Many2many('account.report.footnote', 'account_context_footnote_followup', string='Footnotes')
    partner_id = fields.Many2one('res.partner', string='Partner')
    invoice_address_id = fields.Many2one('res.partner', compute='_get_invoice_address', string='Invoice Address')
    summary = fields.Char(default=lambda s: s.env.user.company_id.overdue_msg and s.env.user.company_id.overdue_msg.replace('\n', '<br />') or s.env['res.company'].default_get(['overdue_msg'])['overdue_msg'])

    @api.multi
    def change_next_action(self, date, note):
        self.partner_id.write({'payment_next_action': note, 'payment_next_action_date': date})
        if self.partner_id.payment_next_action_date != fields.Date.context_today(self):
            msg = _('Next action date: ') + self.partner_id.payment_next_action_date + '.\n' + note
        else:
            msg = note
        self.partner_id.message_post(body=msg, subtype='account_reports.followup_logged_action')

    @api.multi
    def add_footnote(self, type, target_id, column, number, text):
        footnote = self.env['account.report.footnote'].create(
            {'type': type, 'target_id': target_id, 'column': column, 'number': number, 'text': text}
        )
        self.write({'footnotes': [(4, footnote.id)]})

    @api.model
    def get_partners(self):
        return self.env['res.partner'].search([])

    @api.multi
    def edit_footnote(self, number, text):
        footnote = self.footnotes.filtered(lambda s: s.number == number)
        footnote.write({'text': text})

    @api.multi
    def remove_footnote(self, number):
        footnotes = self.footnotes.filtered(lambda s: s.number == number)
        self.write({'footnotes': [(3, footnotes.id)]})

    def get_report_obj(self):
        return self.env['account.followup.report']

    def get_columns_names(self):
        if self.env.context.get('public'):
            return [_(' Date '), _(' Due Date '), _('Communication'), _(' Total Due ')]
        return [_(' Date '), _(' Due Date '), _('Communication'), _(' Expected Date '), _(' Excluded '), _(' Total Due ')]

    @api.multi
    def get_columns_types(self):
        if self.env.context.get('public'):
            return ['date', 'date', 'text', 'number']
        return ['date', 'date', 'text', 'date', 'checkbox', 'number']

    def get_pdf(self, log=False):
        bodies = []
        headers = []
        footers = []
        for context in self:
            context = context.with_context(lang=context.partner_id.lang)
            report_obj = context.get_report_obj()
            lines = report_obj.get_lines(context, public=True)
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            rcontext = {
                'context': context,
                'report': report_obj,
                'lines': lines,
                'mode': 'print',
                'base_url': base_url,
                'css': '',
                'o': self.env.user,
                'today': datetime.today().strftime('%Y-%m-%d'),
                'company': self.env.user.company_id,
                'res_company': self.env.user.company_id,
            }
            html = self.pool['ir.ui.view'].render(self._cr, self._uid, report_obj.get_template() + '_letter', rcontext, context=context.env.context)
            bodies.append((0, html))
            header = self.pool['ir.ui.view'].render(self._cr, self._uid, "report.external_layout_header", rcontext, context=self.env.context)
            rcontext['body'] = header
            header = self.pool['ir.ui.view'].render(self._cr, self._uid, "report.minimal_layout", rcontext, context=self.env.context)
            footer = self.pool['ir.ui.view'].render(self._cr, self._uid, "report.external_layout_footer", rcontext, context=self.env.context)
            rcontext['body'] = footer
            rcontext['subst'] = True
            footer = self.pool['ir.ui.view'].render(self._cr, self._uid, "report.minimal_layout", rcontext, context=self.env.context)
            headers.append(header)
            footers.append(footer)
            if log:
                msg = _('Sent a followup letter')
                context.partner_id.message_post(body=msg, subtype='account_reports.followup_logged_action')

        return self.env['report']._run_wkhtmltopdf(headers, footers, bodies, False, self.env.user.company_id.paperformat_id)

    @api.multi
    def send_email(self):
        email = self.env['res.partner'].browse(self.partner_id.address_get(['invoice'])['invoice']).email
        if email and email.strip():
            email = self.env['mail.mail'].create({
                'subject': _('%s Payment Reminder') % self.env.user.company_id.name,
                'body_html': append_content_to_html(self.with_context(public=True, mode='print').get_html(), self.env.user.signature, plaintext=False),
                'email_from': self.env.user.email or '',
                'email_to': email,
            })
            msg = _(': Sent a followup email')
            self.partner_id.message_post(body=msg, subtype='account_reports.followup_logged_action')
            return True
        return False

    def get_history(self):
        return self.env['mail.message'].search([('subtype_id', '=', self.env.ref('account_reports.followup_logged_action').id), ('id', 'in', self.partner_id.message_ids.ids)], limit=5)

    @api.multi
    def to_auto(self):
        self.partner_id.write({'payment_next_action_date': datetime.today().strftime('%Y-%m-%d')})
        self.unlink()

    @api.multi
    def get_html(self, given_context=None):
        if given_context is None:
            given_context = {}
        lines = self.env['account.followup.report'].with_context(lang=self.partner_id.lang).get_lines(self, public=self.env.context.get('public', False))
        rcontext = {
            'context': self.with_context(lang=self.partner_id.lang),
            'report': self.env['account.followup.report'].with_context(lang=self.partner_id.lang),
            'lines': lines,
            'mode': self.env.context.get('mode', 'display'),
            'time': time,
            'today': datetime.today().strftime('%Y-%m-%d'),
            'res_company': self.env['res.users'].browse(self.env.uid).company_id,
        }
        return self.env['ir.model.data'].xmlid_to_object('account_reports.report_followup').render(rcontext)
