# -*- coding: utf-8 -*-
from openerp import models, fields, api
from datetime import date,datetime
import time
import math

from ..configure import configure
config = configure.dtdream_notice_config()


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
        ('rd_dashboard', 'rd_dashboard'),
        ('search', 'Search'),
        ('qweb', 'QWeb')], string='View Type')


class dtdream_rd_dashboard(models.Model):
    _name = 'dtdream.rd.dashboard'

    @api.model
    def retrieve_rd_dashboard(self):
        res={
            "submit_product":0,
            "submit_version": 0,
        }
        uid = self.env.user.id
        em = self.env['hr.employee'].search([('user_id', '=', self.env.uid)])
        appr= self.env['dtdream_prod_appr'].search(['|','|','|','|','|',('department','=',em.department_id.id),
                                              ('department_2','=',em.department_id.id),('create_uid','=',uid),('current_approver_user','=',uid),
                                              ('his_app_user','=',uid),('followers_user','=',uid)])
        version = self.env['dtdream_rd_version'].search(['|', '|', '|', '|', '|', ('department', '=', em.department_id.id),
                                                     ('department_2', '=', em.department_id.id),
                                                     ('create_uid', '=', uid), ('current_approver_user', '=', uid),
                                                     ('his_app_user', '=', uid), ('followers_user', '=', uid)])
        res['submit_product'] = len(appr)
        res['submit_version'] = len(version)

        return res
    def _get_lists(self):
         return config.get_config_model_list()

    def _get_parent_id(self,menu=None):
        if len(menu.parent_id)>0:
            return self._get_parent_id(menu.parent_id)
        else:
            return menu.id


    @api.model
    def get_all_affairs(self, currentpage=None):
        t_in = time.clock()
        affairs = []
        lists = self._get_lists()
        for list in lists:
            model = list['model']
            affairchild = self.env[model].get_affair()
            affairs += affairchild
        totalpage = int(math.ceil(len(affairs) / 5.0))
        for page in range(totalpage):
            for i in range(5):
                if len(affairs) > page * 5 + i:
                    affairs[page * 5 + i]['affair_id'] = 'affair_' + str(page + 1) + '_'

        data = {'affairs': affairs, 'currentPage': currentpage, 'totalPage': totalpage}
        print "========================get_all_affairs=====================", time.clock() - t_in
        return data

    @api.model
    def get_all_dones(self, currentpage=None):
        t_in = time.clock()
        dones = []
        lists = self._get_lists()
        for list in lists:
            model = list['model']
            affairchild = self.env[model].get_done()
            dones += affairchild
        totalpage = int(math.ceil(len(dones) / 5.0))
        for page in range(totalpage):
            for i in range(5):
                if len(dones) > page * 5 + i:
                    dones[page * 5 + i]['done_id'] = 'done_' + str(page + 1) + '_'

        data = {'dones': dones, 'currentPage': currentpage, 'totalPage': totalpage}
        print "========================get_all_dones=====================", time.clock() - t_in
        return data



    @api.model
    def get_all_applies(self, currentpage=None):
        t_in = time.clock()
        applies = []
        lists = self._get_lists()
        for list in lists:
            model = list['model']
            applychild = self.env[model].get_apply()
            applies+=applychild
        totalpage = int(math.ceil(len(applies) / 5.0))
        for page in range(totalpage):
            for i in range(5):
                if len(applies) > page * 5 + i:
                    applies[page * 5 + i]['apply_id'] = 'apply_' + str(page + 1) + '_'

        data = {'applies': applies, 'currentPage': currentpage,'totalPage':totalpage}
        print "========================get_all_applies=====================", time.clock() - t_in
        return data