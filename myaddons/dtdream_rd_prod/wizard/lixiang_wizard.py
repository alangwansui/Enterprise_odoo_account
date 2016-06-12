# -*- coding: utf-8 -*-
from openerp import models, fields, api
from openerp.exceptions import ValidationError

class lxWizard(models.TransientModel):
    _name = 'dtdream_prod_appr.wizard'
    reason = fields.Char()

    @api.one
    def btn_confirm(self):
        current_lixiang = self.env['dtdream_prod_appr'].browse(self._context['active_id'])
        if current_lixiang.state=='state_00':
            current_lixiang.signal_workflow('btn_to_lixiang')
        elif current_lixiang.state=='state_01':
            current_lixiang.signal_workflow('btn_to_ztsj')
        elif current_lixiang.state=='state_02':
            current_lixiang.signal_workflow('btn_to_ddkf')
        elif current_lixiang.state=='state_03':
            current_lixiang.signal_workflow('btn_to_yzfb')
        elif current_lixiang.state=='state_04':
            current_lixiang.signal_workflow('btn_to_jieshu')


class lxWizardappr(models.TransientModel):
    _name = 'dtdream_prod_appr.wizardappr'
    reason = fields.Char()

    def get_base_url(self,cr,uid):
        base_url = self.pool.get('ir.config_parameter').get_param(cr, uid, 'web.base.url')
        return base_url

    def get_mail_server_name(self):
        return self.env['ir.mail_server'].search([], limit=1).smtp_user

