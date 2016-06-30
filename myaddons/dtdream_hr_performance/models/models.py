# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.exceptions import ValidationError
from lxml import etree


class dtdream_hr_performance(models.Model):
    _name = "dtdream.hr.performance"
    _inherit = ['mail.thread']
    _description = u"员工PBC"

    @api.onchange('department', 'quarter')
    def _onchange_compute_hr_pbc(self):
        if self.department and self.quarter:
            cr = self.env['dtdream.hr.pbc'].search([('state', '=', '99'), ('quarter', '=', self.quarter), '|', ('name', '=', self.department.parent_id.id), ('name', '=', self.department.id)])
            target = [t.id for crr in cr for t in crr.target]
            self.pbc = [(6, 0, target)]

    @api.multi
    def update_dtdream_hr_pbc(self):
        pbc = self.search([])
        for rec in pbc:
            cr = self.env['dtdream.hr.pbc'].search([('state', '=', '99'), ('quarter', '=', rec.quarter), '|', ('name', '=', rec.department.parent_id.id), ('name', '=', rec.department.id)])
            target = [t.id for crr in cr for t in crr.target]
            rec.write({"pbc": [(6, 0, target)]})

    @api.depends('name')
    def _compute_employee_info(self):
        for rec in self:
            rec.workid = rec.name.job_number
            rec.department = rec.name.department_id
            rec.onwork = rec.name.Inaugural_state

    def _compute_name_is_login(self):
        if self.env.user == self.name.user_id:
            self.login = True
        else:
            self.login = False

    def _compute_officer_is_login(self):
        if self.env.user == self.officer.user_id:
            self.is_officer = True
        else:
            self.is_officer = False

    def _compute_login_is_manage(self):
        if self.env.ref("dtdream_hr_performance.group_hr_manage_performance") in self.env.user.groups_id:
            self.manage = True
        else:
            self.manage = False

    @api.model
    def create(self, vals):
        pbc = vals.get('pbc', '')
        if not pbc:
            employee = self.env['hr.employee'].search([('id', '=', vals.get('name', 0))])
            pbc = self.env['dtdream.hr.pbc'].search([('state', '=', '99'), ('quarter', '=', vals.get('quarter', '')),
                                                     '|', ('name', '=', employee.department_id.parent_id.id),
                                                     ('name', '=', employee.department_id.id)])
            vals['pbc'] = [[4, cr.id] for cr in pbc]
        else:
            for val in pbc:
                val[0] = 4
            vals['pbc'] = pbc
        return super(dtdream_hr_performance, self).create(vals)

    @api.multi
    def write(self, vals, flag=True):
        result = vals.get('result', '')
        if result and result.strip() and self.state == "6":
            self.signal_workflow('btn_import')
        return super(dtdream_hr_performance, self).write(vals)

    @api.multi
    def _compute_is_inter_department(self):
        pbc = self.search([])
        for rec in pbc:
            if rec.env.ref("dtdream_hr_performance.group_hr_manage_performance") in rec.env.user.groups_id:
                rec.write({"view_all": True}, False)
            elif rec.env.ref("dtdream_hr_performance.group_hr_inter_performance") not in rec.env.user.groups_id:
                rec.write({"view_all": False}, False)
            else:
                cr = rec.env['dtdream.pbc.hr.interface'].search([('name.user_id', '=', rec.env.user.id)])
                department_id = [department.id for department in cr.department.child_ids if cr.department.child_ids]
                department_id.append(cr.department.id)
                if rec.department.id in department_id:
                    rec.write({"view_all": True}, False)
                else:
                    rec.write({"view_all": False}, False)

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        params = self._context.get('params', None)
        action = params.get("action", 0) if params else 0
        my_action = self.env["ir.actions.act_window"].search([('id', '=', action)])
        res = super(dtdream_hr_performance, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=False)
        doc = etree.XML(res['arch'])
        if my_action.name != u"绩效管理":
            if res['type'] == "form":
                doc.xpath("//form")[0].set("create", "false")
            if res['type'] == "tree":
                doc.xpath("//tree")[0].set("create", "false")
        else:
            inter = self.env.ref("dtdream_hr_performance.group_hr_inter_performance") not in self.env.user.groups_id
            manage = self.env.ref("dtdream_hr_performance.group_hr_manage_performance") not in self.env.user.groups_id
            if inter and manage:
                if res['type'] == "form":
                    doc.xpath("//form")[0].set("create", "false")
                if res['type'] == "tree":
                    doc.xpath("//tree")[0].set("create", "false")
        res['arch'] = etree.tostring(doc)
        self._compute_is_inter_department()
        self.update_dtdream_hr_pbc()
        return res

    @api.multi
    def message_subscribe_users(self, user_ids=None, subtype_ids=None):
        user_ids = []
        result = self.message_subscribe(self.env['res.users'].browse(user_ids).mapped('partner_id').ids, subtype_ids=subtype_ids)
        return result

    def get_mail_server_name(self):
        return self.env['ir.mail_server'].search([], limit=1).smtp_user

    def send_mail_attend_mobile(self, name, subject, content):
        email_to = name.work_email
        appellation = u'{0},您好：'.format(name.name)
        url = '/web#id=%s&view_type=form&model=dtdream.hr.performance' % self.id
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

    name = fields.Many2one('hr.employee', string='花名', required=True)
    department = fields.Many2one('hr.department', string='部门', compute=_compute_employee_info, store=True)
    workid = fields.Char(string='工号', compute=_compute_employee_info, strore=True)
    quarter = fields.Char(string='考核季度', required=True)
    officer = fields.Many2one('hr.employee', string='一考主管', required=True)
    officer_sec = fields.Many2one('hr.employee', string='二考主管', required=True)
    result = fields.Char(string='考核结果')
    onwork = fields.Selection([('Inaugural_state_01', '在职'), ('Inaugural_state_02', '离职')],
                              string="在职状态", compute=_compute_employee_info)
    state = fields.Selection([('0', '待启动'),
                              ('1', '待填写PBC'),
                              ('2', '待主管确认'),
                              ('3', '待考评启动'),
                              ('4', '待总结'),
                              ('5', '待主管评价'),
                              ('6', '待最终考评'),
                              ('99', '考评完成')
                              ], string='状态', default='0')
    pbc = fields.Many2many('dtdream.pbc.target', string="部门PBC")
    pbc_employee = fields.One2many('dtdream.hr.pbc.employee', 'perform', string='个人PBC')
    login = fields.Boolean(compute=_compute_name_is_login)
    is_officer = fields.Boolean(compute=_compute_officer_is_login)
    view_all = fields.Boolean()
    manage = fields.Boolean(string='当前登入者是否绩效管理员', compute=_compute_login_is_manage)

    _sql_constraints = [
        ('name_quarter_uniq', 'unique (name,quarter)', '每个员工每个季度只能有一条员工PBC !')
    ]

    @api.multi
    def wkf_wait_write(self):
        if self.state == '0':
            content = u"您的个人PBC绩效考核已启动,请您填写本季度工作目标,以及具体描述!"
            self.send_mail_attend_mobile(self.name, subject=content, content=content)
        else:
            content = u"您的个人PBC绩效考核已被驳回,请您修改相关内容后再提交!"
            self.send_mail_attend_mobile(self.name, subject=content, content=content)
        self.write({'state': '1'})

    @api.multi
    def wkf_confirm(self):
        self.write({'state': '2'})
        content = u'%s,提交了个人PBC绩效考核,请你确认!' % self.name.name
        self.send_mail_attend_mobile(self.officer, subject=content, content=content)

    @api.multi
    def wkf_evaluate(self):
        self.write({'state': '3'})
        content = u"%s,已经确认了您的个人PBC绩效考核,请您查看!" % self.officer.name
        self.send_mail_attend_mobile(self.name, subject=content, content=content)

    @api.multi
    def wkf_conclud(self):
        self.write({'state': '4'})
        content = u"您的个人PBC绩效考评已启动,请您填写个人总结!"
        self.send_mail_attend_mobile(self.name, subject=content, content=content)

    @api.multi
    def wkf_rate(self):
        self.write({'state': '5'})
        content = u'%s,提交了个人PBC绩效考核总结,请您对该员工进行评价!' % self.name.name
        self.send_mail_attend_mobile(self.officer, subject=content, content=content)

    @api.multi
    def wkf_final(self):
        self.write({'state': '6'})
        content = u'%s,已对您的个人PBC绩效考核做出了评价,请您查看!' % self.officer.name
        self.send_mail_attend_mobile(self.name, subject=content, content=content)

    @api.multi
    def wkf_done(self):
        self.write({'state': '99'})
        content = u'您的个人PBC绩效考核结果已经导入,请您查看!'
        self.send_mail_attend_mobile(self.name, subject=content, content=content)


