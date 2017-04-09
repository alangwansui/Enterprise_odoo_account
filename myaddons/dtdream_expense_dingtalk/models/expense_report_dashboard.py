# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning
import openerp.addons.decimal_precision as dp
from datetime import date,datetime

DEFAULT_SERVER_DATE_FORMAT = "%Y-%m-%d"

class view(models.Model):
    _inherit = 'ir.ui.view'

    type= fields.Selection([
        ('tree', 'Tree'),
        ('form', 'Form'),
        ('graph', 'Graph'),
        ('pivot', 'Pivot'),
        ('calendar', 'Calendar'),
        ('diagram', 'Diagram'),
        ('gantt', 'Gantt'),
        ('kanban', 'Kanban'),
        ('sales_team_dashboard', 'Sales Team Dashboard'),
        ('expense_dashboard', 'expense_dashboard'),
        ('search', 'Search'),
        ('qweb', 'QWeb')], string='View Type')




class dtdream_expense_report_count(models.Model):
    _name = "dtdream.expense.report.dashboard"

    @api.model
    def retrieve_sales_dashboard(self):
        res={
            # add by g0335
            "endTime": "",

            "details_not_belong_to_details":0,

            "receipts_is_draft":0,

            "receipts_is_outtime": 0,
            "receipts_amount_is_outtime": 0,

            "receipts_is_approvaling": 0,
            "receipts_amount_is_approvaling": 0,

            "receipts_is_submited": 0,
            "receipts_amount_is_submited": 0,

            "receipts_is_finished": 0,
            "receipts_amount_is_finished": 0,

            "receipts_approvaled_by_me": 0,
            "receipts_approvaling_by_me": 0
        }

        # add by g0335
        res['endTime'] = datetime.today().strftime(DEFAULT_SERVER_DATE_FORMAT)

        # details do not belong to any details
        res['details_not_belong_to_details'] = self.env['dtdream.expense.record'].search_count([('report_ids','=',False),('create_uid','=',self.env.user.id)])

        # draft receipts
        res['receipts_is_draft'] = self.env['dtdream.expense.report'].search_count([('state','=','draft'),('create_uid','=',self.env.user.id)])

        # outtime receipts
        receipts_is_outtime = self.env['dtdream.expense.report'].search([('is_outtime', '=', True), ('create_uid', '=', self.env.user.id)])
        if receipts_is_outtime:
            res['receipts_is_outtime'] = len(receipts_is_outtime)
            for receipt in receipts_is_outtime:
                res['receipts_amount_is_outtime'] += receipt.outtime_amount
        res['receipts_amount_is_outtime'] = float('%0.2f' % res['receipts_amount_is_outtime'])

        # unfinished receipts
        receipts_is_approvaling = self.env['dtdream.expense.report'].search([('state', '!=', 'yifukuan'), ('create_uid', '=', self.env.user.id)])
        if receipts_is_approvaling:
            res['receipts_is_approvaling'] = len(receipts_is_approvaling)
            for receipt in receipts_is_approvaling:
                res['receipts_amount_is_approvaling'] += receipt.total_shibaoamount
        res['receipts_amount_is_approvaling'] = float('%0.2f' % res['receipts_amount_is_approvaling'])

        # submit receipts
        receipts_is_submited = self.env['dtdream.expense.report'].search(
            [('state','!=','draft'), ('state', '!=', 'yifukuan'), ('create_uid', '=', self.env.user.id)])
        if receipts_is_submited:
            res['receipts_is_submited'] = len(receipts_is_submited)
            for receipt in receipts_is_submited:
                res['receipts_amount_is_submited'] += receipt.total_shibaoamount
        res['receipts_amount_is_submited'] = float('%0.2f' % res['receipts_amount_is_submited'])

        # finished receipts
        receipts_is_finished = self.env['dtdream.expense.report'].search([('state','=','yifukuan'),('create_uid','=',self.env.user.id)])
        if receipts_is_finished:
            res['receipts_is_finished'] = len(receipts_is_finished)
            for receipt in receipts_is_finished:
                res['receipts_amount_is_finished'] += receipt.total_shibaoamount
        res['receipts_amount_is_finished'] = float('%0.2f' % res['receipts_amount_is_finished'])

        # receipts approvaling by me
        res['receipts_approvaling_by_me'] = self.env['dtdream.expense.report'].search_count([('current_handler.user_id','=',self.env.user.id)])

        # receipts approvaled by me
        res['receipts_approvaled_by_me'] = self.env['dtdream.expense.report'].search_count([('hasauditor.user_id', '=', self.env.user.id)])

        # receipts approvaled by not caiwu
        res['receipts_approvaling_by_not_caiwu'] = self.env['dtdream.expense.report'].search_count(
            [('current_handler.user_id', '=', self.env.user.id),
             ('state', '!=', 'jiekoukuaiji'),
             ('state', '!=', 'daifukuan')])

        return res