#立项、总体设计阶段内部的提交
    @api.one
    def btn_confirm(self):
        current_lixiang = self.env['dtdream_prod_appr'].browse(self._context['active_id'])
        if current_lixiang.state=="state_01":
            lg = len(current_lixiang.version_ids)
            if lg<=0:
               raise ValidationError("提交项目时必须至少有一个版本")
            current_lixiang.write({'is_lixiangappred':True})
            current_lixiang.current_approver_user = [(5,)]
            records = self.env['dtdream_rd_approver'].search([('pro_state','=',current_lixiang.state),('level','=','level_01')])           #审批人配置
            rold_ids = []
            for record in records:
                rold_ids +=[record.name.id]
            appro = self.env['dtdream_rd_role'].search([('role_id','=',current_lixiang.id),('cof_id','in',rold_ids),('person','!=',False)]) #产品中角色配置
            self.current_approver_user = [(5,)]
            for record in appro:
                self.env['dtdream_rd_process'].create({"role":record.cof_id.id, "process_id":current_lixiang.id,'pro_state':current_lixiang.state,'approver':record.person.id,'approver_old':record.person.id,'level':'level_01'})       #审批意见记录创建
                self.write({'current_approver_user': [(4, record.person.user_id.id)]})

                subject=current_lixiang.department.name+u"/"+current_lixiang.department_2.name+u"的"+current_lixiang.name+u"待您审批"
                appellation = record.person.name+u",您好"
                content = current_lixiang.department.name+u"的"+current_lixiang.name+u"的立项阶段待您审批"
                base_url = self.get_base_url()
                link = '/web#id=%s&view_type=form&model=dtdream_prod_appr' % current_lixiang.id
                url = base_url+link
                self.env['mail.mail'].create({
                    'body_html': u'''<p>%s</p>
                                 <p>%s</p>
                                 <p> 请点击链接进入:
                                 <a href="%s">%s</a></p>
                                <p>dodo</p>
                                 <p>万千业务，简单有do</p>
                                 <p>%s</p>''' % (appellation,content, url,url,current_lixiang.write_date[:10]),
                    'subject': '%s' % subject,
                    'email_to': '%s' % record.person.work_email,
                    'auto_delete': False,
                    'email_from':self.get_mail_server_name(),
                }).send()


            processes = self.env['dtdream_rd_process'].search([('process_id','=',current_lixiang.id),('pro_state','=','state_01'),('level','=','level_01'),('is_new','=',True)])
            if len(processes)==0:
                ctd = self.env['dtdream_rd_approver'].search([('department','=',current_lixiang.department.id)],limit=1)
                if not current_lixiang.department.manager_id:
                    raise ValidationError(u"请配置%s的部门主管" %(current_lixiang.department.name))
                self.env['dtdream_rd_process'].create({"role":ctd.name.id,"process_id":current_lixiang.id,'pro_state':current_lixiang.state,'approver':current_lixiang.department.manager_id.id,'approver_old':current_lixiang.department.manager_id.id,'level':'level_02'})       #审批意见记录创建
                self.current_approver_user = [(5,)]
                self.write({'current_approver_user': [(4, current_lixiang.department.manager_id.user_id.id)]})

                subject=current_lixiang.department.name+u"/"+current_lixiang.department_2.name+u"的"+current_lixiang.name+u"待您审批"
                appellation = current_lixiang.department.manager_id.name+u",您好"
                content = current_lixiang.department.name+u"的"+current_lixiang.name+u"的立项阶段待您审批"
                base_url = self.get_base_url()
                link = '/web#id=%s&view_type=form&model=dtdream_prod_appr' % current_lixiang.id
                url = base_url+link
                self.env['mail.mail'].create({
                    'body_html': u'''<p>%s</p>
                                 <p>%s</p>
                                 <p> 请点击链接进入:
                                 <a href="%s">%s</a></p>
                                <p>dodo</p>
                                 <p>万千业务，简单有do</p>
                                 <p>%s</p>''' % (appellation,content, url,url,current_lixiang.write_date[:10]),
                    'subject': '%s' % subject,
                    'email_to': '%s' % current_lixiang.department.manager_id.work_email,
                    'auto_delete': False,
                    'email_from':self.get_mail_server_name(),
                }).send()

        if current_lixiang.state=="state_02":
            current_lixiang.write({'is_appred':True})
            current_lixiang.current_approver_user = [(5,)]
            records = self.env['dtdream_rd_approver'].search([('pro_state','=','state_02'),('level','=','level_01')])           #审批人配置
            rold_ids = []
            for record in records:
                rold_ids +=[record.name.id]
            appro = self.env['dtdream_rd_role'].search([('role_id','=',current_lixiang.id),('cof_id','in',rold_ids),('person','!=',False)]) #产品中角色配置
            for record in appro:
                self.env['dtdream_rd_process'].create({"role":record.cof_id.id, "ztsj_process_id":current_lixiang.id,'pro_state':'state_02','approver':record.person.id,'approver_old':record.person.id,'level':'level_01'})       #审批意见记录创建
                current_lixiang.write({'current_approver_user': [(4, record.person.user_id.id)]})

                subject=current_lixiang.department.name+u"/"+current_lixiang.department_2.name+u"的"+current_lixiang.name+u"待您审批"
                appellation = record.person.name+u",您好"
                content = current_lixiang.department.name+u"的"+current_lixiang.name+u"的总体设计阶段待您审批"
                base_url = self.get_base_url()
                link = '/web#id=%s&view_type=form&model=dtdream_prod_appr' % current_lixiang.id
                url = base_url+link
                self.env['mail.mail'].create({
                    'body_html': u'''<p>%s</p>
                                 <p>%s</p>
                                 <p> 请点击链接进入:
                                 <a href="%s">%s</a></p>
                                <p>dodo</p>
                                 <p>万千业务，简单有do</p>
                                 <p>%s</p>''' % (appellation,content, url,url,current_lixiang.write_date[:10]),
                    'subject': '%s' % subject,
                    'email_to': '%s' % record.person.work_email,
                    'auto_delete': False,
                    'email_from':self.get_mail_server_name(),
                }).send()

            processes = self.env['dtdream_rd_process'].search([('ztsj_process_id','=',current_lixiang.id),('pro_state','=','state_02'),('level','=','level_01'),('is_new','=',True)])
            if len(processes)==0:
                ctd = self.env['dtdream_rd_approver'].search([('department','=',current_lixiang.department.id)],limit=1)
                if not current_lixiang.department.manager_id:
                    raise ValidationError(u"请配置%s的部门主管" %(current_lixiang.department.name))
                self.env['dtdream_rd_process'].create({"role":ctd.name.id,"ztsj_process_id":current_lixiang.id,'pro_state':current_lixiang.state,'approver':current_lixiang.department.manager_id.id,'approver_old':current_lixiang.department.manager_id.id,'level':'level_02'})       #审批意见记录创建
                current_lixiang.current_approver_user = [(5,)]
                current_lixiang.write({'current_approver_user': [(4, current_lixiang.department.manager_id.user_id.id)]})
                subject=current_lixiang.department.name+u"/"+current_lixiang.department_2.name+u"的"+current_lixiang.name+u"待您审批"
                appellation = current_lixiang.department.manager_id.name+u",您好"
                content = current_lixiang.department.name+u"的"+current_lixiang.name+u"的总体设计阶段待您审批"
                base_url = self.get_base_url()
                link = '/web#id=%s&view_type=form&model=dtdream_prod_appr' % current_lixiang.id
                url = base_url+link
                self.env['mail.mail'].create({
                    'body_html': u'''<p>%s</p>
                                 <p>%s</p>
                                 <p> 请点击链接进入:
                                 <a href="%s">%s</a></p>
                                <p>dodo</p>
                                 <p>万千业务，简单有do</p>
                                 <p>%s</p>''' % (appellation,content, url,url,current_lixiang.write_date[:10]),
                    'subject': '%s' % subject,
                    'email_to': '%s' % current_lixiang.department.manager_id.work_email,
                    'auto_delete': False,
                    'email_from':self.get_mail_server_name(),
                }).send()

