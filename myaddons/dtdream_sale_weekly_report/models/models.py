# -*- coding: utf-8 -*-

from openerp import models, fields, api
from datetime import datetime
from dateutil.relativedelta import relativedelta

class dtdream_sale_own_report(models.Model):
    _name = 'dtdream.sale.own.report'
    _description = u"个人周报"

    state = fields.Selection(
        [('0', '草稿'),
         ('submit', '已提交')], string="状态", default="0",track_visibility='onchange')

    @api.depends('report_person')
    def _compute_reportor_info(self):
        for ref in self:
            ref.report_person_name = ref.report_person.name
            ref.job_number = ref.report_person.job_number
            ref.department = ref.report_person.department_id.name
            try:
                ref.id - ref.id
            except:
                recs = ref.env["crm.lead"].search([('bidding_time','>=',(datetime.now() - relativedelta(months=3))),('type','=','opportunity')])
                zhengwu_recs = recs.search([('system_department_id.name','=',u"政务系统部")])
                zhengfa_recs = recs.search([('system_department_id.name','=',u"政法系统部")])
                shared_business_recs = recs.search([('system_department_id.name','=',u"共享业务部")])
                dic_zhengwu_recs = [(0,0,{"project_id":i.id}) for i in zhengwu_recs]
                ref.zhengwu_project = False
                ref.zhengwu_project = dic_zhengwu_recs
                dic_zhengfa_recs = [(0,0,{"project_id":i.id}) for i in zhengfa_recs]
                ref.zhengfa_project = False
                ref.zhengfa_project = dic_zhengfa_recs
                dic_shared_business_recs = [(0,0,{"project_id":i.id}) for i in shared_business_recs]
                ref.shared_project = False
                ref.shared_project = dic_shared_business_recs
            ref.zhengwu_total_space = len(ref.zhengwu_project)
            ref.zhengfa_total_space = len(ref.zhengfa_project)
            ref.shared_total_space = len(ref.shared_project)
            zhengwu_space_total = 0
            for rec in ref.zhengwu_project:
                zhengwu_space_total = zhengwu_space_total + rec.space_total
            ref.zhengwu_total_project = zhengwu_space_total
            zhengfa_space_total = 0
            for recc in ref.zhengfa_project:
                zhengfa_space_total = zhengfa_space_total + recc.space_total
            ref.zhengfa_total_project = zhengfa_space_total
            shared_space_total = 0
            for rrec in ref.shared_project:
                shared_space_total = shared_space_total + rrec.space_total
            ref.shared_total_project = shared_space_total

    report_person = fields.Many2one('hr.employee','报告人',default=lambda self:self.env['hr.employee'].search([('login','=',self.env.user.login)]))
    report_person_name = fields.Char(string="报告人花名",compute=_compute_reportor_info)
    job_number = fields.Char(string="工号",compute=_compute_reportor_info)
    department = fields.Char(string="部门",compute=_compute_reportor_info)
    week = fields.Integer(string="周别")

    name = fields.Char('个人周报')
    zhengwu_project = fields.One2many("zhengwu.system.project","zhengwu_project_id",copy=True)
    zhengwu_total_space = fields.Char("项目个数",compute=_compute_reportor_info)
    zhengwu_total_project = fields.Float("整体空间(万元)",compute=_compute_reportor_info)
    zhengwu_important_project = fields.Char("重大项目个数",compute=_compute_reportor_info)
    zhengwu_important_space = fields.Float("重大整体空间(万元)",compute=_compute_reportor_info)

    zhengfa_project = fields.One2many("zhengfa.system.project","zhengfa_project_id")
    zhengfa_total_space = fields.Char("项目个数",compute=_compute_reportor_info)
    zhengfa_total_project = fields.Float("整体空间(万元)",compute=_compute_reportor_info)
    zhengfa_important_project = fields.Char("重大项目个数",compute=_compute_reportor_info)
    zhengfa_important_space = fields.Float("重大整体空间(万元)",compute=_compute_reportor_info)

    shared_project = fields.One2many("shared.business.project","shared_project_id")
    shared_total_space = fields.Char("项目个数",compute=_compute_reportor_info)
    shared_total_project = fields.Float("整体空间(万元)",compute=_compute_reportor_info)
    shared_important_project = fields.Char("重大项目个数",compute=_compute_reportor_info)
    shared_important_space = fields.Float("重大整体空间(万元)",compute=_compute_reportor_info)

    lead_project = fields.One2many("lead.project","lead_project_id")
    sale_channel = fields.One2many("sale.channel","sale_channel_id")
    competitor_situation = fields.One2many("competitor.situation","competitor_situation_id")
    sale_other = fields.One2many("sale.other","sale_other_id")

    dtdream_problem_help = fields.One2many("problem.help","problem_help_id")

    next_zhengwu_project = fields.One2many("zhengwu.system.project","next_zhengwu_project_id")
    next_zhengwu_total_space = fields.Char("项目个数")
    next_zhengwu_total_project = fields.Float("整体空间(万元)")
    next_zhengwu_important_project = fields.Char("重大项目个数")
    next_zhengwu_important_space = fields.Float("重大整体空间(万元)")

    next_zhengfa_project = fields.One2many("zhengfa.system.project","next_zhengfa_project_id")
    next_zhengfa_total_space = fields.Char("项目个数")
    next_zhengfa_total_project = fields.Float("整体空间(万元)")
    next_zhengfa_important_project = fields.Char("重大项目个数")
    next_zhengfa_important_space = fields.Float("重大整体空间(万元)")

    next_shared_project = fields.One2many("shared.business.project","next_shared_project_id")
    next_shared_total_space = fields.Char("项目个数")
    next_shared_total_project = fields.Float("整体空间(万元)")
    next_shared_important_project = fields.Char("重大项目个数")
    next_shared_important_space = fields.Float("重大整体空间(万元)")

    next_sale_other = fields.One2many("sale.other","next_sale_other_id")

    @api.model
    def default_get(self, fields):
        res = super(dtdream_sale_own_report, self).default_get(fields)
        return res