class dtdream_hr_pbc_employee(models.Model):
    _name = "dtdream.hr.pbc.employee"

    def _compute_state_related(self):
        for rec in self:
            rec.state = rec.perform.state
            rec.officer = rec.perform.officer

    def _compute_name_is_login(self):
        for rec in self:
            if rec.env.user == rec.perform.name.user_id:
                rec.login = True
            else:
                rec.login = False

    def _compute_login_is_officer(self):
        for rec in self:
            if rec.env.user == rec.perform.officer.user_id:
                rec.officer = True
            else:
                rec.officer = False

    def _compute_login_is_manage(self):
        for rec in self:
            rec.manage = rec.perform.manage

    perform = fields.Many2one('dtdream.hr.performance')
    work = fields.Char(string='工作目标')
    detail = fields.Text(string='具体描述')
    result = fields.Text(string='关键事件达成')
    evaluate = fields.Text(string='主管评价')
    login = fields.Boolean(compute=_compute_name_is_login)
    officer = fields.Boolean(compute=_compute_login_is_officer)
    manage = fields.Boolean(string='当前登入者是否绩效管理员', compute=_compute_login_is_manage)
    state = fields.Selection([('0', '待启动'),
                              ('1', '待填写PBC'),
                              ('2', '待主管确认'),
                              ('3', '待考评启动'),
                              ('4', '待总结'),
                              ('5', '待主管评价'),
                              ('6', '待最终考评'),
                              ('99', '考评完成')
                              ], string='状态', default='1', compute=_compute_state_related)


