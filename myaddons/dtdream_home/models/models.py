# -*- coding: utf-8 -*-

from openerp import models, fields, api
from ..configure import configure
from datetime import datetime
import time

config = configure.dtdream_notice_config()


class dtdream_home(models.Model):
    _name = 'dtdream_home.dtdream_home'

    @api.model
    def get_record_num(self, user):
        t_in = time.clock()
        user_id = user.get('user_id', None)
        if not user_id:
            return None
        out = len(self.env['dtdream_hr_business.dtdream_hr_business'].search([('name.user_id.id', '=', user_id), ('state', '!=', '5')]))
        special = len(self.env['dtdream.special.approval'].search([('applicant.user_id.id', '=', user_id), ('state', '!=', 'state_05')]))
        expense = len(self.env['dtdream.expense.report'].search([('create_uid_self.id', '=', user_id), ('state','!=','yifukuan')]))
        travel = len(self.env['dtdream.travel.chucha'].search([('name.user_id.id', '=', user_id), ('state','!=','99')]))
        budget = len(self.env['dtdream.budget'].search([('applicant.user_id.id', '=', user_id), ('state','!=','4')]))
        menu_id = self.env['ir.ui.menu'].search([('web_icon', 'ilike', 'dtdream_hr_business')], limit=1).id
        out_url = '/web#menu_id=%s&amp;action_id=%s' % (menu_id, self.env['ir.ui.menu'].search(
            [('name', '=', u'我的申请'), ('parent_id', '=', menu_id)], limit=1).action.id)
        menu_id = self.env['ir.ui.menu'].search([('web_icon', 'ilike', 'dtdream_special_approval')], limit=1).id
        special_url = '/web#menu_id=%s&amp;action_id=%s' % (menu_id, self.env['ir.ui.menu'].search(
            [('name', '=', u'我的申请'), ('parent_id', '=', menu_id)], limit=1).action.id)
        menu_id = self.env['ir.ui.menu'].search([('web_icon', 'ilike', 'dtdream_expense')], limit=1).id
        expense_url = '/web#menu_id=%s&amp;action_id=%s' % (menu_id, self.env['ir.ui.menu'].search(
            [('name', '=', u'我的消费明细'), ('parent_id', '=', menu_id)], limit=1).action.id)

        menu_id = self.env['ir.ui.menu'].search([('web_icon', 'ilike', 'dtdream_travel')], limit=1).id
        travel_url = '/web#menu_id=%s&amp;action_id=%s' % (menu_id, self.env['ir.ui.menu'].search(
            [('name', '=', u'我的申请'), ('parent_id', '=', menu_id)], limit=1).action.id)
        menu_id = self.env['ir.ui.menu'].search([('web_icon', 'ilike', 'dtdream_budget')], limit=1).id
        budget_url = '/web#menu_id=%s&amp;action_id=%s' % (menu_id, self.env['ir.ui.menu'].search(
            [('name', '=', u'我的申请'), ('parent_id', '=', menu_id)], limit=1).action.id)
        print "========================get_record_num=====================", time.clock() - t_in
        return {'out': out, 'special': special, 'expense': expense, 'travel': travel, 'budget': budget,
                'expense_url': expense_url, 'special_url': special_url,'out_url': out_url, 'travel_url': travel_url,
                'budget_url': budget_url, 'my': 0}

    @api.model
    def get_month_record(self, user):
        t_in = time.clock()
        month = ["%s-%02d" % (datetime.today().year-1, m) for m in range(datetime.today().month+1, 13)] +\
                ["%s-%02d" % (datetime.today().year, m) for m in range(1, datetime.today().month+1)]
        total = [0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0, 0]
        completed = [0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0, 0]
        apps_list = []
        user_id = user.get('user_id', None)
        em = self.env['hr.employee'].search([('user_id', '=', user_id)])
        if len(em) == 0:
            grants = {'you': 0, 'fan': 0, 'cash': 0}
            return {'month': month, 'total': total, 'completed': completed, 'grants': grants}
        models = config.get_config_model_list()
        for model in models:
            try:
                if self.env['%s' % model['model']][model['shenqingren']]._name == 'hr.employee':
                    apps = self.env['%s' % model['model']].sudo().search([('%s.user_id.id' % model['shenqingren'], '=', user_id)])
                else:
                    apps = self.env['%s' % model['model']].sudo().search([('%s.id' % model['shenqingren'], '=', user_id)])

                if model['shenqingren']=="PDT":
                    apps=[x for x in apps if x[model['shenqingren']]==em]

                if apps:
                    apps_list.extend(map(lambda x: [model['state_name'], model['state'], x], list(apps)))
            except Exception,e:
                pass
        for state_name, state, app in apps_list:
            date = app.create_date[:7]
            if date in month:
                total_index = month.index(date)
                total[total_index] += 1
            if app[state_name] == state and app.write_date[:7] in month:
                completed_index = month.index(app.write_date[:7])
                completed[completed_index] += 1
        cr = self.env['dtdream.grants.allocation'].search([('create_uid', '=', user_id)])
        grants = {'you': cr.you, 'fan': cr.fan, 'cash': cr.cash}
        print "========================get_month_record=====================", time.clock() - t_in
        return {'month': month, 'total': total, 'completed': completed, 'grants': grants}
