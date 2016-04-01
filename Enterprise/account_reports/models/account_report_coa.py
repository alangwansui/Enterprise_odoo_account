# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from openerp import models, fields, api, _
from datetime import datetime


class report_account_coa(models.AbstractModel):
    _name = "account.coa.report"
    _description = "Chart of Account Report"
    _inherit = "account.general.ledger"

    @api.model
    def get_lines(self, context_id, line_id=None):
        if type(context_id) == int:
            context_id = self.env['account.context.coa'].search([['id', '=', context_id]])
        new_context = dict(self.env.context)
        new_context.update({
            'date_from': context_id.date_from,
            'date_to': context_id.date_to,
            'state': context_id.all_entries and 'all' or 'posted',
            'cash_basis': context_id.cash_basis,
            'context_id': context_id,
            'company_ids': context_id.company_ids.ids,
            'periods_number': context_id.periods_number,
            'periods': [[context_id.date_from, context_id.date_to]] + context_id.get_cmp_periods(),
        })
        return self.with_context(new_context)._lines(line_id)

    @api.model
    def _lines(self, line_id=None):
        lines = []
        context = self.env.context
        company_id = context.get('company_id') or self.env.user.company_id
        grouped_accounts = {}
        period_number = 0
        for period in context['periods']:
            res = self.with_context(date_from_aml=period[0], date_to=period[1], date_from=period[0] and company_id.compute_fiscalyear_dates(datetime.strptime(period[0], "%Y-%m-%d"))['date_from'] or None).group_by_account_id(line_id)  # Aml go back to the beginning of the user chosen range but the amount on the account line should go back to either the beginning of the fy or the beginning of times depending on the account
            for account in res:
                if account not in grouped_accounts.keys():
                    grouped_accounts[account] = [{'balance': 0, 'debit': 0, 'credit': 0} for p in context['periods']]
                grouped_accounts[account][period_number] = res[account]
            period_number += 1
        sorted_accounts = sorted(grouped_accounts, key=lambda a: a.code)
        title_index = '0'
        for account in sorted_accounts:
            non_zero = False
            for p in xrange(len(context['periods'])):
                if not company_id.currency_id.is_zero(grouped_accounts[account][p]['balance']):
                    non_zero = True
            if not non_zero:
                continue
            if account.code[0] > title_index:
                title_index = account.code[0]
                lines.append({
                    'id': title_index,
                    'type': 'line',
                    'name': _("Class %s" % (title_index)),
                    'footnotes': [],
                    'columns': sum([['', ''] for p in xrange(len(context['periods']))], []),
                    'level': 1,
                    'unfoldable': False,
                    'unfolded': True,
                })
            lines.append({
                'id': account.id,
                'type': 'account_id',
                'name': account.code + " " + account.name,
                'footnotes': self.env.context['context_id']._get_footnotes('account_id', account.id),
                'columns': sum([[grouped_accounts[account][p]['balance'] > 0 and self._format(grouped_accounts[account][p]['debit'] - grouped_accounts[account][p]['credit']) or '',
                                 grouped_accounts[account][p]['balance'] < 0 and self._format(grouped_accounts[account][p]['credit'] - grouped_accounts[account][p]['debit']) or '']
                                for p in xrange(len(context['periods']))], []),
                'level': 1,
                'unfoldable': False,
            })
        return lines

    @api.model
    def get_title(self):
        return _("Chart of Account")

    @api.model
    def get_name(self):
        return 'coa'

    @api.model
    def get_report_type(self):
        return 'date_range'


class account_context_coa(models.TransientModel):
    _name = "account.context.coa"
    _description = "A particular context for the chart of account"
    _inherit = "account.report.context.common"

    fold_field = 'unfolded_accounts'
    unfolded_accounts = fields.Many2many('account.account', 'context_to_account_coa', string='Unfolded lines')

    def get_report_obj(self):
        return self.env['account.coa.report']

    def get_columns_names(self):
        temp = self.get_full_date_names(self.date_to)
        columns = [_('Debit') + '<br/>' + temp.decode("utf-8"), _('Credit')]
        if self.comparison and (self.periods_number == 1 or self.date_filter_cmp == 'custom'):
            columns += [_('Debit') + '<br/>' + self.get_cmp_date(), _('Credit')]
        else:
            for period in self.get_cmp_periods(display=True):
                columns += [_('Debit') + '<br/>' + str(period), _('Credit')]
        return columns

    @api.multi
    def get_columns_types(self):
        types = ['number', 'number']
        if self.comparison and (self.periods_number == 1 or self.date_filter_cmp == 'custom'):
            types += ['number', 'number']
        else:
            for period in self.get_cmp_periods(display=True):
                types += ['number', 'number']
        return types
