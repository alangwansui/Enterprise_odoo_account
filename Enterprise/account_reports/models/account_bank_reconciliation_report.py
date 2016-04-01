# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from openerp import models, fields, api, _
from openerp.tools.misc import formatLang


class account_bank_reconciliation_report(models.AbstractModel):
    _name = 'account.bank.reconciliation.report'
    _description = 'Bank reconciliation report'

    line_number = 0

    @api.model
    def get_lines(self, context_id, line_id=None):
        return self.with_context(
            date_to=context_id.date_to,
            journal_id=context_id.journal_id,
            company_ids=context_id.company_ids.ids,
            context_id=context_id,
        )._lines()

    def _format(self, value):
        if self.env.context.get('no_format'):
            return value
        currency_id = self.env.context['journal_id'].currency_id or self.env.context['journal_id'].company_id.currency_id
        if currency_id.is_zero(value):
            # don't print -0.0 in reports
            value = abs(value)
        res = formatLang(self.env, value, currency_obj=currency_id)
        return res

    def add_title_line(self, title, amount):
        self.line_number += 1
        return {
            'id': self.line_number,
            'type': 'line',
            'name': title,
            'footnotes': self.env.context['context_id']._get_footnotes('line', self.line_number),
            'columns': [self.env.context['date_to'], '', self._format(amount)],
            'level': 0,
        }

    def add_subtitle_line(self, title, amount=None):
        self.line_number += 1
        return {
            'id': self.line_number,
            'type': 'line',
            'name': title,
            'footnotes': self.env.context['context_id']._get_footnotes('line', self.line_number),
            'columns': ['', '', amount and self._format(amount) or ''],
            'level': 1,
        }

    def add_total_line(self, amount):
        self.line_number += 1
        return {
            'id': self.line_number,
            'type': 'line',
            'name': '',
            'footnotes': self.env.context['context_id']._get_footnotes('line', self.line_number),
            'columns': ["", "", self._format(amount)],
            'level': 2,
        }

    def add_bank_statement_line(self, line, amount):
        self.line_number += 1
        name = line.name
        return {
            'id': self.line_number,
            'statement_id': line.statement_id.id,
            'type': 'bank_statement_id',
            'name': len(name) >= 85 and name[0:80] + '...' or name,
            'footnotes': self.env.context['context_id']._get_footnotes('bank_statement_id', self.line_number),
            'columns': [line.date, line.ref, self._format(amount)],
            'level': 1,
        }

    @api.model
    def _lines(self):
        lines = []
        #Start amount
        use_foreign_currency = bool(self.env.context['journal_id'].currency_id)
        account_ids = list(set([self.env.context['journal_id'].default_debit_account_id.id, self.env.context['journal_id'].default_credit_account_id.id]))
        lines_already_accounted = self.env['account.move.line'].search([('account_id', 'in', account_ids),
                                                                        ('date', '<=', self.env.context['date_to']),
                                                                        ('company_id', 'in', self.env.context['company_ids'])])
        start_amount = sum([line.amount_currency if use_foreign_currency else line.balance for line in lines_already_accounted])
        lines.append(self.add_title_line(_("Current Balance in Odoo"), start_amount))

        # Un-reconcilied bank statement lines
        move_lines = self.env['account.move.line'].search([('move_id.journal_id', '=', self.env.context['journal_id'].id),
                                                           ('move_id.statement_line_id', '=', False),
                                                           ('user_type_id.type', '!=', 'liquidity'),
                                                           ('date', '<=', self.env.context['date_to']),
                                                           ('company_id', 'in', self.env.context['company_ids'])])
        unrec_tot = 0
        if move_lines:
            tmp_lines = []
            for line in move_lines:
                self.line_number += 1
                tmp_lines.append({
                    'id': self.line_number,
                    'move_id': line.move_id.id,
                    'type': 'move_line_id',
                    'action': line.get_model_id_and_name(),
                    'name': line.name,
                    'footnotes': self.env.context['context_id']._get_footnotes('move_line_id', self.line_number),
                    'columns': [line.date, line.ref, self._format(line.balance)],
                    'level': 1,
                })
                unrec_tot += line.amount_currency if use_foreign_currency else line.balance
            if unrec_tot > 0:
                title = _("Plus Un-Reconciled Bank Statement Lines")
            else:
                title = _("Less Un-Reconciled Bank Statement Lines")
            lines.append(self.add_subtitle_line(title))
            lines += tmp_lines
            lines.append(self.add_total_line(unrec_tot))

        # Outstanding plus
        not_reconcile_plus = self.env['account.bank.statement.line'].search([('statement_id.journal_id', '=', self.env.context['journal_id'].id),
                                                                             ('date', '<=', self.env.context['date_to']),
                                                                             ('journal_entry_ids', '=', False),
                                                                             ('amount', '>', 0),
                                                                             ('company_id', 'in', self.env.context['company_ids'])])
        outstanding_plus_tot = 0
        if not_reconcile_plus:
            lines.append(self.add_subtitle_line(_("Plus Outstanding Payment")))
            for line in not_reconcile_plus:
                lines.append(self.add_bank_statement_line(line, line.amount))
                outstanding_plus_tot += line.amount
            lines.append(self.add_total_line(outstanding_plus_tot))

        # Outstanding less
        not_reconcile_less = self.env['account.bank.statement.line'].search([('statement_id.journal_id', '=', self.env.context['journal_id'].id),
                                                                             ('date', '<=', self.env.context['date_to']),
                                                                             ('journal_entry_ids', '=', False),
                                                                             ('amount', '<', 0),
                                                                             ('company_id', 'in', self.env.context['company_ids'])])
        outstanding_less_tot = 0
        if not_reconcile_less:
            lines.append(self.add_subtitle_line(_("Less Outstanding Receipt")))
            for line in not_reconcile_less:
                lines.append(self.add_bank_statement_line(line, line.amount))
                outstanding_less_tot += line.amount
            lines.append(self.add_total_line(outstanding_less_tot))

        # Final
        computed_stmt_balance = start_amount + outstanding_plus_tot + outstanding_less_tot + unrec_tot
        last_statement = self.env['account.bank.statement'].search([('journal_id', '=', self.env.context['journal_id'].id),
                                       ('date', '<=', self.env.context['date_to']), ('company_id', 'in', self.env.context['company_ids'])], order="date desc, id desc", limit=1)
        real_last_stmt_balance = last_statement.balance_end
        if computed_stmt_balance != real_last_stmt_balance:
            if real_last_stmt_balance - computed_stmt_balance > 0:
                title = _("Plus Unencoded Statements")
            else:
                title = _("Less Unencoded Statements")
            lines.append(self.add_subtitle_line(title, real_last_stmt_balance - computed_stmt_balance))
        lines.append(self.add_title_line(_("Last Statement Balance"), real_last_stmt_balance))
        return lines

    @api.model
    def get_title(self):
        return _("Bank Reconciliation")

    @api.model
    def get_name(self):
        return 'bank_reconciliation'

    @api.model
    def get_report_type(self):
        return 'bank_reconciliation'

    @api.model
    def get_template(self):
        return 'account_reports.report_financial'


class account_report_context_bank_reconciliation(models.TransientModel):
    _name = 'account.report.context.bank.rec'
    _description = 'A particular context for the bank reconciliation report'
    _inherit = 'account.report.context.common'

    def _get_bank_journals(self):
        self.journals = self.env['account.journal'].search([['type', '=', 'bank']])

    journal_id = fields.Many2one('account.journal', string=_("Bank account"))
    journals = fields.One2many('account.journal', string=_("Bank Accounts"), compute=_get_bank_journals)

    def get_report_obj(self):
        return self.env['account.bank.reconciliation.report']

    def get_columns_names(self):
        columns = [_("Date"), _("Reference"), _("Amount")]
        return columns

    @api.multi
    def get_columns_types(self):
        return ['date', 'text', 'number']