# 政务系统部项目
class zhengwu_system_project(models.Model):
    _name = 'zhengwu.system.project'
    _description = u"政务系统部项目"

    zhengwu_project_id = fields.Many2one("dtdream.sale.own.report",string="个人周报")
    manager_zhengwu_project_id = fields.Many2one("dtdream.sale.own.report",string="主管周报")
    next_zhengwu_project_id = fields.Many2one("dtdream.sale.own.report",string="个人周报")
    manager_next_zhengwu_project_id = fields.Many2one("dtdream.sale.own.report",string="主管周报")

    @api.depends('project_id')
    def _compute_project_info(self):
        for rec in self:
            rec.office_id = rec.project_id.office_id.name
            rec.sale_apply_id = rec.project_id.sale_apply_id.name
            rec.space_total = rec.project_id.space_total
            rec.project_master_degree = rec.project_id.project_master_degree
            rec.bidding_time = rec.project_id.bidding_time
            rec.project_number = rec.project_id.project_number
            str = ""
            for recc in rec.project_id.des_records:
                str = str + recc.name + u";"
            rec.project_process = str


    office_id = fields.Char(string="办事处",compute=_compute_project_info)
    project_id = fields.Many2one('crm.lead',string="项目名称")
    sale_apply_id = fields.Char(string="营销责任人",compute=_compute_project_info)
    space_total = fields.Float(string="项目空间",compute=_compute_project_info)
    project_master_degree = fields.Selection([
        ('1', 'A'),
        ('2', 'B'),
        ('3', 'C'),
        ('4', 'D'),
    ],'项目把握度',compute=_compute_project_info)
    bidding_time = fields.Char(string="预计投标日期",compute=_compute_project_info)
    project_process = fields.Text(string="项目进展",compute=_compute_project_info)
    add_project_process = fields.Text(string="补充项目进展")
    project_number = fields.Char(string="项目编号",compute=_compute_project_info)

class zhengfa_system_project(models.Model):
    _name = 'zhengfa.system.project'
    _description = u"政法系统部项目"

    @api.depends('project_id')
    def _compute_project_info(self):
        for rec in self:
            rec.office_id = rec.project_id.office_id.name
            rec.sale_apply_id = rec.project_id.sale_apply_id.name
            rec.space_total = rec.project_id.space_total
            rec.project_master_degree = rec.project_id.project_master_degree
            rec.bidding_time = rec.project_id.bidding_time
            rec.project_number = rec.project_id.project_number
            str = ""
            for recc in rec.project_id.des_records:
                str = str + recc.name + u";"
            rec.project_process = str

    zhengfa_project_id = fields.Many2one("dtdream.sale.own.report",string="个人周报")
    manager_zhengfa_project_id = fields.Many2one("dtdream.sale.own.report",string="主管周报")
    next_zhengfa_project_id = fields.Many2one("dtdream.sale.own.report",string="个人周报")
    manager_next_zhengfa_project_id = fields.Many2one("dtdream.sale.own.report",string="主管周报")

    office_id = fields.Char(string="办事处",compute=_compute_project_info)
    project_id = fields.Many2one('crm.lead',string="项目名称")
    sale_apply_id = fields.Char(string="营销责任人",compute=_compute_project_info)
    space_total = fields.Float(string="项目空间",compute=_compute_project_info)
    project_master_degree = fields.Selection([
        ('1', 'A'),
        ('2', 'B'),
        ('3', 'C'),
        ('4', 'D'),
    ],'项目把握度',compute=_compute_project_info)
    bidding_time = fields.Char(string="预计投标日期",compute=_compute_project_info)
    project_process = fields.Text(string="项目进展",compute=_compute_project_info)
    add_project_process = fields.Text(string="补充项目进展")
    project_number = fields.Char(string="项目编号",compute=_compute_project_info)

