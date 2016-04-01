# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from openerp import models, fields, api, _, osv
from xlwt import Workbook, easyxf
from openerp.exceptions import Warning
from datetime import timedelta, datetime
import calendar
import json


class AccountReportFootnotesManager(models.TransientModel):
    _name = 'account.report.footnotes.manager'
    _description = 'manages footnotes'

    footnotes = fields.One2many('account.report.footnote', 'manager_id')

    @api.multi
    def add_footnote(self, type, target_id, column, number, text):
        self.env['account.report.footnote'].create(
            {'type': type, 'target_id': target_id, 'column': column, 'number': number, 'text': text, 'manager_id': self.id}
        )

    @api.multi
    def edit_footnote(self, number, text):
        footnote = self.footnotes.filtered(lambda s: s.number == number)
        footnote.write({'text': text})

    @api.multi
    def remove_footnote(self, number):
        footnotes = self.footnotes.filtered(lambda s: s.number == number)
        self.write({'footnotes': [(3, footnotes.id)]})


class AccountReportMulticompanyManager(models.TransientModel):
    _name = 'account.report.multicompany.manager'
    _description = 'manages multicompany for reports'

    multi_company = fields.Boolean('Allow multi-company', compute='_get_multi_company', store=False)
    company_ids = fields.Many2many('res.company', relation='account_report_context_company', default=lambda s: [(6, 0, [s.env.user.company_id.id])])
    available_company_ids = fields.Many2many('res.company', relation='account_report_context_available_company', default=lambda s: [(6, 0, s.env.user.company_ids.ids)])

    @api.one
    def _get_multi_company(self):
        group_multi_company = self.env['ir.model.data'].xmlid_to_object('base.group_multi_company')
        if self.create_uid.id in group_multi_company.users.ids:
            self.multi_company = True
        else:
            self.multi_company = False

    @api.multi
    def get_available_company_ids_and_names(self):
        return [[c.id, c.name] for c in self.available_company_ids]

    @api.model
    def get_available_companies(self):
        return self.env.user.company_ids


