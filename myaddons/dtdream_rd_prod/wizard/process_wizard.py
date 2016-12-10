# -*- coding: utf-8 -*-
from openerp import models, fields, api
from openerp.exceptions import ValidationError
from datetime import datetime


#产品审批
class process_wizard(models.TransientModel):
    _name = 'dtdream.process.wizard'
    name = fields.Char("审批阶段")
    reason = fields.Char("意见")


    def get_base_url(self,cr,uid):
        base_url = self.pool.get('ir.config_parameter').get_param(cr, uid, 'web.base.url')
        return base_url

    def get_mail_server_name(self):
        return self.env['ir.mail_server'].sudo().search([], limit=1).smtp_user

    #邮件通知
    def send_next_shenpi_mail(self,current_product,next_shenpi,state_display):
        department_2=u'的'
        if current_product.department_2:
            department_2 = u"/"+current_product.department_2.name+u"的"

        subject=current_product.department.name+department_2+current_product.name+u"待您审批"
        appellation = next_shenpi.name+u",您好"
        content = current_product.department.name+u"的"+current_product.name+u"已进入"+state_display+u"，等待您的审批"
        base_url = self.get_base_url()
        link = '/web#id=%s&view_type=form&model=dtdream_prod_appr' % current_product.id
        url = base_url+link
        self.env['mail.mail'].create({
            'body_html': u'''<p>%s</p>
                         <p>%s</p>
                         <p> 请点击链接进入:
                         <a href="%s">%s</a></p>
                        <p>dodo</p>
                         <p>万千业务，简单有do</p>
                         <p>%s</p>''' % (appellation,content, url,url,current_product.write_date[:10]),
            'subject': '%s' % subject,
            'email_to': '%s' % next_shenpi.work_email,
            'auto_delete': False,
            'email_from':self.get_mail_server_name(),
        }).send()

    #下方备注
    def _message_post(self,current_product,current_process,state,level,result,reason):
        reason= reason or u'无'
        current_product.message_post(body=u"""<table class="zxtable" border="1" style="border-collapse: collapse;">
                                   <tr><th style="padding:10px">产品名称</th><th style="padding:10px">%s</th></tr>
                                   <tr><td style="padding:10px">审批人</td><td style="padding:10px">%s</td></tr>
                                   <tr><td style="padding:10px">内容</td><td style="padding:10px">%s</td></tr>
                                   </table>""" %(current_product.name,current_process.approver.name,u'在'+state+level+u'审批意见:'+result+u',原因：'+reason))

    #立项阶段
    def check_process_ids(self, current_process,current_product,flag):
        reason = current_process.reason or u'无'
        current_product.write({'his_app_user': [(4, current_process.approver.user_id.id)]})
        if current_process.level=='level_01':
            current_product.is_finsished_01 = True
            self._message_post(current_product=current_product,current_process=current_process,state=u'立项阶段',level=u'一级',result=flag,reason=reason)
            processes = self.env['dtdream_rd_process'].search([('process_id','=',current_product.id),('pro_state','=',current_product.state),('is_new','=',True),('level','=','level_01')])
            for process in processes:
                if not (process.is_pass or process.is_risk):
                    current_product.is_finsished_01 = False
                    break
            if current_product.is_finsished_01:
                records = self.env['dtdream_rd_approver'].search([('pro_state','=',current_product.state),('level','=','level_02')])           #审批人配置
                rold_ids = []
                for record in records:
                    rold_ids +=[record.name.id]
                appro = self.env['dtdream_rd_role'].search([('role_id','=',current_product.id),('cof_id','in',rold_ids),('person','!=',False)]) #产品中角色配置
                current_product.current_approver_user = [(5,)]
                if len(appro)==0:
                    current_product.signal_workflow('btn_to_ztsj')
                    current_product.write({'is_lixiangappred':False})
                else:
                    for record in appro:
                        self.env['dtdream_rd_process'].create({"role":record.cof_id.id, "process_id":current_product.id,'pro_state':current_product.state,'approver':record.person.id,'approver_old':record.person.id,'level':'level_02'})       #审批意见记录创建
                        current_product.write({'current_approver_user': [(4, record.person.user_id.id)]})
                        self.send_next_shenpi_mail(current_product=current_product,next_shenpi=record.person,state_display=u'立项阶段')

        elif current_process.level=='level_02':
            current_product.signal_workflow('btn_to_ztsj')
            current_product.write({'is_lixiangappred':False})
            self._message_post(current_product=current_product,current_process=current_process,state=u'立项阶段',level=u'二级',result=flag,reason=reason)

    #总体设计阶段
    def check_ztsj_process_ids(self, current_process,current_product,flag):
        current_product.is_finsished_02 = True
        reason = current_process.reason or u'无'
        current_product.write({'his_app_user': [(4, current_process.approver.user_id.id)]})
        if current_process.level=='level_01':
            self._message_post(current_product=current_product,current_process=current_process,state=u'总体设计阶段',level=u'一级',result=flag,reason=reason)
            processes = self.env['dtdream_rd_process'].search([('ztsj_process_id','=',current_product.id),('pro_state','=',current_product.state),('is_new','=',True),('level','=','level_01')])
            for process in processes:
                if not (process.is_pass or process.is_risk):
                    current_product.is_finsished_02 = False
                    break
            if current_product.is_finsished_02:
                records = self.env['dtdream_rd_approver'].search([('pro_state','=',current_product.state),('level','=','level_02')])           #审批人配置
                rold_ids = []
                for record in records:
                    rold_ids +=[record.name.id]
                appro = self.env['dtdream_rd_role'].search([('role_id','=',current_product.id),('cof_id','in',rold_ids),('person','!=',False)]) #产品中角色配置
                current_product.current_approver_user = [(5,)]
                if len(appro)==0:
                    current_product.signal_workflow('btn_to_ddkf')
                    current_product.write({'overall_actual_time':datetime.now()})
                    current_product.write({'is_appred':False})
                else:
                    for record in appro:
                        self.env['dtdream_rd_process'].create({"role":record.cof_id.id, "ztsj_process_id":current_product.id,'pro_state':current_product.state,'approver':record.person.id,'approver_old':record.person.id,'level':'level_02'})       #审批意见记录创建
                        current_product.write({'current_approver_user': [(4, record.person.user_id.id)]})
                        self.send_next_shenpi_mail(current_product=current_product,next_shenpi=record.person,state_display=u'总体设计阶段')
        elif current_process.level=='level_02':
            current_product.signal_workflow('btn_to_ddkf')
            current_product.write({'overall_actual_time':datetime.now()})
            current_product.write({'is_appred':False})
            self._message_post(current_product=current_product,current_process=current_process,state=u'总体设计阶段',level=u'二级',result=flag,reason=reason)

    #通过
    @api.multi
    def btn_agree(self):
        active_id = self._context['active_id']
        current_process = self.env['dtdream_rd_process'].browse(active_id)
        current_process.write({"is_pass":True,'is_risk':False,'is_refuse':False,"reason":self.reason})
        current_product = current_process.process_id or current_process.ztsj_process_id
        if current_process.pro_state=='state_01' and current_process.pro_state==current_product.state:
            self.check_process_ids(current_process=current_process,current_product=current_product,flag=u'通过')
        elif current_process.pro_state=='state_02' and current_process.pro_state==current_product.state:
            self.check_ztsj_process_ids(current_process=current_process,current_product=current_product,flag=u'通过')

        return {
                'type': 'ir.actions.client',
                'tag': 'reload',
            }

    #带风险通过
    @api.multi
    def btn_other(self):
        active_id = self._context['active_id']
        current_process = self.env['dtdream_rd_process'].browse(active_id)
        current_process.write({"is_pass":False,'is_risk':True,'is_refuse':False,"reason":self.reason})
        current_product = current_process.process_id or current_process.ztsj_process_id
        if current_process.pro_state=='state_01' and current_process.pro_state==current_product.state:
            self.check_process_ids(current_process=current_process,current_product=current_product,flag=u'带风险通过')
        elif current_process.pro_state=='state_02' and current_process.pro_state==current_product.state:
            self.check_ztsj_process_ids(current_process=current_process,current_product=current_product,flag=u'带风险通过')

        return {
                'type': 'ir.actions.client',
                'tag': 'reload',
            }


    #不通过
    @api.multi
    def btn_reject(self):
        active_id = self._context['active_id']
        current_process = self.env['dtdream_rd_process'].browse(active_id)
        if not self.reason:
            raise ValidationError(u'不通过时意见必填')
        current_process.write({"is_pass":False,'is_risk':False,'is_refuse':True,"reason":self.reason})
        current_product = current_process.process_id or current_process.ztsj_process_id
        current_product.write({'his_app_user': [(4, current_process.approver.user_id.id)]})
        if current_process.pro_state=='state_01' and current_process.pro_state==current_product.state:
            if current_process.level=='level_01':
                self._message_post(current_product=current_product,current_process=current_process,state=u'立项阶段',level=u'一级',result=u'不通过',reason=self.reason)
            elif current_process.level=='level_02':
                self._message_post(current_product=current_product,current_process=current_process,state=u'立项阶段',level=u'二级',result=u'不通过',reason=self.reason)
                current_product.write({'is_lixiangappred':False,'is_appred':False,'is_finsished_01':False})
                processes = self.env['dtdream_rd_process'].search([('process_id','=',current_product.id)])
                processes.unlink()
        elif current_process.pro_state=='state_02' and current_process.pro_state==current_product.state:
            if current_process.level=='level_01':
                self._message_post(current_product=current_product,current_process=current_process,state=u'总体设计阶段',level=u'一级',result=u'不通过',reason=self.reason)
            elif current_process.level=='level_02':
                self._message_post(current_product=current_product,current_process=current_process,state=u'总体设计阶段',level=u'二级',result=u'不通过',reason=self.reason)
                current_product.write({'is_appred':False,'is_finsished_02':False})
                ztsj_processes = self.env['dtdream_rd_process'].search([('ztsj_process_id','=',current_product.id)])
                ztsj_processes.unlink()
        return {
                'type': 'ir.actions.client',
                'tag': 'reload',
            }

