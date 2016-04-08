# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from openerp import models, fields, api, _
from openerp.tools.misc import formatLang
from datetime import datetime, timedelta


class report_account_general_ledger(models.AbstractModel):
    _name = "account.general.ledger"
    _description = "General Ledger Report"

    def _format(self, value):
        if self.env.context.get('no_format'):
            return value
        currency_id = self.env.user.company_id.currency_id
        if currency_id.is_zero(value):
            # don't print -0.0 in reports
            value = abs(value)
        res = formatLang(self.env, value, currency_obj=currency_id)
        return res

    @api.model
    def get_lines(self, context_id, line_id=None):
        if type(context_id) == int:
            context_id = self.env['account.context.general.ledger'].search([['id', '=', context_id]])
        new_context = dict(self.env.context)
        new_context.update({
            'date_from': context_id.date_from,
            'date_to': context_id.date_to,
            'state': context_id.all_entries and 'all' or 'posted',
            'cash_basis': context_id.cash_basis,
            'context_id': context_id,
            'company_ids': context_id.company_ids.ids,
        })
        return self.with_context(new_context)._lines(line_id)

    def do_query(self, line_id):
        select = ',COALESCE(SUM(\"account_move_line\".debit-\"account_move_line\".credit), 0),SUM(\"account_move_line\".amount_currency),SUM(\"account_move_line\".debit),SUM(\"account_move_line\".credit)'
        if self.env.context.get('cash_basis'):
            select = select.replace('debit', 'debit_cash_basis').replace('credit', 'credit_cash_basis')
        sql = "SELECT \"account_move_line\".account_id%s FROM %s WHERE %s%s GROUP BY \"account_move_line\".account_id"
        tables, where_clause, where_params = self.env['account.move.line']._query_get()
        line_clause = line_id and ' AND \"account_move_line\".account_id = ' + str(line_id) or ''
        query = sql % (select, tables, where_clause, line_clause)
        self.env.cr.execute(query, where_params)
        results = self.env.cr.fetchall()
        results = dict([(k[0], {'balance': k[1], 'amount_currency': k[2], 'debit': k[3], 'credit': k[4]}) for k in results])
        return results

    def group_by_account_id(self, line_id):
        accounts = {}
        results = self.do_query(line_id)
        initial_bal_date_to = datetime.strptime(self.env.context['date_from_aml'], "%Y-%m-%d") + timedelta(days=-1)
        initial_bal_results = self.with_context(date_to=initial_bal_date_to.strftime('%Y-%m-%d')).do_query(line_id)
        context = self.env.context
        base_domain = [('date', '<=', context['date_to']), ('company_id', 'in', context['company_ids'])]
        if context['date_from_aml']:
            base_domain.append(('date', '>=', context['date_from_aml']))
        if context['state'] == 'posted':
            base_domain.append(('move_id.state', '=', 'posted'))
        for account_id, result in results.items():
            domain = list(base_domain)  # copying the base domain
            domain.append(('account_id', '=', account_id))
            account = self.env['account.account'].browse(account_id)
            accounts[account] = result
            accounts[account]['initial_bal'] = initial_bal_results.get(account.id, {'balance': 0, 'amount_currency': 0, 'debit': 0, 'credit': 0})
            if not context.get('print_mode'):
                #  fetch the 81 first amls. The report only displays the first 80 amls. We will use the 81st to know if there are more than 80 in which case a link to the list view must be displayed.
                accounts[account]['lines'] = self.env['account.move.line'].search(domain, order='date', limit=81)
            else:
                accounts[account]['lines'] = self.env['account.move.line'].search(domain, order='date')
        return accounts

    @api.model
    def _lines(self, line_id=None):
        lines = []
        context = self.env.context
        company_id = context.get('company_id') or self.env.user.company_id
        grouped_accounts = self.with_context(date_from_aml=context['date_from'], date_from=context['date_from'] and company_id.compute_fiscalyear_dates(datetime.strptime(context['date_from'], "%Y-%m-%d"))['date_from'] or None).group_by_account_id(line_id)  # Aml go back to the beginning of the user chosen range but the amount on the account line should go back to either the beginning of the fy or the beginning of times depending on the account
        sorted_accounts = sorted(grouped_accounts, key=lambda a: a.code)
        unfold_all = context.get('print_mode') and not context['context_id']['unfolded_accounts']
        for account in sorted_accounts:
            debit = grouped_accounts[account]['debit']
            credit = grouped_accounts[account]['credit']
            balance = grouped_accounts[account]['balance']
            amount_currency = '' if not account.currency_id else grouped_accounts[account]['amount_currency']
            lines.append({
                'id': account.id,
                'type': 'line',
                'name': account.code + " " + account.name,
                'footnotes': self.env.context['context_id']._get_footnotes('line', account.id),
                'columns': ['', '', '', amount_currency, self._format(debit), self._format(credit), self._format(balance)],
                'level': 2,
                'unfoldable': True,
                'unfolded': account in context['context_id']['unfolded_accounts'] or unfold_all,
                'colspan': 4,
            })
            if account in context['context_id']['unfolded_accounts'] or unfold_all:
                progress = 0
                domain_lines = []
                amls = grouped_accounts[account]['lines']
                too_many = False
                if len(amls) > 80 and not context.get('print_mode'):
                    amls = amls[-80:]
                    too_many = True
                for line in amls:
                    if self.env.context['cash_basis']:
                        line_debit = line.debit_cash_basis
                        line_credit = line.credit_cash_basis
                    else:
                        line_debit = line.debit
                        line_credit = line.credit
                    progress = progress + line_debit - line_credit
                    currency = "" if not line.account_id.currency_id else line.amount_currency
                    name = []
                    name = line.name and line.name or ''
                    if line.ref:
                        name = name and name + ' - ' + line.ref or line.ref
                    if len(name) > 35:
                        name = name[:32] + "..."
                    partner_name = line.partner_id.name
                    if partner_name and len(partner_name) > 35:
                        partner_name = partner_name[:32] + "..."
                    domain_lines.append({
                        'id': line.id,
                        'type': 'move_line_id',
                        'move_id': line.move_id.id,
                        'action': line.get_model_id_and_name(),
                        'name': line.move_id.name if line.move_id.name else '/',
                        'footnotes': self.env.context['context_id']._get_footnotes('move_line_id', line.id),
                        'columns': [line.date, name, partner_name, currency,
                                    line_debit != 0 and self._format(line_debit) or '',
                                    line_credit != 0 and self._format(line_credit) or '',
                                    self._format(progress)],
                        'level': 1,
                    })
                initial_debit = grouped_accounts[account]['initial_bal']['debit']
                initial_credit = grouped_accounts[account]['initial_bal']['credit']
                initial_balance = grouped_accounts[account]['initial_bal']['balance']
                initial_currency = '' if not account.currency_id else grouped_accounts[account]['initial_bal']['amount_currency']
                domain_lines[:0] = [{
                    'id': account.id,
                    'type': 'initial_balance',
                    'name': _('Initial Balance'),
                    'footnotes': self.env.context['context_id']._get_footnotes('initial_balance', account.id),
                    'columns': ['', '', '', initial_currency, self._format(initial_debit), self._format(initial_credit), self._format(initial_balance)],
                    'level': 1,
                }]
                domain_lines.append({
                    'id': account.id,
                    'type': 'o_account_reports_domain_total',
                    'name': _('Total ') + account.name,
                    'footnotes': self.env.context['context_id']._get_footnotes('o_account_reports_domain_total', account.id),
                    'columns': ['', '', '', amount_currency, self._format(debit), self._format(credit), self._format(balance)],
                    'level': 1,
                })
                if too_many:
                    domain_lines.append({
                        'id': account.id,
                        'type': 'too_many',
                        'name': _('There are more than 80 items in this list, click here to see all of them'),
                        'footnotes': [],
                        'colspan': 8,
                        'columns': [],
                        'level': 3,
                    })
                lines += domain_lines
        return lines

    @api.model
    def get_title(self):
        return _("General Ledger")

    @api.model
    def get_name(self):
        return 'general_ledger'

    @api.model
    def get_report_type(self):
        return 'no_comparison'

    def get_template(self):
        return 'account_reports.report_financial'


class account_context_general_ledger(models.TransientModel):
    _name = "account.context.general.ledger"
    _description = "A particular context for the general ledger"
    _inherit = "account.report.context.common"

    fold_field = 'unfolded_accounts'
    unfolded_accounts = fields.Many2many('account.account', 'context_to_account', string='Unfolded lines')

    def get_report_obj(self):
        return self.env['account.general.ledger']

    def get_columns_names(self):
        return [_("Date"), _("Communication"), _("Partner"), _("Currency"), _("Debit"), _("Credit"), _("Balance")]

    @api.multi
    def get_columns_types(self):
        return ["date", "text", "text", "number", "number", "number", "number"]
