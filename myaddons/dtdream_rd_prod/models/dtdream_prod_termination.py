# -*- coding: utf-8 -*-
from openerp import models, fields, api
from openerp.exceptions import ValidationError
from lxml import etree
from datetime import datetime,timedelta


class dtdream_prod_termination(models.Model):
    _name = "dtdream.prod.termination"
    _inherit =['mail.thread']
    _description = u"中止"

    def compute_get_name(self):
        version=''
        if self.version:
            version=u'/'+self.version.version_numb+u'/'

        self.name=self.project.name+version+u'的中止'

    name = fields.Char(compute=compute_get_name)
    project = fields.Many2one("dtdream_prod_appr" ,required=True,string="产品名称")
    version = fields.Many2one("dtdream_rd_version",string="版本")
    reason = fields.Text(string="中止原因",track_visibility='onchange')
    state= fields.Selection([('cg','草稿'),('spz','审批中'),('ysp','已审批')],string="状态",default='cg')
    appr_PL_CCB = fields.Many2one("hr.employee", string="审批人PL-CCB")

    @api.depends("current_approver_user")
    def _depends_user(self):
        for rec in self:
            if rec.current_approver_user:
                em = self.env['hr.employee'].search([('user_id','=',rec.current_approver_user.id)])
                rec.current_approver=em.id
            else:
                rec.current_approver=False
    current_approver = fields.Many2one("hr.employee",compute="_depends_user",string="当前经办人")
    current_approver_user = fields.Many2one("res.users",string="当前经办人用户")
    role_person = fields.Many2many("res.users" ,"dtdream_termination_role_user",string="对应产品角色中的人员用户")
    his_app_user = fields.Many2many("res.users" ,"dtdream_termination_his_user",string="历史审批人用户")

    @api.onchange('message_follower_ids')
    @api.constrains('message_follower_ids')
    def _compute_follower(self):
        self.followers_user = False
        followers_user = [(4, foll.partner_id.user_ids.id) for foll in self.message_follower_ids]
        self.write({'followers_user': followers_user})
        for foll in self.message_follower_ids:
            if foll.partner_id.user_ids not in self.env.ref("dtdream_rd_prod.group_dtdream_rd_user_all").users and  foll.partner_id.user_ids not in self.env.ref("dtdream_rd_prod.group_dtdream_rd_qa").users:
                self.env.ref("dtdream_rd_prod.group_dtdream_rd_user_all").sudo().write({'users': [(4,foll.partner_id.user_ids.id)]})

    followers_user = fields.Many2many("res.users" ,"termination_f_u_u",string="关注者")

    @api.constrains('project')
    def con_name_role(self):
        self.role_person=[(5,)]
        roles = [(4, role.person.user_id.id) for role in self.project.role_ids if
                 role.person.id and role.person.user_id.id]
        self.write({'role_person': roles})
        roles = [role.person.user_id.id for role in self.project.role_ids if
                 role.person.id and role.person.user_id.id]
        self.message_subscribe_users(user_ids=roles)


    @api.multi
    def _compute_is_shenpiren(self):
        for rec in self:
            if self.env.user in rec.current_approver_user:
                rec.is_shenpiren=True
            else:
                rec.is_shenpiren = False
    is_shenpiren = fields.Boolean(string="是否审批人",compute=_compute_is_shenpiren,readonly=True)

    @api.multi
    def _compute_create(self):
        for rec in self:
            if rec.create_uid==self.env.user:
                rec.is_create=True
            else:
                rec.is_create=False
    is_create = fields.Boolean(string="是否创建者",compute=_compute_create,default=True)

    @api.multi
    def _compute_is_qa(self):
        users =  self.env.ref("dtdream_rd_prod.group_dtdream_rd_qa").users
        for rec in self:
            if self.env.user in users:
                rec.is_Qa = True
            else:
                rec.is_Qa=False
    is_Qa = fields.Boolean(string="是否在QA组",compute=_compute_is_qa,readonly=True)


    def _send_email(self,project,version,plccb):
        department_2 = project.department_2.name or ''
        version_numb = version.version_numb or ''
        subject=''
        if department_2:
            subject=project.department.name+u"/"+department_2+u"的"+project.name+u"待您的审批"
        else:
            subject=project.department.name+u"的"+project.name+u"待您的审批"
        appellation = plccb.name+u",您好"
        content = project.department.name+u"的"+project.name+u"的"+version_numb+u"中止申请，待您审批"
        base_url = project.get_base_url()
        link = '/web#id=%s&view_type=form&model=dtdream.prod.termination' % self.id
        url = base_url+link
        self.env['mail.mail'].create({
            'body_html': u'''<p>%s</p>
                         <p>%s</p>
                         <p> 请点击链接进入:
                         <a href="%s">%s</a></p>
                        <p>dodo</p>
                         <p>万千业务，简单有do</p>
                         <p>%s</p>''' % (appellation,content, url,url,self.write_date[:10]),
            'subject': '%s' % subject,
            'email_to': '%s' % plccb.work_email,
            'auto_delete': False,
            'email_from':project.get_mail_server_name(),
        }).send()


    @api.multi
    def terminationtj(self):
        if self.reason:
            is_plccb = False
            plccb=None
            for role in self.project.role_ids:
                if role.cof_id.name=="PL-CCB":
                    is_plccb=True
                    plccb=role.person
                    break
            if not is_plccb or not plccb:
                raise ValidationError(u"该产品没有配置PL-CCB")
            project = self.project
            self.write({'state':'spz'})
            if not self.version:                                           #产品
                project.write({'is_zanting_backtjN':True})
                self._send_email(plccb=plccb,project=project,version=self.version)
                self.write({'current_approver_user': plccb.user_id.id})
                self.message_post(body=u"""<table class="zxtable" border="1" style="border-collapse: collapse;">
                                           <tr><th style="padding:10px">产品名称</th><th style="padding:10px">%s</th></tr>
                                           <tr><td style="padding:10px">操作</td><td style="padding:10px">%s</td></tr>
                                           <tr><td style="padding:10px">申请原因</td><td style="padding:10px">%s</td></tr>
                                           </table>""" %(project.name,u'提交中止',self.reason))
                project.message_post(body=u"""<table class="zxtable" border="1" style="border-collapse: collapse;">
                                                           <tr><th style="padding:10px">产品名称</th><th style="padding:10px">%s</th></tr>
                                                           <tr><td style="padding:10px">操作</td><td style="padding:10px">%s</td></tr>
                                                           <tr><td style="padding:10px">申请原因</td><td style="padding:10px">%s</td></tr>
                                                           </table>""" % (project.name, u'提交中止', self.reason))
            else:
                version = self.version
                version.write({'is_zanting_backtjN':True})
                self._send_email(plccb=plccb,project=project,version=version)
                self.write({'current_approver_user': plccb.user_id.id})
                self.message_post(body=u"""<table class="zxtable" border="1" style="border-collapse: collapse;">
                                           <tr><th style="padding:10px">产品名称</th><th style="padding:10px">%s</th></tr>
                                           <tr><th style="padding:10px">版本号</th><th style="padding:10px">%s</th></tr>
                                           <tr><td style="padding:10px">操作</td><td style="padding:10px">%s</td></tr>
                                           <tr><td style="padding:10px">申请原因</td><td style="padding:10px">%s</td></tr>
                                           </table>""" %(project.name,version.version_numb,u'提交中止',self.reason))
                version.message_post(body=u"""<table class="zxtable" border="1" style="border-collapse: collapse;">
                                                           <tr><th style="padding:10px">产品名称</th><th style="padding:10px">%s</th></tr>
                                                           <tr><th style="padding:10px">版本号</th><th style="padding:10px">%s</th></tr>
                                                           <tr><td style="padding:10px">操作</td><td style="padding:10px">%s</td></tr>
                                                           <tr><td style="padding:10px">申请原因</td><td style="padding:10px">%s</td></tr>
                                                           </table>""" % (project.name, version.version_numb, u'提交中止', self.reason))
        else:
            raise ValidationError('申请原因未填写')


    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        params = self._context.get('params', None)
        action = params.get("action", 0) if params else 0
        my_action = self.env["ir.actions.act_window"].search([('id', '=', action)])
        res = super(dtdream_prod_termination, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=False)
        doc = etree.XML(res['arch'])
        if res['type'] == "form":
            doc.xpath("//form")[0].set("create", "false")
        if res['type'] == "tree":
            doc.xpath("//tree")[0].set("create", "false")
        if res['type'] == "kanban":
            doc.xpath("//kanban")[0].set("create", "false")
        res['arch'] = etree.tostring(doc)
        return res

    def _get_parent_id(self,menu=None):
        if len(menu.parent_id)>0:
            return self._get_parent_id(menu.parent_id)
        else:
            return menu.id

    @api.model
    def get_apply(self):
        applies=[]
        state_list = [('cg', '草稿'), ('spz', '审批中'), ('ysp', '已审批')]
        state_dict = dict(state_list)
        appr = self.env['dtdream.prod.termination'].search([('create_uid','=',self.env.user.id),('state','!=','ysp')])
        menu_id = self._get_menu_id()
        for app in appr:
            department = ''
            if app.project.department_2:
                department = app.project.department.name + '/' + app.project.department_2.name
            else:
                department = app.project.department.name
            deferdays = (datetime.now() - datetime.strptime(app.write_date, '%Y-%m-%d %H:%M:%S') + timedelta(hours=8)).days
            if deferdays == 0:
                defer = False
            else:
                defer = True
            apply={
                'department':department,
                'appr': app.project.name,
                'version':app.version.version_numb or '',
                'PDT': app.project.PDT.name or '',
                'YF_manager': app.project.YF_manager.name or '',
                'style':u'中止',
                'state': state_dict[app.state],
                'defer':defer,
                'url': '/web#id=' + str(app.id) + '&view_type=form&model=' + app._name + '&menu_id=' + str(menu_id),
                'deferdays': deferdays
            }
            applies.append(apply)
        return applies

    # 待我审批流程
    @api.model
    def get_affair(self):
        affairs = []
        state_list = [('cg', '草稿'), ('spz', '审批中'), ('ysp', '已审批')]
        state_dict = dict(state_list)
        appr = self.env['dtdream.prod.termination'].search([('current_approver_user', '=', self.env.user.id)])
        menu_id = self._get_menu_id()
        for app in appr:
            department = ''
            if app.project.department_2:
                department = app.project.department.name + '/' + app.project.department_2.name
            else:
                department = app.project.department.name
            deferdays = (datetime.now() - datetime.strptime(app.write_date, '%Y-%m-%d %H:%M:%S') + timedelta(hours=8)).days
            if deferdays == 0:
                defer = False
            else:
                defer = True
            apply = {
                'department':department,
                'appr': app.project.name,
                'version': app.version.version_numb or '',
                'PDT': app.project.PDT.name or '',
                'YF_manager': app.project.YF_manager.name or '',
                'style': u'中止',
                'state': state_dict[app.state],
                'defer': defer,
                'url': '/web#id=' + str(app.id) + '&view_type=form&model=' + app._name + '&menu_id=' + str(menu_id),
                'deferdays': deferdays
            }
            affairs.append(apply)
        return affairs

    @api.model
    def get_done(self):
        affairs = []
        state_list = [('cg', '草稿'), ('spz', '审批中'), ('ysp', '已审批')]
        state_dict = dict(state_list)
        appr = self.env['dtdream.prod.termination'].search([('his_app_user', '=', self.env.user.id)])
        menu_id = self._get_menu_id()
        for app in appr:
            department = ''
            if app.project.department_2:
                department = app.project.department.name + '/' + app.project.department_2.name
            else:
                department = app.project.department.name
            deferdays = (datetime.now() - datetime.strptime(app.write_date, '%Y-%m-%d %H:%M:%S') + timedelta(hours=8)).days
            if deferdays == 0:
                defer = False
            else:
                defer = True
            apply = {
                'department':department,
                'appr': app.project.name,
                'version': app.version.version_numb or '',
                'PDT': app.project.PDT.name or '',
                'YF_manager': app.project.YF_manager.name or '',
                'style': u'中止',
                'state': state_dict[app.state],
                'defer': defer,
                'url': '/web#id=' + str(app.id) + '&view_type=form&model=' + app._name + '&menu_id=' + str(menu_id),
                'deferdays': deferdays
            }
            affairs.append(apply)
        return affairs

    def _get_menu_id(self):
        act_windows = self.env['ir.actions.act_window'].sudo().search([('res_model', '=', 'dtdream.prod.termination')])
        menu = None
        for act_window in act_windows:
            action_id = 'ir.actions.act_window,' + str(act_window.id)
            menu = self.env['ir.ui.menu'].sudo().search([('action', '=', action_id)])
            if len(menu)>0:
                break
        menu_id = self._get_parent_id(menu)
        return menu_id