class shared_business_project(models.Model):
    _name = 'shared.business.project'
    _description = u"共享业务部"

    @api.depends('project_id')
    def _compute_project_info(self):
        for rec in self:
            rec.office_id = rec.project_id.office_id.name
            rec.sale_apply_id = rec.project_id.sale_apply_id.name
            rec.space_total = rec.project_id.space_total
            rec.project_master_degree = rec.project_id.project_master_degree
            rec.bidding_time = rec.project_id.bidding_time
            rec.project_number = rec.project_id.project_number
            str = ""
            for recc in rec.project_id.des_records:
                str = str + recc.name + u";"
            rec.project_process = str

    shared_project_id = fields.Many2one("dtdream.sale.own.report",string="个人周报")
    manager_shared_project_id = fields.Many2one("dtdream.sale.own.report",string="主管周报")
    next_shared_project_id = fields.Many2one("dtdream.sale.own.report",string="个人周报")
    manager_next_shared_project_id = fields.Many2one("dtdream.sale.own.report",string="主管周报")
    office_id = fields.Char(string="办事处",compute=_compute_project_info)
    project_id = fields.Many2one('crm.lead',string="项目名称")
    sale_apply_id = fields.Char(string="营销责任人",compute=_compute_project_info)
    space_total = fields.Float(string="项目空间",compute=_compute_project_info)
    project_master_degree = fields.Selection([
        ('1', 'A'),
        ('2', 'B'),
        ('3', 'C'),
        ('4', 'D'),
    ],'项目把握度',compute=_compute_project_info)
    bidding_time = fields.Char(string="预计投标日期",compute=_compute_project_info)
    project_process = fields.Text(string="项目进展",compute=_compute_project_info)
    add_project_process = fields.Text(string="补充项目进展")
    project_number = fields.Char(string="项目编号",compute=_compute_project_info)


# 重大机会点
class lead_project(models.Model):
    _name = 'lead.project'
    _description = u"重大机会点"

    lead_project_id = fields.Many2one("dtdream.sale.own.report",string="个人周报")
    manager_lead_project_id = fields.Many2one("dtdream.sale.own.report",string="主管周报")

    @api.depends('project_id')
    def _compute_project_info(self):
        for rec in self:
            rec.office_id = rec.project_id.office_id.name
            rec.sale_apply_id = rec.project_id.sale_apply_id.name
            rec.space_total = rec.project_id.space_total
            rec.project_master_degree = rec.project_id.project_master_degree
            rec.bidding_time = rec.project_id.bidding_time
            rec.project_number = rec.project_id.project_number
            str = ""
            for recc in rec.project_id.des_records:
                str = str + recc.name + u";"
            rec.project_process = str

    office_id = fields.Char(string="办事处",compute=_compute_project_info)
    project_id = fields.Many2one('crm.lead',string="项目名称")
    sale_apply_id = fields.Char(string="营销责任人",compute=_compute_project_info)
    space_total = fields.Float(string="项目空间",compute=_compute_project_info)
    project_master_degree = fields.Selection([
        ('1', 'A'),
        ('2', 'B'),
        ('3', 'C'),
        ('4', 'D'),
    ],'项目把握度',compute=_compute_project_info)
    bidding_time = fields.Char(string="预计投标日期",compute=_compute_project_info)
    project_process = fields.Text(string="项目进展",compute=_compute_project_info)
    add_project_process = fields.Text(string="补充项目进展")
    project_number = fields.Char(string="项目编号",compute=_compute_project_info)


# 渠道进展
class sale_channel(models.Model):
    _name = 'sale.channel'
    _description = u"渠道进展"

    sale_channel_id = fields.Many2one("dtdream.sale.own.report",string="个人周报")
    manager_sale_channel_id = fields.Many2one("dtdream.sale.own.report",string="主管周报")

    name = fields.Char("渠道名称")
    project_id = fields.Many2one("crm.lead",string="关联项目")
    channer_process = fields.Text("进展")

# 竞争对手情况
class competitor_situation(models.Model):
    _name = 'competitor.situation'
    _description = u"竞争对手情况"

    competitor_situation_id = fields.Many2one("dtdream.sale.own.report",string="个人周报")
    manager_competitor_situation_id = fields.Many2one("dtdream.sale.own.report",string="主管周报")

    name = fields.Char("详情")

