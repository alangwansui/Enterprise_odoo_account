# -*- coding: utf-8 -*-
from openerp import models, fields, api
import math
from datetime import datetime
import time

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

    def _get_lists(self,menu_date=None):
        workflows = self.env['workflow'].search([])
        lists = []
        children = menu_date['children']
        action_menus = self.get_action_menu(children)
        for menu in action_menus:
            action_id = str(menu['action']).split(',')[1]
            act_window = self.env['ir.actions.act_window'].search([('id', '=', action_id)])
            model = act_window.res_model
            for workflow in workflows:
                if workflow.osv == model:
                    lists.append(model)
            if "dtdream_prod_appr" in lists:
                lists.extend(['dtdream_execption', 'dtdream.prod.suspension', 'dtdream.prod.suspension.restoration',
                              'dtdream.prod.termination'])
        lists = set(lists)
        return lists


    @api.model
    def get_all_affairs(self,menu_date=None,currentPage=None):
        t_in = time.clock()
        affairs = []
        lists = self._get_lists(menu_date=menu_date)

        #可查看到的所有的模型lists
        em = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)])
        for list in lists:
            act_window = self.env['ir.actions.act_window'].search([('res_model', '=', list)])[0]
            action_id = 'ir.actions.act_window,' + str(act_window.id)
            menu = self.env['ir.ui.menu'].search([('action', '=', action_id)])
            menu_id = self._get_parent_id(menu)
            configs = config.get_fields_by_model(model_name=list)
            if configs:
                fields = configs['fields']
                if self.env[list][fields['dangqianzerenren']]._name == 'hr.employee':
                   results = self.env[list].search([(fields['dangqianzerenren'], '=', em.id)])
                else:
                    results  = self.env[list].search([(fields['dangqianzerenren'],'=',self.env.user.id)])
                for result in results:
                    b = result[fields['shenqishijian']]
                    deferdays = (datetime.now() - datetime.strptime(b, '%Y-%m-%d %H:%M:%S')).days
                    if deferdays == 0:
                        defer = False
                    else:
                        defer = True
                    affair={
                        'name':fields['description'],
                        'defer' :defer,
                        'user' : em.name,
                        'date':result[fields['shenqishijian']],
                        'url': '/web#id=' + str(result.id) + '&view_type=form&model='+list+'&menu_id='+str(menu_id),
                        'deferdays':deferdays
                    }
                    affairs.append(affair)
        totalPage= int(math.ceil(len(affairs)/5.0))
        for page in range(totalPage):
            for i in range(5):
                if len(affairs)>page*5+i:
                    affairs[page*5+i]['affair_id']='affair_'+str(page+1)+'_';

        data = {'affairs': affairs, 'currentPage': currentPage, 'totalPage':totalPage}
        print "========================get_all_affairs=====================", time.clock() - t_in
        return data

    @api.model
    def get_all_applies(self, menu_date=None,currentPage=None):
        t_in = time.clock()
        applies = []
        lists = self._get_lists(menu_date=menu_date)

        # 可查看到的所有的模型lists
        for list in lists:
            act_window = self.env['ir.actions.act_window'].search([('res_model', '=', list)])[0]
            action_id = 'ir.actions.act_window,'+str(act_window.id)
            menu = self.env['ir.ui.menu'].search([('action', '=', action_id)])
            menu_id = self._get_parent_id(menu)
            configs = config.get_fields_by_model(model_name=list)
            if configs:
                fields = configs['fields']
                resultsb = self.env[list].search(['|', (fields['shenqingren'], '=', self.env.user.id), ('create_uid', '=', self.env.user.id)])
                for result in resultsb:
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
                        'date': result[fields['shenqishijian']],
                        'url': '/web#id=' + str(result.id) + '&view_type=form&model=' + list+'&menu_id='+str(menu_id),
                        'deferdays':deferdays
                    }
                    applies.append(apply)
        totalPage=int(math.ceil(len(applies)/5.0))
        for page in range(totalPage):
            for i in range(5):
                if len(applies)>page*5+i:
                    applies[page*5+i]['apply_id']='apply_'+str(page+1)+'_';
        data = {'applies': applies, 'currentPage': currentPage, 'totalPage': totalPage}
        print "========================get_all_applies=====================", time.clock() - t_in
        return data