class dtdream_prod_termination_w(models.TransientModel):
    _name = "dtdream.prod.termination.w"
    _inherit =['mail.thread']
    _description = u"中止"

    def compute_get_name(self):
        version=''
        if self.version:
            version=u'/'+self.version.version_numb+u'/'

        self.name=self.project.name+version+u'的中止'

    name = fields.Char(compute=compute_get_name)
    project = fields.Many2one("dtdream_prod_appr" ,required=True,string="产品名称")
    version = fields.Many2one("dtdream_rd_version",string="版本")
    reason = fields.Text(string="原因",track_visibility='onchange')
    state= fields.Selection([('cg','草稿'),('spz','审批中'),('ysp','已审批')],string="状态",default='cg')
    appr_PL_CCB = fields.Many2one("hr.employee", string="审批人PL-CCB")

    @api.multi
    def terminationtj(self):
        if self.reason:
            is_plccb = False
            plccb = None
            for role in self.project.role_ids:
                if role.cof_id.name == "PL-CCB":
                    is_plccb = True
                    plccb = role.person
                    break
            if not is_plccb or not plccb:
                raise ValidationError(u"该产品没有配置PL-CCB")
            termination = self.env['dtdream.prod.termination'].create({'project': self.project.id, 'version': self.version.id, 'reason': self.reason, 'state': self.state})
            project = termination.project
            termination.write({'state': 'spz'})
            if not termination.version:  # 产品
                project.write({'is_zanting_backtjN': True})
                termination._send_email(plccb=plccb, project=project, version=self.version)
                termination.write({'current_approver_user': plccb.user_id.id})
                termination.message_post(body=u"""<table class="zxtable" border="1" style="border-collapse: collapse;">
                                               <tr><th style="padding:10px">产品名称</th><th style="padding:10px">%s</th></tr>
                                               <tr><td style="padding:10px">操作</td><td style="padding:10px">%s</td></tr>
                                               <tr><td style="padding:10px">申请原因</td><td style="padding:10px">%s</td></tr>
                                               </table>""" % (project.name, u'提交中止', termination.reason))
                project.message_post(body=u"""<table class="zxtable" border="1" style="border-collapse: collapse;">
                                                               <tr><th style="padding:10px">产品名称</th><th style="padding:10px">%s</th></tr>
                                                               <tr><td style="padding:10px">操作</td><td style="padding:10px">%s</td></tr>
                                                               <tr><td style="padding:10px">申请原因</td><td style="padding:10px">%s</td></tr>
                                                               </table>""" % (project.name, u'提交中止', termination.reason))
            else:
                version = termination.version
                version.write({'is_zanting_backtjN': True})
                termination._send_email(plccb=plccb, project=project, version=version)
                termination.write({'current_approver_user': plccb.user_id.id})
                termination.message_post(body=u"""<table class="zxtable" border="1" style="border-collapse: collapse;">
                                               <tr><th style="padding:10px">产品名称</th><th style="padding:10px">%s</th></tr>
                                               <tr><th style="padding:10px">版本号</th><th style="padding:10px">%s</th></tr>
                                               <tr><td style="padding:10px">操作</td><td style="padding:10px">%s</td></tr>
                                               <tr><td style="padding:10px">申请原因</td><td style="padding:10px">%s</td></tr>
                                               </table>""" % (project.name, version.version_numb, u'提交中止', termination.reason))
                version.message_post(body=u"""<table class="zxtable" border="1" style="border-collapse: collapse;">
                                                               <tr><th style="padding:10px">产品名称</th><th style="padding:10px">%s</th></tr>
                                                               <tr><th style="padding:10px">版本号</th><th style="padding:10px">%s</th></tr>
                                                               <tr><td style="padding:10px">操作</td><td style="padding:10px">%s</td></tr>
                                                               <tr><td style="padding:10px">申请原因</td><td style="padding:10px">%s</td></tr>
                                                               </table>""" % (
                project.name, version.version_numb, u'提交中止', termination.reason))
        else:
            raise ValidationError('申请原因未填写')