# 其他
class sale_other(models.Model):
    _name = 'sale.other'
    _description = u"其他"

    sale_other_id = fields.Many2one("dtdream.sale.own.report",string="个人周报")
    manager_sale_other_id = fields.Many2one("dtdream.sale.own.report",string="主管周报")
    next_sale_other_id = fields.Many2one("dtdream.sale.own.report",string="个人周报")
    manager_next_sale_other_id = fields.Many2one("dtdream.sale.own.report",string="主管周报")

    name = fields.Char("详情")

class problem_help(models.Model):
    _name = "problem.help"
    _description = u"问题与求助"

    problem_help_id = fields.Many2one("dtdream.sale.own.report",string="个人周报")
    manager_problem_help_id = fields.Many2one("dtdream.sale.manager.report",string="主管周报")
    name = fields.Char("问题详情")
    type = fields.Many2one('problem.type',string="问题类型")
    report_help_people = fields.Many2many("hr.employee",string="求助对象")


class dtdream_problem_type(models.Model):
    _name = 'problem.type'
    _description = u"问题类型"

    name = fields.Char("问题类型")

class dtdream_sale_manager_report(models.Model):
    _name = 'dtdream.sale.manager.report'
    _description = u"主管周报"

    @api.depends('report_manager')
    def _compute_reportor_info(self):
        self.report_manager_name = self.report_manager.name
        self.job_number = self.report_manager.job_number
        self.department = self.report_manager.department_id.name

    report_manager = fields.Many2one('hr.employee','主管',default=lambda self:self.env['hr.employee'].search([('login','=',self.env.user.login)]))
    report_manager_name = fields.Char(string="主管花名",compute=_compute_reportor_info)
    job_number = fields.Char(string="工号",compute=_compute_reportor_info)
    department = fields.Char(string="部门",compute=_compute_reportor_info)
    week = fields.Integer(string="周别")
    name = fields.Char('主管周报')
    zhengwu_project = fields.One2many("zhengwu.system.project","manager_zhengwu_project_id")
    zhengwu_total_space = fields.Char("项目个数")
    zhengwu_total_project = fields.Float("整体空间(万元)")
    zhengwu_important_project = fields.Char("重大项目个数")
    zhengwu_important_space = fields.Float("重大整体空间(万元)")

    zhengfa_project = fields.One2many("zhengfa.system.project","manager_zhengfa_project_id")
    zhengfa_total_space = fields.Char("项目个数")
    zhengfa_total_project = fields.Float("整体空间(万元)")
    zhengfa_important_project = fields.Char("重大项目个数")
    zhengfa_important_space = fields.Float("重大整体空间(万元)")

    shared_project = fields.One2many("shared.business.project","manager_shared_project_id")
    shared_total_space = fields.Char("项目个数")
    shared_total_project = fields.Float("整体空间(万元)")
    shared_important_project = fields.Char("重大项目个数")
    shared_important_space = fields.Float("重大整体空间(万元)")

    lead_project = fields.One2many("lead.project","manager_lead_project_id")
    sale_channel = fields.One2many("sale.channel","manager_sale_channel_id")
    competitor_situation = fields.One2many("competitor.situation","manager_competitor_situation_id")
    sale_other = fields.One2many("sale.other","manager_sale_other_id")

    dtdream_manager_problem_help = fields.One2many("problem.help","manager_problem_help_id")

    next_zhengwu_project = fields.One2many("zhengwu.system.project","manager_next_zhengwu_project_id")
    next_zhengwu_total_space = fields.Char("项目个数")
    next_zhengwu_total_project = fields.Float("整体空间(万元)")
    next_zhengwu_important_project = fields.Char("重大项目个数")
    next_zhengwu_important_space = fields.Float("重大整体空间(万元)")

    next_zhengfa_project = fields.One2many("zhengfa.system.project","manager_next_zhengfa_project_id")
    next_zhengfa_total_space = fields.Char("项目个数")
    next_zhengfa_total_project = fields.Float("整体空间(万元)")
    next_zhengfa_important_project = fields.Char("重大项目个数")
    next_zhengfa_important_space = fields.Float("重大整体空间(万元)")

    next_shared_project = fields.One2many("shared.business.project","manager_next_shared_project_id")
    next_shared_total_space = fields.Char("项目个数")
    next_shared_total_project = fields.Float("整体空间(万元)")
    next_shared_important_project = fields.Char("重大项目个数")
    next_shared_important_space = fields.Float("重大整体空间(万元)")

    next_sale_other = fields.One2many("sale.other","manager_next_sale_other_id")