class dtdream_hr_pbc(models.Model):
    _name = "dtdream.hr.pbc"
    _description = u'部门PBC'
    _inherit = ['mail.thread']

    def get_inter_employee(self):
        cr = self.env['dtdream.pbc.hr.config'].search([], limit=1)
        inter = [rec.name.user_id for rec in cr.interface]
        return inter

    @api.multi
    def _compute_is_inter(self):
        pbc = self.search([])
        for rec in pbc:
            if rec.env.ref("dtdream_hr_performance.group_hr_inter_performance") not in rec.env.user.groups_id:
                rec.write({"is_inter": False}, False)
            else:
                rec.write({"is_inter": True}, False)

    @api.multi
    def _compute_login_in_department(self):
        cr = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)])
        pbc = self.search([])
        for rec in pbc:
            if rec.name == cr.department_id or rec.name == cr.department_id.parent_id:
                rec.write({"is_in_department": True}, False)
            else:
                rec.write({"is_in_department": False}, False)

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(dtdream_hr_pbc, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=False)
        doc = etree.XML(res['arch'])
        inter = self.env.ref("dtdream_hr_performance.group_hr_inter_performance") not in self.env.user.groups_id
        manage = self.env.ref("dtdream_hr_performance.group_hr_manage_performance") not in self.env.user.groups_id
        if inter and manage:
            if res['type'] == "form":
                doc.xpath("//form")[0].set("create", "false")
                doc.xpath("//form")[0].set("edit", "false")
            if res['type'] == "tree":
                doc.xpath("//tree")[0].set("create", "false")
                doc.xpath("//tree")[0].set("edit", "false")
        res['arch'] = etree.tostring(doc)
        self._compute_login_in_department()
        self._compute_is_inter()
        return res

    @api.multi
    def unlink(self):
        for rec in self:
            department = []
            manage = rec.env.ref("dtdream_hr_performance.group_hr_manage_performance") not in rec.env.user.groups_id
            if manage:
                inter = rec.env['dtdream.pbc.hr.interface'].search([('name.user_id', '=', rec.env.user.id)])
                if rec.env.ref("dtdream_hr_performance.group_hr_inter_performance") not in rec.env.user.groups_id:
                    raise ValidationError("普通员工无法删除部门PBC!")
                for crr in inter:
                    department.append(crr.department.id)
                    for depart in crr.department.child_ids:
                        department.append(depart.id)
                if rec.name.id not in department:
                    raise ValidationError("HR接口人只能删除所接口部门的部门PBC!")
        return super(dtdream_hr_pbc, self).unlink()

    @api.multi
    def write(self, vals, flag=True):
        if flag:
            department = []
            manage = self.env.ref("dtdream_hr_performance.group_hr_manage_performance") not in self.env.user.groups_id
            if manage:
                inter = self.env['dtdream.pbc.hr.interface'].search([('name.user_id', '=', self.env.user.id)])
                for crr in inter:
                    department.append(crr.department.id)
                    for depart in crr.department.child_ids:
                        department.append(depart.id)
                if self.name.id not in department:
                    raise ValidationError("HR接口人只能编辑所接口部门的部门PBC!")
        return super(dtdream_hr_pbc, self).write(vals)

    @api.model
    def create(self, vals):
        department = []
        manage = self.env.ref("dtdream_hr_performance.group_hr_manage_performance") not in self.env.user.groups_id
        if manage:
            inter = self.env['dtdream.pbc.hr.interface'].search([('name.user_id', '=', self.env.user.id)])
            for crr in inter:
                department.append(crr.department.id)
                for depart in crr.department.child_ids:
                    department.append(depart.id)
            if vals.get('name', '') not in department:
                raise ValidationError("HR接口人只能创建所接口部门的部门PBC!")
        return super(dtdream_hr_pbc, self).create(vals)

    name = fields.Many2one('hr.department', string='部门', required=True)
    is_inter = fields.Boolean(string="是否接口人", default=lambda self: True)
    is_in_department = fields.Boolean(string='是否所在部门')
    quarter = fields.Char(string='考核季度', required=True)
    state = fields.Selection([('0', '草稿'),
                              ('99', '完成'),
                              ], string='状态', default='0')
    target = fields.One2many('dtdream.pbc.target', 'target', string='工作内容')

    _sql_constraints = [
        ('name_quarter_uniq', 'unique (name,quarter)', '每个季度只能有一条PBC !')
    ]

    @api.multi
    def wkf_done(self):
        self.write({'state': '99'})


