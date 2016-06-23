# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.exceptions import ValidationError
from datetime import datetime
from lxml import etree


class dtdream_hr_performance(models.Model):
    _name = "dtdream.hr.performance"
    _inherit = ['mail.thread']
    _description = u"员工PBC"

    @api.onchange('department', 'quarter')
    def _onchange_compute_hr_pbc(self):
        if self.department and self.quarter:
            cr = self.env['dtdream.hr.pbc'].search([('year', '=', self.year), ('state', '=', '99'), ('quarter', '=', self.quarter), '|', ('name', '=', self.department.parent_id.id), ('name', '=', self.department.id)])
            self.pbc = cr

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

    @api.model
    def create(self, vals):
        pbc = vals.get('pbc', '')
        for val in pbc:
            val[0] = 4
        vals['pbc'] = pbc
        return super(dtdream_hr_performance, self).create(vals)

    @api.multi
    def write(self, vals, flag=True):
        return super(dtdream_hr_performance, self).write(vals)

    def get_inter_employee(self):
        cr = self.env['dtdream.pbc.hr.config'].search([], limit=1)
        inter = [rec.name.user_id for rec in cr.interface]
        manage = cr.manage
        return inter, manage

    @api.multi
    def _compute_is_inter_department(self):
        inter, manage = self.get_inter_employee()
        pbc = self.search([])
        for rec in pbc:
            if rec.env.user == manage.user_id:
                rec.write({"view_all": True}, False)
            elif rec.env.user not in inter:
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
            cr = self.env['dtdream.pbc.hr.config'].search([], limit=1)
            inter = [rec.name.user_id for rec in cr.interface]
            inter.append(cr.manage.user_id)
            if self.env.user not in inter:
                if res['type'] == "form":
                    doc.xpath("//form")[0].set("create", "false")
                if res['type'] == "tree":
                    doc.xpath("//tree")[0].set("create", "false")
        res['arch'] = etree.tostring(doc)
        self._compute_is_inter_department()
        return res

    name = fields.Many2one('hr.employee', string='花名', required=True)
    department = fields.Many2one('hr.department', string='部门', compute=_compute_employee_info)
    workid = fields.Char(string='工号', compute=_compute_employee_info)
    year = fields.Char(string='考核年度', default=lambda self: u"%s财年" % datetime.now().year, readonly=True)
    quarter = fields.Selection([('1', 'Q1'),
                                ('2', 'Q2'),
                                ('3', 'Q3'),
                                ('4', 'Q4')], string='考核季度', required=True)
    officer = fields.Many2one('hr.employee', string='主管')
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
    pbc = fields.Many2many('dtdream.hr.pbc', string="部门PBC")
    pbc_employee = fields.One2many('dtdream.hr.pbc.employee', 'perform', string='个人PBC')
    login = fields.Boolean(compute=_compute_name_is_login)
    is_officer = fields.Boolean(compute=_compute_officer_is_login)
    view_all = fields.Boolean(string='所有单据')

    _sql_constraints = [
        ('name_quarter_uniq', 'unique (name,quarter, year)', '每个员工每个季度只能有一条员工PBC !')
    ]

    @api.multi
    def wkf_wait_write(self):
        self.write({'state': '1'})

    @api.multi
    def wkf_confirm(self):
        self.write({'state': '2'})

    @api.multi
    def wkf_evaluate(self):
        self.write({'state': '3'})

    @api.multi
    def wkf_conclud(self):
        self.write({'state': '4'})

    @api.multi
    def wkf_rate(self):
        self.write({'state': '5'})

    @api.multi
    def wkf_final(self):
        self.write({'state': '6'})

    @api.multi
    def wkf_done(self):
        self.write({'state': '99'})


class dtdream_hr_pbc_employee(models.Model):
    _name = "dtdream.hr.pbc.employee"

    def _compute_state_related(self):
        for rec in self:
            rec.state = rec.perform.state

    def _compute_name_is_login(self):
        for rec in self:
            if rec.env.user == rec.perform.name.user_id:
                rec.login = True
            else:
                rec.login = False

    perform = fields.Many2one('dtdream.hr.performance')
    work = fields.Char(string='工作目标')
    detail = fields.Text(string='具体描述')
    result = fields.Text(string='关键事件达成')
    evaluate = fields.Text(string='主管评价')
    login = fields.Boolean(compute=_compute_name_is_login)
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
    _inherit = ['mail.thread']

    @api.onchange("target")
    def _compute_work_content(self):
        content = ""
        count = 0
        for rec in self.target:
            count += 1
            content += "{0}. {1}\n".format(count, rec.works)
        self.content = content

    def get_inter_employee(self):
        cr = self.env['dtdream.pbc.hr.config'].search([], limit=1)
        inter = [rec.name.user_id for rec in cr.interface]
        inter.append(cr.manage.user_id)
        return inter

    @api.multi
    def _compute_is_inter(self):
        inter = self.get_inter_employee()
        pbc = self.search([])
        for rec in pbc:
            if self.env.user not in inter:
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
        inter = self.get_inter_employee()
        if self.env.user not in inter:
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
            cr = rec.env['dtdream.pbc.hr.config'].search([], limit=1)
            if rec.env.user != cr.manage.user_id:
                inter = rec.env['dtdream.pbc.hr.interface'].search([('name.user_id', '=', rec.env.user.id)])
                if not inter:
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
            cr = self.env['dtdream.pbc.hr.config'].search([], limit=1)
            if self.env.user != cr.manage.user_id:
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
        cr = self.env['dtdream.pbc.hr.config'].search([], limit=1)
        if self.env.user != cr.manage.user_id:
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
    year = fields.Char(string='考核年度', default=lambda self: u"%s财年" % datetime.now().year, readonly=True)
    quarter = fields.Selection([('1', 'Q1'),
                                ('2', 'Q2'),
                                ('3', 'Q3'),
                                ('4', 'Q4'),
                                ], string='考核季度', required=True)
    state = fields.Selection([('0', '草稿'),
                              ('99', '完成'),
                              ], string='状态', default='0')
    target = fields.One2many('dtdream.pbc.target', 'target', string='工作内容')
    content = fields.Text(string="工作内容")

    _sql_constraints = [
        ('name_quarter_uniq', 'unique (name,quarter, year)', '每个季度只能有一条PBC !')
    ]

    @api.multi
    def wkf_done(self):
        self.write({'state': '99'})


class dtdream_pbc_target(models.Model):
    _name = "dtdream.pbc.target"

    target = fields.Many2one('dtdream.hr.pbc', string='部门PBC')
    num = fields.Char(string='业务目标')
    works = fields.Text(string='关键指标,关键动作,行为', required=True)


class dtdream_pbc_hr_config(models.Model):
    _name = "dtdream.pbc.hr.config"

    manage = fields.Many2one('hr.employee', string='绩效管理员')
    interface = fields.One2many('dtdream.pbc.hr.interface', 'inter', string='业务接口人设置')


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


