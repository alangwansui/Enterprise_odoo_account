# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from openerp import models, api
from openerp.tools.translate import _
from openerp.tools.misc import formatLang


class report_account_generic_tax_report(models.AbstractModel):
    _name = "account.generic.tax.report"
    _description = "Generic Tax Report"

    def _format(self, value):
        if self.env.context.get('no_format'):
            return value
        currency_id = self.env.user.company_id.currency_id
        if currency_id.is_zero(value):
            # don't print -0.0 in reports
            value = abs(value)
        return formatLang(self.env, value, currency_obj=currency_id)

    @api.model
    def get_lines(self, context_id, line_id=None):
        return self.with_context(
            date_from=context_id.date_from,
            date_to=context_id.date_to,
            state=context_id.all_entries and 'all' or 'posted',
            comparison=context_id.comparison,
            date_from_cmp=context_id.date_from_cmp,
            date_to_cmp=context_id.date_to_cmp,
            cash_basis=context_id.cash_basis,
            periods_number=context_id.periods_number,
            periods=context_id.get_cmp_periods(),
            context_id=context_id,
            company_ids=context_id.company_ids.ids,
            strict_range=True,
        )._lines()

    def _compute_from_amls(self, taxes, period_number):
        sql = """SELECT "account_move_line".tax_line_id, COALESCE(SUM("account_move_line".debit-"account_move_line".credit), 0)
                    FROM %s
                    WHERE %s GROUP BY "account_move_line".tax_line_id"""
        tables, where_clause, where_params = self.env['account.move.line']._query_get()
        query = sql % (tables, where_clause)
        self.env.cr.execute(query, where_params)
        results = self.env.cr.fetchall()
        for result in results:
            if result[0] in taxes:
                taxes[result[0]]['periods'][period_number]['tax'] = result[1]
                taxes[result[0]]['show'] = True
        sql = """SELECT r.account_tax_id, COALESCE(SUM("account_move_line".debit-"account_move_line".credit), 0)
                 FROM %s
                 INNER JOIN account_move_line_account_tax_rel r ON ("account_move_line".id = r.account_move_line_id)
                 INNER JOIN account_tax t ON (r.account_tax_id = t.id)
                 WHERE %s GROUP BY r.account_tax_id"""
        if self.env.context.get('cash_basis'):
            sql = sql.replace('debit', 'debit_cash_basis').replace('credit', 'credit_cash_basis')
        query = sql % (tables, where_clause)
        self.env.cr.execute(query, where_params)
        results = self.env.cr.fetchall()
        for result in results:
            if result[0] in taxes:
                taxes[result[0]]['periods'][period_number]['net'] = result[1]
                taxes[result[0]]['show'] = True

    @api.model
    def _lines(self):
        taxes = {}
        context = self.env.context
        for tax in self.env['account.tax'].search([]):
            taxes[tax.id] = {'obj': tax, 'show': False, 'periods': [{'net': 0, 'tax': 0}]}
            for period in context['periods']:
                taxes[tax.id]['periods'].append({'net': 0, 'tax': 0})
        period_number = 0
        self._compute_from_amls(taxes, period_number)
        for period in context['periods']:
            period_number += 1
            self.with_context(date_from=period[0], date_to=period[1])._compute_from_amls(taxes, period_number)
        lines = []
        types = ['sale', 'purchase']
        groups = dict((tp, {}) for tp in types)
        for key, tax in taxes.items():
            if tax['obj'].type_tax_use == 'none':
                continue
            if tax['obj'].children_tax_ids:
                tax['children'] = []
                for child in tax['obj'].children_tax_ids:
                    if child.type_tax_use != 'none':
                        continue
                    tax['children'].append(taxes[child.id])
            if tax['obj'].children_tax_ids and not tax.get('children'):
                continue
            groups[tax['obj'].type_tax_use][key] = tax
        line_id = 0
        for tp in types:
            sign = tp == 'sale' and -1 or 1
            lines.append({
                    'id': line_id,
                    'name': tp == 'sale' and _('Sale') or _('Purchase'),
                    'type': 'line',
                    'footnotes': self.env.context['context_id']._get_footnotes('line', tp),
                    'unfoldable': False,
                    'columns': ['' for k in range(0, (len(context['periods']) + 1) * 2)],
                    'level': 1,
                })
            for key, tax in sorted(groups[tp].items(), key=lambda k: k[1]['obj'].sequence):
                if tax['show']:
                    lines.append({
                        'id': tax['obj'].id,
                        'name': tax['obj'].name + ' (' + str(tax['obj'].amount) + ')',
                        'type': 'tax_id',
                        'footnotes': self.env.context['context_id']._get_footnotes('tax_id', tax['obj'].id),
                        'unfoldable': False,
                        'columns': sum([[self._format(period['net'] * sign), self._format(period['tax'] * sign)] for period in tax['periods']], []),
                        'level': 1,
                    })
                    for child in tax.get('children', []):
                        lines.append({
                            'id': child['obj'].id,
                            'name': '   ' + child['obj'].name + ' (' + str(child['obj'].amount) + ')',
                            'type': 'tax_id',
                            'footnotes': self.env.context['context_id']._get_footnotes('tax_id', child['obj'].id),
                            'unfoldable': False,
                            'columns': sum([[self._format(period['net'] * sign), self._format(period['tax'] * sign)] for period in child['periods']], []),
                            'level': 2,
                        })
            line_id += 1
        return lines

    @api.model
    def get_title(self):
        return _('Tax Report')

    @api.model
    def get_name(self):
        return 'generic_tax_report'

    @api.model
    def get_report_type(self):
        return 'date_range'

    @api.model
    def get_template(self):
        return 'account_reports.report_financial'


class AccountReportContextTax(models.TransientModel):
    _name = "account.report.context.tax"
    _description = "A particular context for the generic tax report"
    _inherit = "account.report.context.common"

    def get_report_obj(self):
        return self.env['account.generic.tax.report']

    def get_columns_names(self):
        is_xls = self.env.context.get('is_xls', False)
        columns = [_('Net') + ('\n' if is_xls else '<br/>') + self.get_full_date_names(self.date_to, self.date_from), _('Tax')]
        if self.comparison and (self.periods_number == 1 or self.date_filter_cmp == 'custom'):
            columns += [_('Net') + ('\n' if is_xls else '<br/>') + self.get_cmp_date(), _('Tax')]
        else:
            for period in self.get_cmp_periods(display=True):
                columns += [_('Net') + ('\n' if is_xls else '<br/>') + str(period), _('Tax')]
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

    def get_action(self, tax_type, active_id):
        name = tax_type == 'net' and _('Net Tax Lines') or _('Tax Lines')
        domain = [('date', '>=', self.date_from), ('date', '<=', self.date_to)]
        if not self.all_entries:
            domain.append(('move_id.state', '=', 'posted'))
        if tax_type == 'net':
            domain.append(('tax_ids', 'in', [active_id]))
        elif tax_type == 'tax':
            domain.append(('tax_line_id', 'in', [active_id]))
        return {
            'name': name,
            'res_model': 'account.move.line',
            'domain': domain,
        }