#版本审批
class ver_process_wizard(models.TransientModel):
    _name = 'dtdream.ver.process.wizard'
    name = fields.Char("审批阶段")
    reason = fields.Char("意见")


    def get_base_url(self,cr,uid):
        base_url = self.pool.get('ir.config_parameter').get_param(cr, uid, 'web.base.url')
        return base_url

    def get_mail_server_name(self):
        return self.env['ir.mail_server'].sudo().search([], limit=1).smtp_user

    #邮件通知
    def send_next_shenpi_mail(self,current_product,current_version,next_shenpi,state_display):
        department_2=u'的'
        if current_product.department_2:
            department_2 = u"/"+current_product.department_2.name+u"的"

        subject=current_product.department.name+department_2+current_product.name+u"的"+current_version.version_numb+u"版本，待您审批"
        appellation = next_shenpi.name+u",您好"
        content = current_product.department.name+u"的"+current_product.name+u"的"+current_version.version_numb+u"版本已进入待"+state_display+u"阶段，等待您的审批"
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
            'email_to': '%s' % next_shenpi.work_email,
            'auto_delete': False,
            'email_from':self.get_mail_server_name(),
        }).send()

    #下方备注
    def _message_post(self,current_product,current_version,current_process,state,level,result,reason):
        reason= reason or u'无'
        current_version.message_post(body=u"""<table class="zxtable" border="1" style="border-collapse: collapse;">
                                   <tr><th style="padding:10px">产品名称</th><th style="padding:10px">%s</th></tr>
                                   <tr><th style="padding:10px">版本号</th><th style="padding:10px">%s</th></tr>
                                   <tr><td style="padding:10px">审批人</td><td style="padding:10px">%s</td></tr>
                                   <tr><td style="padding:10px">内容</td><td style="padding:10px">%s</td></tr>
                                   </table>""" %(current_product.name,current_version.version_numb,current_process.approver.name,u'在'+state+level+u'审批意见:'+result+u',原因：'+reason))

    #计划中
    def check_process_id_01(self,current_product,current_version,current_process,flag):
        reason = current_process.reason or u'无'
        if current_process.level=='level_01':
            current_version.is_finish_01 = True
            self._message_post(current_product=current_product,current_version=current_version,current_process=current_process,state=u'计划中',level=u'一级',result=flag,reason=reason)
            processes = self.env['dtdream_rd_process_ver'].search([('process_01_id','=',current_version.id),('ver_state','=',current_version.version_state),('is_new','=',True),('level','=','level_01')])
            for process in processes:
                if not (process.is_pass or process.is_risk):
                    current_version.is_finish_01 = False
                    break
            if current_version.is_finish_01:
                if current_version.pro_flag=="flag_06":
                    records = self.env['dtdream_rd_approver_ver'].search([('ver_state','=',current_version.version_state),('level','=','level_02'),('is_formal','=',True)])           #版本审批配置
                else:
                    records = self.env['dtdream_rd_approver_ver'].search([('ver_state','=',current_version.version_state),('level','=','level_02'),('is_formal','=',False)])           #版本审批配置
                rold_ids = []
                for record in records:
                    rold_ids +=[record.name.id]
                appro = self.env['dtdream_rd_role'].search([('role_id','=',current_version.proName.id),('cof_id','in',rold_ids),('person','!=',False)]) #产品中角色配置
                current_version.current_approver_user = [(5,)]
                if len(appro)==0:
                    current_version.signal_workflow('btn_to_kaifa')
                    current_version.write({'is_click_01':False})
                else:
                    for record in appro:
                        current_version.add_follower(employee_id=record.person.id)
                        self.env['dtdream_rd_process_ver'].create({"role":record.cof_id.id, "process_01_id":current_version.id,'ver_state':current_version.version_state,'approver':record.person.id,'approver_old':record.person.id,'level':'level_02'})       #审批意见记录创建
                        current_version.write({'current_approver_user': [(4, record.person.user_id.id)]})
                        self.send_next_shenpi_mail(current_product=current_product,current_version=current_version,next_shenpi=record.person,state_display=u'计划中')
        elif current_process.level=='level_02':
            self._message_post(current_product=current_product,current_version=current_version,current_process=current_process,state=u'计划中',level=u'二级',result=flag,reason=reason)
            current_version.signal_workflow('btn_to_kaifa')
            current_version.write({'is_click_01':False})

    #开发中
    def check_process_id_02(self,current_product,current_version,current_process,flag):
        reason=current_process.reason or u'无'
        if current_process.level=='level_01':
            current_version.is_finish_02 = True
            self._message_post(current_product=current_product,current_version=current_version,current_process=current_process,state=u'开发中',level=u'一级',result=flag,reason=reason)
            processes = self.env['dtdream_rd_process_ver'].search([('process_02_id','=',current_version.id),('ver_state','=',current_version.version_state),('is_new','=',True),('level','=','level_01')])
            for process in processes:
                if not (process.is_pass or process.is_risk):
                    current_version.is_finish_02 = False
                    break
            if current_version.is_finish_02:
                if current_version.pro_flag=="flag_06":
                    records = self.env['dtdream_rd_approver_ver'].search([('ver_state','=',current_version.version_state),('level','=','level_02'),('is_formal','=',True)])           #版本审批配置
                else:
                    records = self.env['dtdream_rd_approver_ver'].search([('ver_state','=',current_version.version_state),('level','=','level_02'),('is_formal','=',False)])           #版本审批配置
                rold_ids = []
                for record in records:
                    rold_ids +=[record.name.id]
                appro = self.env['dtdream_rd_role'].search([('role_id','=',current_version.proName.id),('cof_id','in',rold_ids),('person','!=',False)]) #产品中角色配置
                current_version.current_approver_user = [(5,)]
                if len(appro)==0:
                    current_version.signal_workflow('btn_to_dfb')
                    current_version.write({'is_click_02':False})
                else:
                    for record in appro:
                        current_version.add_follower(employee_id=record.person.id)
                        self.env['dtdream_rd_process_ver'].create({"role":record.cof_id.id, "process_02_id":current_version.id,'ver_state':current_version.version_state,'approver':record.person.id,'approver_old':record.person.id,'level':'level_02'})       #审批意见记录创建
                        current_version.write({'current_approver_user': [(4, record.person.user_id.id)]})
                        self.send_next_shenpi_mail(current_product=current_product,current_version=current_version,next_shenpi=record.person,state_display=u'开发中')
        elif current_process.level=='level_02':
            self._message_post(current_product=current_product,current_version=current_version,current_process=current_process,state=u'开发中',level=u'二级',result=flag,reason=reason)
            current_version.signal_workflow('btn_to_dfb')
            current_version.write({'is_click_02':False})

    #待发布
    def check_process_id_03(self,current_product,current_version,current_process,flag):
        reason = current_process.reason or u'无'
        if current_process.level=='level_01':
            current_version.is_finish_03 = True
            self._message_post(current_product=current_product,current_version=current_version,current_process=current_process,state=u'待发布',level=u'一级',result=flag,reason=reason)
            processes = self.env['dtdream_rd_process_ver'].search([('process_03_id','=',current_version.id),('ver_state','=',current_version.version_state),('is_new','=',True),('level','=','level_01')])
            for process in processes:
                if not (process.is_pass or process.is_risk):
                    current_version.is_finish_03 = False
                    break
            if current_version.is_finish_03:
                if current_version.pro_flag=="flag_06":
                    records = self.env['dtdream_rd_approver_ver'].search([('ver_state','=',current_version.version_state),('level','=','level_02'),('is_formal','=',True)])           #版本审批配置
                else:
                    records = self.env['dtdream_rd_approver_ver'].search([('ver_state','=',current_version.version_state),('level','=','level_02'),('is_formal','=',False)])           #版本审批配置
                rold_ids = []
                for record in records:
                    rold_ids +=[record.name.id]
                appro = self.env['dtdream_rd_role'].search([('role_id','=',current_version.proName.id),('cof_id','in',rold_ids),('person','!=',False)]) #产品中角色配置
                current_version.current_approver_user = [(5,)]
                if len(appro)==0:
                    current_version.signal_workflow('btn_to_yfb')
                    current_version.write({'is_click_03':False})
                else:
                    for record in appro:
                        current_version.add_follower(employee_id=record.person.id)
                        self.env['dtdream_rd_process_ver'].create({"role":record.cof_id.id, "process_03_id":current_version.id,'ver_state':current_version.version_state,'approver':record.person.id,'approver_old':record.person.id,'level':'level_02'})       #审批意见记录创建
                        current_version.write({'current_approver_user': [(4, record.person.user_id.id)]})
                        self.send_next_shenpi_mail(current_product=current_product,current_version=current_version,next_shenpi=record.person,state_display=u'待发布')
        elif current_process.level=='level_02':
            self._message_post(current_product=current_product,current_version=current_version,current_process=current_process,state=u'待发布',level=u'二级',result=flag,reason=reason)
            current_version.signal_workflow('btn_to_yfb')
            current_version.write({'is_click_03':False})

    #通过
    @api.multi
    def btn_agree(self):
        active_id = self._context['active_id']
        current_process = self.env['dtdream_rd_process_ver'].browse(active_id)
        current_process.write({"is_pass":True,'is_risk':False,'is_refuse':False,"reason":self.reason})
        current_version=current_process.process_01_id or current_process.process_02_id or current_process.process_03_id
        current_version.write({'his_app_user': [(4, current_process.approver.user_id.id)]})
        current_product=current_version.proName

        if current_process.ver_state=='initialization' and current_process.ver_state==current_version.version_state:
            self.check_process_id_01(current_product=current_product,current_version=current_version,current_process=current_process,flag=u'通过')
        if current_process.ver_state=='Development' and current_process.ver_state==current_version.version_state:
            self.check_process_id_02(current_product=current_product,current_version=current_version,current_process=current_process,flag=u'通过')
        if current_process.ver_state=='pending' and current_process.ver_state==current_version.version_state:
            self.check_process_id_03(current_product=current_product,current_version=current_version,current_process=current_process,flag=u'通过')

        return {
                'type': 'ir.actions.client',
                'tag': 'reload',
            }

    #带风险通过
    @api.multi
    def btn_other(self):
        active_id = self._context['active_id']
        current_process = self.env['dtdream_rd_process_ver'].browse(active_id)
        current_process.write({"is_pass":False,'is_risk':True,'is_refuse':False,"reason":self.reason})
        current_version=current_process.process_01_id or current_process.process_02_id or current_process.process_03_id
        current_version.write({'his_app_user': [(4, current_process.approver.user_id.id)]})
        current_product=current_version.proName
        if current_process.ver_state=='initialization' and current_process.ver_state==current_version.version_state:
            self.check_process_id_01(current_product=current_product,current_version=current_version,current_process=current_process,flag=u'带风险通过')
        if current_process.ver_state=='Development' and current_process.ver_state==current_version.version_state:
            self.check_process_id_02(current_product=current_product,current_version=current_version,current_process=current_process,flag=u'带风险通过')
        if current_process.ver_state=='pending' and current_process.ver_state==current_version.version_state:
            self.check_process_id_03(current_product=current_product,current_version=current_version,current_process=current_process,flag=u'带风险通过')

        return {
                'type': 'ir.actions.client',
                'tag': 'reload',
            }

    #不通过
    @api.multi
    def btn_reject(self):
        active_id = self._context['active_id']
        current_process = self.env['dtdream_rd_process_ver'].browse(active_id)
        if not self.reason:
            raise ValidationError(u'不通过时意见必填')
        current_process.write({"is_pass":False,'is_risk':False,'is_refuse':True,"reason":self.reason})
        current_version=current_process.process_01_id or current_process.process_02_id or current_process.process_03_id
        current_version.write({'his_app_user': [(4, current_process.approver.user_id.id)]})
        current_product=current_version.proName
        if current_process.ver_state=='initialization' and current_process.ver_state==current_version.version_state:
            if current_process.level=='level_01':
                self._message_post(current_product=current_product,current_process=current_process,state=u'计划中',level=u'一级',result=u'不通过',reason=self.reason)
            elif current_process.level=='level_02':
                self._message_post(current_product=current_product,current_process=current_process,state=u'计划中',level=u'二级',result=u'不通过',reason=self.reason)
                proces_01all = self.env['dtdream_rd_process_ver'].search([('process_01_id','=',current_version.id),('ver_state','=',current_version.version_state)])
                proces_01all.unlink()
                current_version.write({'is_click_01':False,'is_finish_01':False})
        if current_process.ver_state=='Development' and current_process.ver_state==current_version.version_state:
            if current_process.level=='level_01':
                self._message_post(current_product=current_product,current_process=current_process,state=u'开发中',level=u'一级',result=u'不通过',reason=self.reason)
            elif current_process.level=='level_02':
                self._message_post(current_product=current_product,current_process=current_process,state=u'开发中',level=u'二级',result=u'不通过',reason=self.reason)
                proces_02all = self.env['dtdream_rd_process_ver'].search([('process_02_id','=',current_version.id),('ver_state','=',current_version.version_state)])
                proces_02all.unlink()
                current_version.write({'is_click_02':False,'is_finish_02':False})
        if current_process.ver_state=='pending' and current_process.ver_state==current_version.version_state:
            if current_process.level=='level_01':
                self._message_post(current_product=current_product,current_process=current_process,state=u'待发布',level=u'一级',result=u'不通过',reason=self.reason)
            elif current_process.level=='level_02':
                self._message_post(current_product=current_product,current_process=current_process,state=u'待发布',level=u'二级',result=u'不通过',reason=self.reason)
                proces_03all = self.env['dtdream_rd_process_ver'].search([('process_03_id','=',current_version.id),('ver_state','=',current_version.version_state)])
                proces_03all.unlink()
                current_version.write({'is_click_03':False,'is_finish_03':False})
        return {
                'type': 'ir.actions.client',
                'tag': 'reload',
            }