class AccountReportContextCommon(models.TransientModel):
    _name = "account.report.context.common"
    _description = "A particular context for a financial report"
    _inherits = {'account.report.footnotes.manager': 'footnotes_manager_id', 'account.report.multicompany.manager': 'multicompany_manager_id'}

    @api.model
    def get_context_by_report_name(self, name):
        return self.env[self._report_name_to_report_context()[name]]

    @api.model
    def get_context_name_by_report_name_json(self):
        return json.dumps(self._report_name_to_report_context())

    @api.model
    def get_context_name_by_report_model_json(self):
        return json.dumps(self._report_model_to_report_context())

    def _report_name_to_report_model(self):
        return {
            'financial_report': 'account.financial.html.report',
            'generic_tax_report': 'account.generic.tax.report',
            'followup_report': 'account.followup.report',
            'bank_reconciliation': 'account.bank.reconciliation.report',
            'general_ledger': 'account.general.ledger',
            'coa': 'account.coa.report',
            'l10n_be_partner_vat_listing': 'l10n.be.report.partner.vat.listing',
            'l10n_be_partner_vat_intra': 'l10n.be.report.partner.vat.intra',
        }

    def _report_model_to_report_context(self):
        return {
            'account.financial.html.report': 'account.financial.html.report.context',
            'account.generic.tax.report': 'account.report.context.tax',
            'account.followup.report': 'account.report.context.followup',
            'account.bank.reconciliation.report': 'account.report.context.bank.rec',
            'account.general.ledger': 'account.context.general.ledger',
            'account.coa.report': 'account.context.coa',
            'l10n.be.report.partner.vat.listing': 'l10n.be.partner.vat.listing.context',
            'l10n.be.report.partner.vat.intra': 'l10n.be.partner.vat.intra.context',
        }

    def _report_name_to_report_context(self):
        return dict([(k[0], self._report_model_to_report_context()[k[1]]) for k in self._report_name_to_report_model().items()])

    @api.model
    def get_full_report_name_by_report_name(self, name):
        return self._report_name_to_report_model()[name]

    def get_report_obj(self):
        raise Warning(_('get_report_obj not implemented'))

    @api.depends('date_filter_cmp')
    @api.multi
    def _get_comparison(self):
        for context in self:
            if context.date_filter_cmp == 'no_comparison':
                context.comparison = False
            else:
                context.comparison = True

    @api.model
    def _get_footnotes(self, type, target_id):
        footnotes = self.footnotes.filtered(lambda s: s.type == type and s.target_id == target_id)
        result = {}
        for footnote in footnotes:
            result.update({footnote.column: footnote.number})
        return result

    fold_field = ''
    date_from = fields.Date("Start date")
    date_to = fields.Date("End date")
    all_entries = fields.Boolean('Use all entries (not only posted ones)', default=False, required=True)
    date_filter = fields.Char('Date filter used', default=None)
    next_footnote_number = fields.Integer(default=1, required=True)
    summary = fields.Char(default='')
    comparison = fields.Boolean(compute='_get_comparison', string='Enable comparison', default=False)
    date_from_cmp = fields.Date("Start date for comparison",
                                default=lambda s: datetime.today() + timedelta(days=-395))
    date_to_cmp = fields.Date("End date for comparison",
                              default=lambda s: datetime.today() + timedelta(days=-365))
    cash_basis = fields.Boolean('Enable cash basis columns', default=False)
    date_filter_cmp = fields.Char('Comparison date filter used', default='no_comparison')
    periods_number = fields.Integer('Number of periods', default=1)
    footnotes_manager_id = fields.Many2one('account.report.footnotes.manager', string='Footnotes Manager', required=True, ondelete='cascade')
    multicompany_manager_id = fields.Many2one('account.report.multicompany.manager', string='Multi-company Manager', required=True, ondelete='cascade')

    @api.multi
    def remove_line(self, line_id):
        self.write({self.fold_field: [(3, line_id)]})

    @api.multi
    def add_line(self, line_id):
        self.write({self.fold_field: [(4, line_id)]})

    @api.multi
    def edit_summary(self, text):
        self.write({'summary': text})

    @api.multi
    def get_next_footnote_number(self):
        res = self.next_footnote_number
        self.write({'next_footnote_number': self.next_footnote_number + 1})
        return res

    @api.multi
    def set_next_number(self, num):
        self.write({'next_footnote_number': num})
        return

    def get_columns_names(self):
        raise Warning(_('get_columns_names not implemented'))

    def get_full_date_names(self, dt_to, dt_from=None):
        convert_date = self.env['ir.qweb.field.date'].value_to_html
        date_to = convert_date(dt_to, None)
        dt_to = datetime.strptime(dt_to, "%Y-%m-%d")
        if dt_from:
            date_from = convert_date(dt_from, None)
        if 'month' in self.date_filter:
            return dt_to.strftime('%b %Y')
        if 'quarter' in self.date_filter:
            quarter = (dt_to.month - 1) / 3 + 1
            return dt_to.strftime('Quarter #' + str(quarter) + ' %Y')
        if 'year' in self.date_filter:
            if self.env.user.company_id.fiscalyear_last_day == 31 and self.env.user.company_id.fiscalyear_last_month == 12:
                return dt_to.strftime('%Y')
            else:
                return str(dt_to.year - 1) + ' - ' + str(dt_to.year)
        if not dt_from:
            return _('(As of %s)') % (date_to,)
        return _('(From %s <br/> to  %s)') % (date_from, date_to)

    def get_cmp_date(self):
        if self.get_report_obj().get_report_type() == 'no_date_range':
            return self.get_full_date_names(self.date_to_cmp)
        return self.get_full_date_names(self.date_to_cmp, self.date_from_cmp)

    def get_periods(self):
        res = self.get_cmp_periods()
        if self.get_report_obj().get_report_type() == 'no_date_range':
            res[:0] = [[False, self.date_to]]
        else:
            res[:0] = [[self.date_from, self.date_to]]
            if self.get_report_obj().get_report_type() == 'date_range_extended':
                dt_from = datetime.strptime(self.date_to, "%Y-%m-%d") + timedelta(days=1)
                res[:0] = [[dt_from.strftime("%Y-%m-%d"), False]]
                dt_to = datetime.strptime(res[-1][0], "%Y-%m-%d") - timedelta(days=1)
                res.append([False, dt_to.strftime("%Y-%m-%d")])
        return res

    def get_cmp_periods(self, display=False):
        if not self.comparison:
            return []
        dt_to = datetime.strptime(self.date_to, "%Y-%m-%d")
        if self.get_report_obj().get_report_type() != 'no_date_range':
            dt_from = self.date_from and datetime.strptime(self.date_from, "%Y-%m-%d") or self.env.user.company_id.compute_fiscalyear_dates(dt_to)['date_from']
        columns = []
        if self.date_filter_cmp == 'custom':
            if display:
                return ['Comparison<br />' + self.get_cmp_date(), '%']
            else:
                if self.get_report_obj().get_report_type() == 'no_date_range':
                    return [[False, self.date_to_cmp]]
                return [[self.date_from_cmp, self.date_to_cmp]]
        if self.date_filter_cmp == 'same_last_year':
            columns = []
            for k in xrange(0, self.periods_number):
                dt_to = dt_to.replace(year=dt_to.year - 1)
                if display:
                    if self.get_report_obj().get_report_type() == 'no_date_range':
                        columns += [self.get_full_date_names(dt_to.strftime("%Y-%m-%d"))]
                    else:
                        dt_from = dt_from.replace(year=dt_from.year - 1)
                        columns += [self.get_full_date_names(dt_to.strftime("%Y-%m-%d"), dt_from.strftime("%Y-%m-%d"))]
                else:
                    if self.get_report_obj().get_report_type() == 'no_date_range':
                        columns += [[False, dt_to.strftime("%Y-%m-%d")]]
                    else:
                        dt_from = dt_from.replace(year=dt_from.year - 1)
                        columns += [[dt_from.strftime("%Y-%m-%d"), dt_to.strftime("%Y-%m-%d")]]
            return columns
        if 'month' in self.date_filter:
            for k in xrange(0, self.periods_number):
                dt_to = dt_to.replace(day=1)
                dt_to -= timedelta(days=1)
                if display:
                    columns += [dt_to.strftime('%b %Y')]
                else:
                    if self.get_report_obj().get_report_type() == 'no_date_range':
                        columns += [[False, dt_to.strftime("%Y-%m-%d")]]
                    else:
                        dt_from -= timedelta(days=1)
                        dt_from = dt_from.replace(day=1)
                        columns += [[dt_from.strftime("%Y-%m-%d"), dt_to.strftime("%Y-%m-%d")]]
        elif 'quarter' in self.date_filter:
            quarter = (dt_to.month - 1) / 3 + 1
            year = dt_to.year
            for k in xrange(0, self.periods_number):
                if display:
                    if quarter == 1:
                        quarter = 4
                        year -= 1
                    else:
                        quarter -= 1
                    columns += ['Quarter #' + str(quarter) + ' ' + str(year)]
                else:
                    if dt_to.month == 12:
                        dt_to = dt_to.replace(month=9, day=30)
                    elif dt_to.month == 9:
                        dt_to = dt_to.replace(month=6, day=30)
                    elif dt_to.month == 6:
                        dt_to = dt_to.replace(month=3, day=31)
                    else:
                        dt_to = dt_to.replace(month=12, day=31, year=dt_to.year - 1)
                    if self.get_report_obj().get_report_type() == 'no_date_range':
                        columns += [[False, dt_to.strftime("%Y-%m-%d")]]
                    else:
                        if dt_from.month == 10:
                            dt_from = dt_from.replace(month=7)
                        elif dt_from.month == 7:
                            dt_from = dt_from.replace(month=4)
                        elif dt_from.month == 4:
                            dt_from = dt_from.replace(month=1)
                        else:
                            dt_from = dt_from.replace(month=10, year=dt_from.year - 1)
                        columns += [[dt_from.strftime("%Y-%m-%d"), dt_to.strftime("%Y-%m-%d")]]
        elif 'year' in self.date_filter:
            dt_to = datetime.strptime(self.date_to, "%Y-%m-%d")
            for k in xrange(0, self.periods_number):
                dt_to = dt_to.replace(year=dt_to.year - 1)
                if display:
                    if dt_to.strftime("%m-%d") == '12-31':
                        columns += [dt_to.year]
                    else:
                        columns += [str(dt_to.year - 1) + ' - ' + str(dt_to.year)]
                else:
                    if self.get_report_obj().get_report_type() == 'no_date_range':
                        columns += [[False, dt_to.strftime("%Y-%m-%d")]]
                    else:
                        dt_from = dt_to.replace(year=dt_to.year - 1) + timedelta(days=1)
                        columns += [[dt_from.strftime("%Y-%m-%d"), dt_to.strftime("%Y-%m-%d")]]
        else:
            if self.get_report_obj().get_report_type() != 'no_date_range':
                dt_from = datetime.strptime(self.date_from, "%Y-%m-%d")
                delta = dt_to - dt_from
                delta = timedelta(days=delta.days + 1)
                delta_days = delta.days
                for k in xrange(0, self.periods_number):
                    dt_from -= delta
                    dt_to -= delta
                    if display:
                        columns += [str((k + 1) * delta_days) + ' - ' + str((k + 2) * delta_days) + ' days ago']
                    else:
                        columns += [[dt_from.strftime("%Y-%m-%d"), dt_to.strftime("%Y-%m-%d")]]
            else:
                for k in xrange(0, self.periods_number):
                    dt_to -= timedelta(days=calendar.monthrange(dt_to.year, dt_to.month > 1 and dt_to.month - 1 or 12)[1])
                    if display:
                        columns += [dt_to.strftime('(as of %d %b %Y)')]
                    else:
                        columns += [[False, dt_to.strftime("%Y-%m-%d")]]
        return columns

    @api.model
    def create(self, vals):
        res = super(AccountReportContextCommon, self).create(vals)
        report_type = res.get_report_obj().get_report_type()
        if report_type in ['date_range', 'date_range_cash', 'no_comparison']:
            dt = datetime.today()
            update = {
                'date_from': datetime.today().replace(day=1),
                'date_to': dt.replace(day=calendar.monthrange(dt.year, dt.month)[1]),
                'date_filter': 'this_month',
            }
        elif report_type == 'date_range_extended':
            dt = datetime.today()
            update = {
                'date_from': datetime.today() - timedelta(days=29),
                'date_to': datetime.today(),
                'date_filter': 'custom',
                'date_filter_cmp': 'previous_period',
                'periods_number': 3,
            }
        else:
            update = {
                'date_from': datetime.today(),
                'date_to': datetime.today(),
                'date_filter': 'today',
            }
        res.write(update)
        return res

    def get_xml(self):
        return self.env['account.financial.html.report.xml.export'].do_xml_export(self)

    def get_pdf(self):
        report_obj = self.get_report_obj()
        lines = report_obj.with_context(print_mode=True).get_lines(self)
        base_url = self.env['ir.config_parameter'].sudo().get_param('report.url') or self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        rcontext = {
            'mode': 'print',
            'base_url': base_url,
            'company': self.env.user.company_id,
        }

        body = self.pool['ir.ui.view'].render(
            self._cr, self._uid, "account_reports.report_financial_letter",
            values=dict(rcontext, lines=lines, report=report_obj, context=self),
            context=self.env.context
        )

        header = self.pool['report'].render(
            self._cr, self._uid, [], "report.internal_layout",
            values=rcontext,
            context=self.env.context
        )
        header = self.pool['report'].render(
            self._cr, self._uid, [], "report.minimal_layout",
            values=dict(rcontext, subst=True, body=header),
            context=self.env.context
        )

        landscape = False
        if len(self.get_columns_names()) > 4:
            landscape = True

        return self.env['report']._run_wkhtmltopdf([header], [''], [(0, body)], landscape, self.env.user.company_id.paperformat_id, spec_paperformat_args={'data-report-margin-top': 10, 'data-report-header-spacing': 10})

    @api.multi
    def get_html_and_data(self, given_context=None):
        if given_context is None:
            given_context = {}
        result = {}
        if given_context:
            update = {}
            for field in given_context:
                if field.startswith('add_'):
                    update[field[4:]] = [(4, int(given_context[field]))]
                if field.startswith('remove_'):
                    update[field[7:]] = [(3, int(given_context[field]))]
                if self._fields.get(field) and given_context[field] != 'undefined':
                    if given_context[field] == 'false':
                        given_context[field] = False
                    if given_context[field] == 'none':
                        given_context[field] = None
                    if field == 'company_ids': #  Needs to be treated differently as it's a many2many
                        update[field] = [(6, 0, given_context[field])]
                    else:
                        update[field] = given_context[field]

            self.write(update)
            if 'force_account' in given_context and (not self.date_from or self.date_from == self.date_to):
                self.date_from = self.env.user.company_id.compute_fiscalyear_dates(datetime.strptime(self.date_to, "%Y-%m-%d"))['date_from']
                self.date_filter = 'custom'
        lines = self.get_report_obj().get_lines(self)
        rcontext = {
            'res_company': self.env['res.users'].browse(self.env.uid).company_id,
            'context': self,
            'report': self.get_report_obj(),
            'lines': lines,
            'mode': 'display',
        }
        result['html'] = self.env['ir.model.data'].xmlid_to_object(self.get_report_obj().get_template()).render(rcontext)
        result['report_type'] = self.get_report_obj().get_report_type()
        select = ['id', 'date_filter', 'date_filter_cmp', 'date_from', 'date_to', 'periods_number', 'date_from_cmp', 'date_to_cmp', 'cash_basis', 'all_entries', 'company_ids', 'multi_company']
        result['report_context'] = self.read(select)[0]
        result['xml_export'] = self.env['account.financial.html.report.xml.export'].is_xml_export_available(self.get_report_obj())
        result['fy'] = {
            'fiscalyear_last_day': self.env.user.company_id.fiscalyear_last_day,
            'fiscalyear_last_month': self.env.user.company_id.fiscalyear_last_month,
        }
        result['available_companies'] = self.multicompany_manager_id.get_available_company_ids_and_names()
        return result

    def get_xls(self, response):
        book = Workbook()
        report_id = self.get_report_obj()
        sheet = book.add_sheet(report_id.get_title())

        title_style = easyxf('font: bold true; borders: bottom medium;', num_format_str='#,##0.00')
        level_0_style = easyxf('font: bold true; borders: bottom medium, top medium; pattern: pattern solid;', num_format_str='#,##0.00')
        level_0_style_left = easyxf('font: bold true; borders: bottom medium, top medium, left medium; pattern: pattern solid;', num_format_str='#,##0.00')
        level_0_style_right = easyxf('font: bold true; borders: bottom medium, top medium, right medium; pattern: pattern solid;', num_format_str='#,##0.00')
        level_1_style = easyxf('font: bold true; borders: bottom medium, top medium;', num_format_str='#,##0.00')
        level_1_style_left = easyxf('font: bold true; borders: bottom medium, top medium, left medium;', num_format_str='#,##0.00')
        level_1_style_right = easyxf('font: bold true; borders: bottom medium, top medium, right medium;', num_format_str='#,##0.00')
        level_2_style = easyxf('font: bold true; borders: top medium;', num_format_str='#,##0.00')
        level_2_style_left = easyxf('font: bold true; borders: top medium, left medium;', num_format_str='#,##0.00')
        level_2_style_right = easyxf('font: bold true; borders: top medium, right medium;', num_format_str='#,##0.00')
        level_3_style = easyxf(num_format_str='#,##0.00')
        level_3_style_left = easyxf('borders: left medium;', num_format_str='#,##0.00')
        level_3_style_right = easyxf('borders: right medium;', num_format_str='#,##0.00')
        domain_style = easyxf('font: italic true;', num_format_str='#,##0.00')
        domain_style_left = easyxf('font: italic true; borders: left medium;', num_format_str='#,##0.00')
        domain_style_right = easyxf('font: italic true; borders: right medium;', num_format_str='#,##0.00')
        upper_line_style = easyxf('borders: top medium;', num_format_str='#,##0.00')
        def_style = easyxf(num_format_str='#,##0.00')

        sheet.col(0).width = 10000

        sheet.write(0, 0, '', title_style)

        x = 1
        for column in self.with_context(is_xls=True).get_columns_names():
            sheet.write(0, x, column, title_style)
            x += 1

        y_offset = 1
        lines = report_id.with_context(no_format=True, print_mode=True).get_lines(self)

        for y in range(0, len(lines)):
            if lines[y].get('level') == 0:
                for x in range(0, len(lines[y]['columns']) + 1):
                    sheet.write(y + y_offset, x, None, upper_line_style)
                y_offset += 1
                style_left = level_0_style_left
                style_right = level_0_style_right
                style = level_0_style
            elif lines[y].get('level') == 1:
                for x in range(0, len(lines[y]['columns']) + 1):
                    sheet.write(y + y_offset, x, None, upper_line_style)
                y_offset += 1
                style_left = level_1_style_left
                style_right = level_1_style_right
                style = level_1_style
            elif lines[y].get('level') == 2:
                style_left = level_2_style_left
                style_right = level_2_style_right
                style = level_2_style
            elif lines[y].get('level') == 3:
                style_left = level_3_style_left
                style_right = level_3_style_right
                style = level_3_style
            elif lines[y].get('type') != 'line':
                style_left = domain_style_left
                style_right = domain_style_right
                style = domain_style
            else:
                style = def_style
                style_left = def_style
                style_right = def_style
            sheet.write(y + y_offset, 0, lines[y]['name'], style_left)
            for x in xrange(1, len(lines[y]['columns']) + 1):
                if isinstance(lines[y]['columns'][x - 1], tuple):
                    lines[y]['columns'][x - 1] = lines[y]['columns'][x - 1][0]
                if x < len(lines[y]['columns']):
                    sheet.write(y + y_offset, x, lines[y]['columns'][x - 1], style)
                else:
                    sheet.write(y + y_offset, x, lines[y]['columns'][x - 1], style_right)
        if lines:
            for x in xrange(0, len(lines[0]['columns']) + 1):
                sheet.write(len(lines) + y_offset, x, None, upper_line_style)

        book.save(response.stream)

    # Tries to find the corresponding context (model name and id) and creates it if none is found.
    @api.model
    def return_context(self, report_model, given_context, report_id=None):
        context_model = self._report_model_to_report_context()[report_model]
        # Fetch the context_id or create one if none exist.
        # Look for a context with create_uid = current user (and with possibly a report_id)
        domain = [('create_uid', '=', self.env.user.id)]
        if report_id:
            domain.append(('report_id', '=', int(report_id)))
        context = False
        for c in self.env[context_model].search(domain):
            if set(c.available_company_ids.ids) == set(self.env.user.company_ids.ids):
                context = c
                break
        if context and (given_context.get('force_fy') or (report_model == 'account.bank.reconciliation.report' and given_context.get('active_id'))):
            context.unlink()
            context = self.env[context_model].browse([]) # set it to an empty set to indicate the contexts have been removed
        if not context:
            create_vals = {}
            if report_id:
                create_vals['report_id'] = report_id
            if 'force_fy' in given_context:
                create_vals['force_fy'] = True
            if report_model == 'account.bank.reconciliation.report' and given_context.get('active_id'):
                create_vals['journal_id'] = given_context['active_id']
            context = self.env[context_model].create(create_vals)
        if 'force_account' in given_context:
            context.unfolded_accounts = [(6, 0, [given_context['active_id']])]
        return [context_model, context.id]


class AccountReportFootnote(models.TransientModel):
    _name = "account.report.footnote"
    _description = "Footnote for reports"

    type = fields.Char()
    target_id = fields.Integer()
    column = fields.Integer()
    number = fields.Integer()
    text = fields.Char()
    manager_id = fields.Many2one('account.report.footnotes.manager')
