# -*- coding: utf-8 -*-
from openerp import models, fields, api
import math
from datetime import datetime
import time
import threading
from openerp.api import Environment
mutex = threading.Lock()

from ..configure import configure
config = configure.dtdream_notice_config()
action_menu=[]
class dtdream_content_event_affairs(models.Model):
    _name = 'dtdream.content.event.affairs'


    @api.model
    def get_action_menu(self,children=None):
        for menu in children:
            childr = menu['children']
            if menu['action']:
                action_menu.append(menu)
            elif childr:
                self.get_action_menu(childr)
        return action_menu

    def _get_parent_id(self,menu=None):
        if len(menu.parent_id)>0:
            return self._get_parent_id(menu.parent_id)
        else:
            return menu.id

    def yyy(self, lists, action_menus,workflows):
        mutex.acquire()
        with Environment.manage():
            for menu in action_menus:
                action_id = str(menu['action']).split(',')[1]
                act_window = self.env['ir.actions.act_window'].sudo().search([('id', '=', action_id)])
                model = act_window.res_model
                for workflow in workflows:
                    if workflow.osv == model:
                        lists.append(model)
        mutex.release()

    def _get_lists(self,menu_date=None):
        workflows = self.env['workflow'].sudo().search([])
        lists = []
        # children = menu_date['children']
        # action_menus = self.get_action_menu(children)
        # for menu in action_menus:
        #     action_id = str(menu['action']).split(',')[1]
        #     act_window = self.env['ir.actions.act_window'].search([('id', '=', action_id)])
        #     model = act_window.res_model
        models = config.get_config_model_list()
        for model in models:
            for workflow in workflows:
                if workflow.osv == model['model']:
                    lists.append(model['model'])
            if "dtdream_prod_appr" in lists:
                lists.extend(['dtdream_execption', 'dtdream.prod.suspension', 'dtdream.prod.suspension.restoration',
                              'dtdream.prod.termination'])
        lists = set(lists)
        return lists

    #待我处理的事项
    @api.model
    # def get_all_affairs(self, menu_date=None, currentPage=None):
    def get_all_affairs(self,menu_date=None):
        t_in = time.clock()
        affairs = []
        lists = self._get_lists(menu_date=menu_date)
        resultList=[]
        #可查看到的所有的模型lists
        em = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)])
        if len(em) == 0:
            data = {'affairs': affairs, 'currentPage': 1, 'totalPage': 0}
            return data
        for list in lists:
            configs = config.get_fields_by_model(model_name=list)
            if configs:
                fields = configs['fields']
                if self.env[list][fields['dangqianzerenren']]._name == 'hr.employee':
                   results = self.env[list].sudo().search([(fields['dangqianzerenren'], '=', em.id),(fields['state_name'], '!=',fields['state'])])
                else:
                    results  = self.env[list].sudo().search([(fields['dangqianzerenren'],'=',self.env.user.id),(fields['state_name'], '!=',fields['state'])])
                resultList+=results
        for result in resultList:
            configs = config.get_fields_by_model(model_name=result._name)
            fields = configs['fields']
            menu_id = self._get_menu_id(result)
            b = result[fields['shenqishijian']]
            shenqingren=""
            if result[fields['shenqingren']]._name == 'hr.employee':
                shenqingren = result[fields['shenqingren']].name
            else:
                employee = self.env['hr.employee'].search([('user_id', '=', result[fields['shenqingren']].id)])
                shenqingren= employee.name

            deferdays = (datetime.now() - datetime.strptime(b, '%Y-%m-%d %H:%M:%S')).days
            if deferdays == 0:
                defer = False
            else:
                defer = True
            affair={
                'name':fields['description'],
                'defer' :defer,
                'user' : shenqingren,
                'date':result[fields['shenqishijian']][:10],
                'url': '/web#id=' + str(result.id) + '&view_type=form&model='+result._name+'&menu_id='+str(menu_id),
                'deferdays':deferdays
            }
            affairs.append(affair)
        # totalPage= int(math.ceil(len(affairs)/5.0))
        # for page in range(totalPage):
        #     for i in range(5):
        #         if len(affairs)>page*5+i:
        #             affairs[page*5+i]['affair_id']='affair_'+str(page+1)+'_';

        # data = {'affairs': affairs, 'currentPage': currentPage, 'totalPage':totalPage}
        data = {'affairs': affairs}
        print "========================get_all_affairs=====================", time.clock() - t_in
        return data

    @api.model
    # def get_all_applies(self, menu_date=None, currentPage=None):
    def get_all_applies(self, menu_date=None):
        t_in = time.clock()
        applies = []
        resultList=[]
        lists = self._get_lists(menu_date=menu_date)
        # 可查看到的所有的模型lists
        em = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)])
        if len(em)==0:
            data = {'applies': applies, 'currentPage': 1, 'totalPage': 0}
            return data
        for list in lists:
            configs = config.get_fields_by_model(model_name=list)
            if configs:
                fields = configs['fields']
                if fields['shenqingren'] == "PDT":
                    if self.env[list][fields['shenqingren']]._name == 'hr.employee':
                        resultsb = self.env[list].sudo().search(
                            ['&', (fields['state_name'], 'not in', fields['stateList']),(fields['state_name'], '!=',fields['state'])])
                    else:
                        resultsb = self.env[list].sudo().search(
                            ['&', (fields['state_name'], 'not in', fields['stateList']),(fields['state_name'], '!=',fields['state'])])
                    resultsb = [x for x in resultsb if x[fields['shenqingren']] == em]
                else:
                    if self.env[list][fields['shenqingren']]._name == 'hr.employee':
                        resultsb = self.env[list].sudo().search(
                            ['&', (fields['state_name'], 'not in', fields['stateList']), '&', (fields['shenqingren'], '=', em.id),(fields['state_name'], '!=',fields['state'])])
                    else:
                        resultsb = self.env[list].sudo().search(
                            ['&', (fields['state_name'], 'not in', fields['stateList']), '&', (fields['shenqingren'], '=', self.env.user.id),(fields['state_name'], '!=',fields['state'])])


                resultList+=resultsb
        for result in resultList:
            configs = config.get_fields_by_model(model_name=result._name)
            fields = configs['fields']
            if len(result[fields['dangqianzerenren']])>0:
                menu_id = self._get_menu_id(result)
                dangqianzerenren = ''
                for zenrenren in result[fields['dangqianzerenren']]:
                    if zenrenren._name == 'hr.employee':
                        dangqianzerenren += zenrenren.name + ','
                    else:
                        employee = self.env['hr.employee'].search([('user_id', '=', zenrenren.id)])
                        if employee:
                            dangqianzerenren += employee.name + ','
                if len(dangqianzerenren)>1:
                    dangqianzerenren = dangqianzerenren[:-1]
                if len(dangqianzerenren)>6:
                    dangqianzerenren = dangqianzerenren[:6]+u'...'
                b = result[fields['shenqishijian']]
                deferdays = (datetime.now() - datetime.strptime(b, '%Y-%m-%d %H:%M:%S')).days
                if deferdays==0:
                    defer=False
                else:
                    defer = True
                apply = {
                    'name': fields['description'],
                    'defer': defer,
                    'user': dangqianzerenren,
                    'date': result[fields['shenqishijian']][:10],
                    'url': '/web#id=' + str(result.id) + '&view_type=form&model=' + result._name+'&menu_id='+str(menu_id),
                    'deferdays':deferdays
                }
                applies.append(apply)
        # totalPage=int(math.ceil(len(applies)/5.0))
        # for page in range(totalPage):
        #     for i in range(5):
        #         if len(applies)>page*5+i:
        #             applies[page*5+i]['apply_id']='apply_'+str(page+1)+'_';
        # data = {'applies': applies, 'currentPage': currentPage, 'totalPage': totalPage}
        data = {'applies': applies}
        print "========================get_all_applies=====================", time.clock() - t_in
        return data

    def _get_menu_id(self, result):
        act_windows = self.env['ir.actions.act_window'].sudo().search([('res_model', '=', result._name)])
        menu = None
        for act_window in act_windows:
            action_id = 'ir.actions.act_window,' + str(act_window.id)
            menu = self.env['ir.ui.menu'].sudo().search([('action', '=', action_id)])
            if len(menu)>0:
                break
        menu_id = self._get_parent_id(menu)
        return menu_id