class versionWizard(models.TransientModel):
    _name = 'dtdream_rd_version.wizard'
    reason = fields.Char()

    def get_base_url(self,cr,uid):
        base_url = self.pool.get('ir.config_parameter').get_param(cr, uid, 'web.base.url')
        return base_url

    def get_mail_server_name(self):
        return self.env['ir.mail_server'].search([], limit=1).smtp_user

    @api.one
    def btn_version_submit(self):
        current_version = self.env['dtdream_rd_version'].browse(self._context['active_id'])
        state = current_version.version_state
        current_version.current_approver_user = [(5,)]
        if state=='initialization':
            current_version.write({'is_click_01':True})
            process_01 = self.env['dtdream_rd_process_ver'].search([('process_01_id','=',current_version.id),('ver_state','=',state),('is_new','=',True)])
            if len(process_01)==0:
                records = self.env['dtdream_rd_approver_ver'].search([('ver_state','=',state),('level','=','level_01')])           #版本审批配置
                rold_ids = []
                for record in records:
                    rold_ids +=[record.name.id]
                appro = self.env['dtdream_rd_role'].search([('role_id','=',current_version.proName.id),('cof_id','in',rold_ids),('person','!=',False)]) #产品中角色配置
                if len(appro)==0:
                    ctd = self.env['dtdream_rd_approver_ver'].search([('department','=',current_version.proName.department.id)],limit=1)
                    if not current_version.proName.department.manager_id:
                        raise ValidationError(u"请配置%s的部门主管" %(current_version.proName.department.name))
                    self.env['dtdream_rd_process_ver'].create({"role":ctd.name.id, "process_01_id":current_version.id,'ver_state':state,'approver':current_version.proName.department.manager_id.id,'approver_old':current_version.proName.department.manager_id.id,'level':'level_02'})       #审批意见记录创建
                    self.current_approver_user = [(5,)]
                    self.write({'current_approver_user': [(4, current_version.proName.department.manager_id.user_id.id)]})
                    subject=current_version.proName.department.name+u"/"+current_version.proName.department_2.name+u"的"+current_version.proName.name+u"的"+current_version.version_numb+u"版本，待您审批"
                    appellation = current_version.proName.department.manager_id.name+u",您好"
                    content = current_version.proName.department.name+u"的"+current_version.proName.name+u"的"+current_version.version_numb+u"版本的草稿阶段待您审批"
                    base_url = self.get_base_url()
                    link = '/web#id=%s&view_type=form&model=dtdream_rd_version' % current_version.id
                    url = base_url+link
                    self.env['mail.mail'].create({
                        'body_html': u'''<p>%s</p>
                                     <p>%s</p>
                                     <p> 请点击链接进入:
                                     <a href="%s">%s</a></p>
                                    <p>dodo</p>
                                     <p>万千业务，简单有do</p>
                                     <p>%s</p>''' % (appellation,content, url,url,current_version.write_date[:10]),
                        'subject': '%s' % subject,
                        'email_to': '%s' % current_version.proName.department.manager_id.work_email,
                        'auto_delete': False,
                        'email_from':self.get_mail_server_name(),
                    }).send()
                else:
                    for record in appro:
                        self.env['dtdream_rd_process_ver'].create({"role":record.cof_id.id, "process_01_id":current_version.id,'ver_state':state,'approver':record.person.id,'approver_old':record.person.id,'level':'level_01'})       #审批意见记录创建
                        current_version.write({'current_approver_user': [(4, record.person.user_id.id)]})
                        subject=current_version.proName.department.name+u"/"+current_version.proName.department_2.name+u"的"+current_version.proName.name+u"的"+current_version.version_numb+u"版本，待您审批"
                        appellation = record.person.name+u",您好"
                        content = current_version.proName.department.name+u"的"+current_version.proName.name+u"的"+current_version.version_numb+u"版本的草稿阶段待您审批"
                        base_url = self.get_base_url()
                        link = '/web#id=%s&view_type=form&model=dtdream_rd_version' % current_version.id
                        url = base_url+link
                        self.env['mail.mail'].create({
                            'body_html': u'''<p>%s</p>
                                         <p>%s</p>
                                         <p> 请点击链接进入:
                                         <a href="%s">%s</a></p>
                                        <p>dodo</p>
                                         <p>万千业务，简单有do</p>
                                         <p>%s</p>''' % (appellation,content, url,url,current_version.write_date[:10]),
                            'subject': '%s' % subject,
                            'email_to': '%s' % record.person.work_email,
                            'auto_delete': False,
                            'email_from':self.get_mail_server_name(),
                        }).send()
        elif state=='Development':
            current_version.write({'is_click_02':True})
            process_02 = self.env['dtdream_rd_process_ver'].search([('process_02_id','=',current_version.id),('ver_state','=',state),('is_new','=',True)])
            if len(process_02)==0:
                records = self.env['dtdream_rd_approver_ver'].search([('ver_state','=',state),('level','=','level_01')])           #产品审批配置
                rold_ids = []
                for record in records:
                    rold_ids +=[record.name.id]
                appro = self.env['dtdream_rd_role'].search([('role_id','=',current_version.proName.id),('cof_id','in',rold_ids),('person','!=',False)]) #产品中角色配置
                if len(appro)==0:
                    ctd = self.env['dtdream_rd_approver_ver'].search([('department','=',current_version.proName.department.id)],limit=1)
                    if not current_version.proName.department.manager_id:
                        raise ValidationError(u"请配置%s的部门主管" %(current_version.proName.department.name))
                    self.env['dtdream_rd_process_ver'].create({"role":ctd.name.id, "process_02_id":current_version.id,'ver_state':state,'approver':current_version.proName.department.manager_id.id,'approver_old':current_version.proName.department.manager_id.id,'level':'level_02'})       #审批意见记录创建
                    self.current_approver_user = [(5,)]
                    self.write({'current_approver_user': [(4, current_version.proName.department.manager_id.user_id.id)]})
                    subject=current_version.proName.department.name+u"/"+current_version.proName.department_2.name+u"的"+current_version.proName.name+u"的"+current_version.version_numb+u"版本，待您审批"
                    appellation = current_version.proName.department.manager_id.name+u",您好"
                    content = current_version.proName.department.name+u"的"+current_version.proName.name+u"的"+current_version.version_numb+u"版本的开发中阶段待您审批"
                    base_url = self.get_base_url()
                    link = '/web#id=%s&view_type=form&model=dtdream_rd_version' % current_version.id
                    url = base_url+link
                    self.env['mail.mail'].create({
                        'body_html': u'''<p>%s</p>
                                     <p>%s</p>
                                     <p> 请点击链接进入:
                                     <a href="%s">%s</a></p>
                                    <p>dodo</p>
                                     <p>万千业务，简单有do</p>
                                     <p>%s</p>''' % (appellation,content, url,url,current_version.write_date[:10]),
                        'subject': '%s' % subject,
                        'email_to': '%s' % current_version.proName.department.manager_id.work_email,
                        'auto_delete': False,
                        'email_from':self.get_mail_server_name(),
                    }).send()
                else:
                    for record in appro:
                        self.env['dtdream_rd_process_ver'].create({"role":record.cof_id.id, "process_02_id":current_version.id,'ver_state':state,'approver':record.person.id,'approver_old':record.person.id,'level':'level_01'})       #审批意见记录创建
                        current_version.write({'current_approver_user': [(4, record.person.user_id.id)]})
                        subject=current_version.proName.department.name+u"/"+current_version.proName.department_2.name+u"的"+current_version.proName.name+u"的"+current_version.version_numb+u"版本，待您审批"
                        appellation = record.person.name+u",您好"
                        content = current_version.proName.department.name+u"的"+current_version.proName.name+u"的"+current_version.version_numb+u"版本的开发中阶段待您审批"
                        base_url = self.get_base_url()
                        link = '/web#id=%s&view_type=form&model=dtdream_rd_version' % current_version.id
                        url = base_url+link
                        self.env['mail.mail'].create({
                            'body_html': u'''<p>%s</p>
                                         <p>%s</p>
                                         <p> 请点击链接进入:
                                         <a href="%s">%s</a></p>
                                        <p>dodo</p>
                                         <p>万千业务，简单有do</p>
                                         <p>%s</p>''' % (appellation,content, url,url,current_version.write_date[:10]),
                            'subject': '%s' % subject,
                            'email_to': '%s' % record.person.work_email,
                            'auto_delete': False,
                            'email_from':self.get_mail_server_name(),
                        }).send()
        elif state=='pending':
            current_version.write({'is_click_03':True})
            process_03 = self.env['dtdream_rd_process_ver'].search([('process_03_id','=',current_version.id),('ver_state','=',state),('is_new','=',True)])
            if len(process_03)==0:
                records = self.env['dtdream_rd_approver_ver'].search([('ver_state','=',state),('level','=','level_01')])           #产品审批配置
                rold_ids = []
                for record in records:
                    rold_ids +=[record.name.id]
                appro = self.env['dtdream_rd_role'].search([('role_id','=',current_version.proName.id),('cof_id','in',rold_ids),('person','!=',False)]) #产品中角色配置
                if len(appro)==0:
                    if not current_version.proName.department.manager_id:
                        raise ValidationError(u"请配置%s的部门主管" %(current_version.proName.department.name))
                    ctd = self.env['dtdream_rd_approver_ver'].search([('department','=',current_version.proName.department.id)],limit=1)
                    self.env['dtdream_rd_process_ver'].create({"role":ctd.name.id, "process_03_id":current_version.id,'ver_state':state,'approver':current_version.proName.department.manager_id.id,'approver_old':current_version.proName.department.manager_id.id,'level':'level_02'})       #审批意见记录创建
                    current_version.write({'current_approver_user': [(4, current_version.proName.department.manager_id.user_id.id)]})

                    subject=current_version.proName.department.name+u"/"+current_version.proName.department_2.name+u"的"+current_version.proName.name+u"的"+current_version.version_numb+u"版本，待您审批"
                    appellation = current_version.proName.department.manager_id.name+u",您好"
                    content = current_version.proName.department.name+u"的"+current_version.proName.name+u"的"+current_version.version_numb+u"版本的带发布阶段待您审批"
                    base_url = self.get_base_url()
                    link = '/web#id=%s&view_type=form&model=dtdream_rd_version' % current_version.id
                    url = base_url+link
                    self.env['mail.mail'].create({
                        'body_html': u'''<p>%s</p>
                                     <p>%s</p>
                                     <p> 请点击链接进入:
                                     <a href="%s">%s</a></p>
                                    <p>dodo</p>
                                     <p>万千业务，简单有do</p>
                                     <p>%s</p>''' % (appellation,content, url,url,current_version.write_date[:10]),
                        'subject': '%s' % subject,
                        'email_to': '%s' % current_version.proName.department.manager_id.work_email,
                        'auto_delete': False,
                        'email_from':self.get_mail_server_name(),
                    }).send()
                else:
                    for record in appro:
                        self.env['dtdream_rd_process_ver'].create({"role":record.cof_id.id, "process_03_id":current_version.id,'ver_state':state,'approver':record.person.id,'approver_old':record.person.id,'level':'level_01'})       #审批意见记录创建
                        current_version.write({'current_approver_user': [(4, record.person.user_id.id)]})

                        subject=current_version.proName.department.name+u"/"+current_version.proName.department_2.name+u"的"+current_version.proName.name+u"的"+current_version.version_numb+u"版本，待您审批"
                        appellation = current_version.proName.department.manager_id.name+u",您好"
                        content = current_version.proName.department.name+u"的"+current_version.proName.name+u"的"+current_version.version_numb+u"版本的待发布阶段待您审批"
                        base_url = self.get_base_url()
                        link = '/web#id=%s&view_type=form&model=dtdream_rd_version' % current_version.id
                        url = base_url+link
                        self.env['mail.mail'].create({
                            'body_html': u'''<p>%s</p>
                                         <p>%s</p>
                                         <p> 请点击链接进入:
                                         <a href="%s">%s</a></p>
                                        <p>dodo</p>
                                         <p>万千业务，简单有do</p>
                                         <p>%s</p>''' % (appellation,content, url,url,current_version.write_date[:10]),
                            'subject': '%s' % subject,
                            'email_to': '%s' % current_version.proName.department.manager_id.work_email,
                            'auto_delete': False,
                            'email_from':self.get_mail_server_name(),
                        }).send()

