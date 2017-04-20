# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning
import openerp.addons.decimal_precision as dp
from datetime import date, datetime

DEFAULT_SERVER_DATE_FORMAT = "%Y-%m-%d"


class view(models.Model):
    _inherit = 'ir.ui.view'

    type = fields.Selection([
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
        ('reserve_fund_dashboard', 'reserve_fund_dashboard'),
        ('search', 'Search'),
        ('qweb', 'QWeb')], string='View Type')


class dtdream_reserve_fund_dashboard(models.Model):
    _name = 'dtdream.reserve.fund.dashboard'
    _description = u"仪表盘"

    @api.model
    def retrieve_reserve_fund_dashboard(self):

        res = {"receipts_is_draft": 0,
               "receipts_approvaled_by_me": 0,
               "receipts_approvaling_by_me": 0,
               "receipts_not_off":0,
               "receipts_out_time":0}
        # draft receipts
        res['receipts_is_draft'] = self.env['dtdream.reserve.fund'].search_count([('state', '=', '草稿'), ('applicant.user_id', '=', self.env.user.id)])

        # receipts approvaling by me
        res['receipts_approvaling_by_me'] = self.env['dtdream.reserve.fund'].search_count([('current_handler.user_id', '=', self.env.user.id)])

        # receipts approvaled by me
        res['receipts_approvaled_by_me'] = self.env['dtdream.reserve.fund'].search_count([('his_handler.user_id', '=', self.env.user.id)])

        res["receipts_not_off"] = self.env['dtdream.reserve.fund'].search_count([('applicant.user_id', '=', self.env.user.id),('state', '=', '已付款'), ('if_off', '=', False)])
        res["receipts_out_time"] = self.env['dtdream.reserve.fund'].search_count([('applicant.user_id', '=', self.env.user.id),('state', '=', '已付款'), ('if_off', '=', False), ('is_out_time', '=', True)])

        return res
