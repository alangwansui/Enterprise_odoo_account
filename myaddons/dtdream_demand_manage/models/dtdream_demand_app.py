# -*- coding: utf-8 -*-

from openerp import models, fields, api
from lxml import etree
from openerp.osv import expression


class dtdream_demand_app(models.Model):
    _name = 'dtdream.demand.app'
    _description = u'应用开发'
    _inherit = ['mail.thread']

    @api.depends('name')
    def _compute_department_belong(self):
        for rec in self:
            rec.department = rec.name.department_id

    def _compute_is_applicant(self):
        if self.env.user == self.name.user_id:
            self.is_applicant = True
        else:
            self.is_applicant = False

    def _compute_is_creator(self):
        if self.create_uid == self.env.user:
            self.is_creator = True
        else:
            self.is_creator = False

    def _compute_is_analyst(self):
        if self.analyst.user_id == self.env.user:
            self.is_analyst = True
        else:
            self.is_analyst = False

    def _compute_is_entrusted_analyst(self):
        if self.entrusted_analyst.user_id == self.env.user:
            self.is_entrusted_analyst = True
        else:
            self.is_entrusted_analyst = False

    def _compute_is_practice_man(self):
        if self.practice_man.user_id == self.env.user:
            self.is_practice_man = True
        else:
            self.is_practice_man = False

    def _compute_is_direct_manage(self):
        if self.name.department_id.manager_id.user_id == self.env.user:
            self.is_direct_manage = True
        else:
            self.is_direct_manage = False

    def _compute_is_it_manage(self):
        it = self.env['hr.department'].search([('name', '=', u'信息开发部'), ('parent_id.name', '=', u'综合开发部')], limit=1)
        if it.manager_id.user_id == self.env.user:
            self.is_IT_manage = True
        else:
            self.is_IT_manage = False

    def _compute_is_current(self):
        if self.current_approve.user_id == self.env.user:
            self.is_current = True
        else:
            self.is_current = False

    def _compute_login_is_manage(self):
        if self.env.ref("dtdream_demand_manage.dtdream_demand_manage") in self.env.user.groups_id:
            self.is_manage = True
        else:
            self.is_manage = False

    @api.multi
    def entrust_others_analysis(self):
        current_approve = self.entrusted_analyst
        approve = self.analyst
        self.conclude = False
        self.man_hours = 0
        self.priority = False
        self.write({'current_approve': current_approve.id, 'approves': [(4, approve.id)]})
        self.add_follower(user_id=approve.user_id)
        subject = u'【通知】%s委托您分析需求方案' % approve.name
        content = u'%s委托您分析方案,请您对需求做方案分析!' % approve.name
        self.send_mail(current_approve, subject=subject, content=content)
        self._message_poss(state=u'IT方案分析', action=u'委托他人分析', approve=current_approve.name)

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        params = self._context.get('params', None)
        action = params.get("action", 0) if params else 0
        my_action = self.env["ir.actions.act_window"].search([('id', '=', action)])
        res = super(dtdream_demand_app, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=False)
        doc = etree.XML(res['arch'])
        if my_action.name != u"我的申请":
            if res['type'] == "form":
                doc.xpath("//form")[0].set("create", "false")
            if res['type'] == "tree":
                doc.xpath("//tree")[0].set("create", "false")
        res['arch'] = etree.tostring(doc)
        return res

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        params = self._context.get('params', {})
        action = params.get('action', None)
        if action:
            menu = self.env["ir.actions.act_window"].search([('id', '=', action)]).name
        if menu == u"所有单据":
            manage = self.env.ref("dtdream_demand_manage.dtdream_demand_manage") in self.env.user.groups_id
            if manage:
                domain = domain if domain else []
            else:
                uid = self._context.get('uid', '')
                domain = expression.AND([['|', '|', '|', ('name.user_id', '=', uid), ('create_uid', '=', uid),
                                          ('current_approve.user_id', '=', uid), ('approves.user_id', '=', uid)], domain])
        return super(dtdream_demand_app, self).search_read(domain=domain, fields=fields, offset=offset,
                                                           limit=limit, order=order)

    def get_demand_app_menu(self):
        menu_id = self.env['ir.ui.menu'].search([('name', '=', u'IT需求管理')], limit=1).id
        parent_id = self.env['ir.ui.menu'].search([('name', '=', u'所有单据'), ('parent_id', '=', menu_id)], limit=1).id
        menu = self.env['ir.ui.menu'].search([('name', '=', u'应用开发及优化'), ('parent_id', '=', parent_id)], limit=1)
        action = menu.action.id
        return menu_id, action

    def get_mail_server_name(self):
        return self.env['ir.mail_server'].search([], limit=1).smtp_user

    def get_base_url(self, cr, uid):
        base_url = self.pool.get('ir.config_parameter').get_param(cr, uid, 'web.base.url')
        return base_url

    def send_mail(self, name, subject, content):
        email_to = name.work_email
        appellation = u'{0},您好：'.format(name.name)
        base_url = self.get_base_url()
        menu_id, action = self.get_demand_app_menu()
        url = '%s/web#id=%s&view_type=form&model=dtdream.demand.app&action=%s&menu_id=%s' % (base_url, self.id, action, menu_id)
        subject = subject
        content = content
        self.env['mail.mail'].create({
                'body_html': u'''<p>%s</p>
                                <p>%s</p>
                                <p><a href="%s">点击进入查看</a></p>
                                <p>dodo</p>
                                <p>万千业务，简单有do</p>
                                <p>%s</p>''' % (appellation, content, url, self.write_date[:10]),
                'subject': '%s' % subject,
                'email_from': self.get_mail_server_name(),
                'email_to': '%s' % email_to,
                'auto_delete': False,
            }).send()

    @api.multi
    def _message_poss(self, state, action, approve=''):
        self.message_post(body=u"""<table border="1" style="border-collapse: collapse;">
                                               <tr><td style="padding:10px">状态</td><td style="padding:10px">%s</td></tr>
                                               <tr><td style="padding:10px">操作</td><td style="padding:10px">%s</td></tr>
                                               <tr><td style="padding:10px">下一处理人</td><td style="padding:10px">%s</td></tr>
                                               </table>""" % (state, action, approve))

    @api.model
    def add_follower(self, user_id):
        """添加关注者"""
        self.message_subscribe_users(user_ids=[user_id.id])

    name = fields.Many2one('hr.employee', string='申请人',
                           default=lambda self: self.env["hr.employee"].search([("user_id", "=", self.env.user.id)]))
    department = fields.Many2one('hr.department', string='所属部门', compute=_compute_department_belong)
    expect_complete_time = fields.Date(string='期望完成时间')
    operate_type = fields.Selection([('create', '新增项目'), ('update', '优化项目')], string='项目类别')
    app_name = fields.Char(string='项目名称')
    description = fields.Text(string='需求描述')
    attachment = fields.Binary(string="附件(限制25M以下)", store=True)
    attachment_name = fields.Char(string="附件名")
    comments = fields.Text(string='评审意见')
    require_comments = fields.Text(string='需求评审意见')
    analyst = fields.Many2one('hr.employee', string='方案分析人员')
    entrusted_analyst = fields.Many2one('hr.employee', string='委托分析人员')
    conclude = fields.Text(string='结论')
    man_hours = fields.Integer(string='预估工时(人天)')
    priority = fields.Selection([('SS', 'SS'), ('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')], string='优先级')
    plan_comments = fields.Text(string='方案评审意见')
    practice_man = fields.Many2one('hr.employee', string='实施人员')
    plan_time = fields.Date(string='计划完成时间')
    done_time = fields.Date(string='实际完成时间')
    remark = fields.Text(string='备注')
    current_approve = fields.Many2one('hr.employee', string='当前处理人')
    approves = fields.Many2many('hr.employee', string='已审批的人')
    is_applicant = fields.Boolean(string='是否申请人', compute=_compute_is_applicant)
    is_creator = fields.Boolean(string='是否创建人', compute=_compute_is_creator, default=lambda self: True)
    is_analyst = fields.Boolean(string='是否方案分析人员', compute=_compute_is_analyst)
    is_entrusted_analyst = fields.Boolean(string='是否委托分析人员', compute=_compute_is_entrusted_analyst)
    is_practice_man = fields.Boolean(string='是否实施人员', compute=_compute_is_practice_man)
    is_direct_manage = fields.Boolean(string='是否直接主管', compute=_compute_is_direct_manage)
    is_IT_manage = fields.Boolean(string='是否IT部门主管', compute=_compute_is_it_manage)
    is_current = fields.Boolean(string='是否当前处理人', compute=_compute_is_current)
    is_manage = fields.Boolean(string='是否管理员', compute=_compute_login_is_manage)
    state = fields.Selection([('0', '草稿'),
                              ('1', '部门主管审批'),
                              ('2', 'IT需求审批'),
                              ('3', 'IT方案分析'),
                              ('4', 'IT方案审批'),
                              ('5', 'IT实施'),
                              ('99', '完成'),
                              ], string='状态', default='0')

    @api.multi
    def wkf_draft(self):
        self.write({"state": '0', 'current_approve': ''})

    @api.multi
    def wkf_department_approve(self):
        current_approve = self.name.department_id.manager_id
        self.write({"state": '1', 'current_approve': current_approve.id})
        subject = u'【通知】%s提交了应用开发及优化类需求申请' % self.name.name
        content = u'%s提交了应用开发及优化类需求申请,请您审批!' % self.name.name
        self.send_mail(current_approve, subject=subject, content=content)
        self._message_poss(state=u'草稿-->部门主管审批', action=u'提交', approve=current_approve.name)

    @api.multi
    def wkf_demand_approve(self):
        current_approve = self.env['hr.department'].search(
            [('name', '=', u'信息开发部'), ('parent_id.name', '=', u'综合开发部')], limit=1).manager_id
        approve = self.name.department_id.manager_id
        self.write({"state": '2', 'current_approve': current_approve.id, 'approves': [(4, approve.id)]})
        self.add_follower(user_id=approve.user_id)
        subject = u'【通知】%s提交了应用开发及优化类需求申请' % self.name.name
        content = u'%s提交了应用开发及优化类需求申请,请您审批!' % self.name.name
        self.send_mail(current_approve, subject=subject, content=content)
        self._message_poss(state=u'部门主管审批-->IT需求审批', action=u'同意', approve=current_approve.name)

    @api.multi
    def wkf_plan_analyst(self):
        current_approve = self.analyst
        approve = self.env['hr.department'].search(
            [('name', '=', u'信息开发部'), ('parent_id.name', '=', u'综合开发部')], limit=1).manager_id
        self.write({"state": '3', 'current_approve': current_approve.id, 'approves': [(4, approve.id)]})
        self.add_follower(user_id=approve.user_id)
        subject = u'【通知】%s提交了应用开发及优化类需求申请' % self.name.name
        content = u'%s提交了应用开发及优化类需求申请,请您分析方案!' % self.name.name
        self.send_mail(current_approve, subject=subject, content=content)
        self._message_poss(state=u'IT需求审批-->IT方案分析', action=u'同意', approve=current_approve.name)

    @api.multi
    def wkf_plan_approve(self):
        current_approve = self.env['hr.department'].search(
            [('name', '=', u'信息开发部'), ('parent_id.name', '=', u'综合开发部')], limit=1).manager_id
        if self.entrusted_analyst:
            approve = self.entrusted_analyst
        else:
            approve = self.analyst
        self.write({"state": '4', 'current_approve': current_approve.id, 'approves': [(4, approve.id)]})
        self.add_follower(user_id=approve.user_id)
        subject = u'【通知】%s提交了需求分析方案' % approve.name
        content = u'%s提交了需求分析方案,请您审批!' % approve.name
        self.send_mail(current_approve, subject=subject, content=content)
        self._message_poss(state=u'IT方案分析-->IT方案审批', action=u'提交', approve=current_approve.name)

    @api.multi
    def wkf_plan_doing(self):
        current_approve = self.practice_man
        self.write({"state": '5', 'current_approve': current_approve.id})
        subject = u'【通知】%s提交了应用开发类需求,请您按照方案实施' % self.name.name
        content = u'%s提交了应用开发类需求,请您按照方案实施!' % self.name.name
        self.send_mail(current_approve, subject=subject, content=content)
        self._message_poss(state=u'IT方案审批-->IT实施', action=u'同意', approve=current_approve.name)

    @api.multi
    def wkf_done(self):
        approve = self.practice_man
        self.write({"state": '99', 'current_approve': '', 'approves': [(4, approve.id)]})
        self.add_follower(user_id=approve.user_id)
        self._message_poss(state=u'IT实施-->完成', action=u'提交', approve= '')