class dtdream_pbc_target(models.Model):
    _name = "dtdream.pbc.target"
    _order = "target"

    def _compute_department_target(self):
        for rec in self:
            rec.depart_target = rec.target.name.complete_name

    target = fields.Many2one('dtdream.hr.pbc', string='部门PBC')
    depart_target = fields.Char(compute=_compute_department_target)
    num = fields.Char(string='业务目标')
    works = fields.Text(string='关键指标,关键动作,行为', required=True)


class dtdream_pbc_hr_config(models.Model):
    _name = "dtdream.pbc.hr.config"

    interface = fields.One2many('dtdream.pbc.hr.interface', 'inter', string='业务接口部门设置')


class dtdream_pbc_hr_interface(models.Model):
    _name = "dtdream.pbc.hr.interface"

    name = fields.Many2one('hr.employee', string='HR接口人')
    department = fields.Many2one('hr.department', string='接口业务部门')
    inter = fields.Many2one('dtdream.pbc.hr.config')


class dtdream_hr_pbc_start(models.TransientModel):
    _name = "dtdream.hr.pbc.start"

    @api.one
    def start_hr_pbc(self):
        context = dict(self._context or {})
        pbc = context.get('active_ids', []) or []
        performance = self.env['dtdream.hr.performance'].browse(pbc)
        for per in performance:
            if per.state == '0' and per.onwork == 'Inaugural_state_01':
                per.signal_workflow('btn_start')
        return {'type': 'ir.actions.act_window_close'}

    @api.one
    def start_hr_pbc_evaluate(self):
        context = dict(self._context or {})
        pbc = context.get('active_ids', []) or []
        performance = self.env['dtdream.hr.performance'].browse(pbc)
        for per in performance:
            if per.state == '3':
                per.signal_workflow('btn_start2')
        return {'type': 'ir.actions.act_window_close'}


