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
                if datetime.weekday(datetime.now()) >= 4:
                    report_end_time = datetime.now() - relativedelta(days=((datetime.weekday(datetime.now())) - 4))
                    ref.report_end_time = report_end_time
                else:
                    report_end_time = datetime.now() + relativedelta(days=(4-7-datetime.weekday(datetime.now())))
                    ref.report_end_time = report_end_time
                ref.report_start_time = report_end_time - relativedelta(days=7)
                ref.week = datetime.strftime(datetime.now(),"%W")


                zhengwu_recs = ref.env["crm.lead"].search([('system_department_id.name','=',u"政务系统部"),('bidding_time','>=',datetime.now()),('type','=','opportunity'),('bidding_time','<=',(report_end_time - relativedelta(days=7) + relativedelta(months=3)))])
                zhengfa_recs = ref.env["crm.lead"].search([('system_department_id.name','=',u"政法系统部"),('bidding_time','>=',datetime.now()),('type','=','opportunity'),('bidding_time','<=',(report_end_time - relativedelta(days=7) + relativedelta(months=3)))])
                shared_business_recs = ref.env["crm.lead"].search([('system_department_id.name','=',u"共享业务部"),('bidding_time','>=',datetime.now()),('type','=','opportunity'),('bidding_time','<=',(report_end_time - relativedelta(days=7) + relativedelta(months=3)))])
                list = []
                for rec in zhengwu_recs:
                    str = ""
                    for recc in rec.des_records:
                        if recc.create_date[:10] <= report_end_time.strftime('%Y-%m-%d') and recc.create_date[:10] >= (report_end_time - relativedelta(days=7)).strftime('%Y-%m-%d'):
                            if recc.name != False:
                                str = str + recc.name + u";"
                    project_process = str
                    list.append((0,0,{"project_id":rec.id,"office_id":rec.office_id.name,"sale_apply_id":rec.sale_apply_id.name,"space_total":rec.space_total,
                                          "project_master_degree":rec.project_master_degree,"bidding_time":rec.bidding_time,"project_number":rec.project_number,
                                          "project_process":project_process,'project_leave':rec.project_leave}))
                ref.zhengwu_project = False
                ref.zhengwu_project = list
                alist = []
                for rec in zhengfa_recs:
                    str = ""
                    for recc in rec.des_records:
                        if recc.create_date[:10] <= report_end_time.strftime('%Y-%m-%d') and recc.create_date[:10] >= (report_end_time - relativedelta(days=7)).strftime('%Y-%m-%d'):
                            if recc.name != False:
                                str = str + recc.name + u";"
                    project_process = str
                    alist.append((0,0,{"project_id":rec.id,"office_id":rec.office_id.name,"sale_apply_id":rec.sale_apply_id.name,"space_total":rec.space_total,
                                          "project_master_degree":rec.project_master_degree,"bidding_time":rec.bidding_time,"project_number":rec.project_number,
                                          "project_process":project_process,'project_leave':rec.project_leave}))
                ref.zhengfa_project = False
                ref.zhengfa_project = alist
                blist = []
                for rec in shared_business_recs:
                    str = ""
                    for recc in rec.des_records:
                        if recc.create_date[:10] <= report_end_time.strftime('%Y-%m-%d') and recc.create_date[:10] >= (report_end_time - relativedelta(days=7)).strftime('%Y-%m-%d'):
                            if recc.name != False:
                                str = str + recc.name + u";"
                    project_process = str
                    blist.append((0,0,{"project_id":rec.id,"office_id":rec.office_id.name,"sale_apply_id":rec.sale_apply_id.name,"space_total":rec.space_total,
                                          "project_master_degree":rec.project_master_degree,"bidding_time":rec.bidding_time,"project_number":rec.project_number,
                                          "project_process":project_process,'project_leave':rec.project_leave}))
                ref.shared_project = False
                ref.shared_project = blist

    @api.onchange('zhengwu_project')
    def _onchange_zhengwu_project(self):
        self.zhengwu_total_space = len(self.zhengwu_project)
        zhengwu_space_total = 0
        zhengwu_important_project = 0
        zhengwu_important_space = 0
        for rec in self.zhengwu_project:
            zhengwu_space_total = zhengwu_space_total + rec.project_id.space_total
            if rec.project_id.project_leave in ('company_leave','department_leave'):
                zhengwu_important_project = zhengwu_important_project + 1;
                zhengwu_important_space = zhengwu_important_space + rec.project_id.space_total
        self.zhengwu_total_project = zhengwu_space_total
        self.zhengwu_important_project = zhengwu_important_project
        self.zhengwu_important_space = zhengwu_important_space

    @api.onchange('zhengfa_project')
    def _onchange_zhengfa_project(self):
        self.zhengfa_total_space = len(self.zhengfa_project)
        zhengfa_space_total = 0
        zhengfa_important_project = 0
        zhengfa_important_space = 0
        for rec in self.zhengfa_project:
            zhengfa_space_total = zhengfa_space_total + rec.project_id.space_total
            if rec.project_id.project_leave in ('company_leave','department_leave'):
                zhengfa_important_project = zhengfa_important_project + 1;
                zhengfa_important_space = zhengfa_important_space + rec.project_id.space_total
        self.zhengfa_total_project = zhengfa_space_total
        self.zhengfa_important_project = zhengfa_important_project
        self.zhengfa_important_space = zhengfa_important_space

    @api.onchange('shared_project')
    def _onchange_shared_project(self):
        self.shared_total_space = len(self.shared_project)
        shared_space_total = 0
        shared_important_project = 0
        shared_important_space = 0
        for rec in self.shared_project:
            shared_space_total = shared_space_total + rec.project_id.space_total
            if rec.project_id.project_leave in ('company_leave','department_leave'):
                shared_important_project = shared_important_project + 1;
                shared_important_space = shared_important_space + rec.project_id.space_total
        self.shared_total_project = shared_space_total
        self.shared_important_project = shared_important_project
        self.shared_important_space = shared_important_space

    @api.multi
    def btn_submit(self):
        self.write({'state':'submit'})
        if len(self.zhengwu_project) > 0 :
            for rec in self.zhengwu_project:
                if rec.project_process != False:
                    crm_rec = self.env['crm.lead'].search([('project_number','=',rec.project_number)])[0]
                    crm_rec.des_records.create({"name":rec.project_process,"des_id":crm_rec.id})
        if len(self.zhengfa_project) > 0 :
            for rec in self.zhengfa_project:
                if rec.project_process != False:
                    crm_rec = self.env['crm.lead'].search([('project_number','=',rec.project_number)])[0]
                    crm_rec.des_records.create({"name":rec.project_process,"des_id":crm_rec.id})
        if len(self.shared_project) > 0 :
            for rec in self.shared_project:
                if rec.project_process != False:
                    crm_rec = self.env['crm.lead'].search([('project_number','=',rec.project_number)])[0]
                    crm_rec.des_records.create({"name":rec.project_process,"des_id":crm_rec.id})


    report_person = fields.Many2one('hr.employee','报告人',default=lambda self:self.env['hr.employee'].search([('login','=',self.env.user.login)]))
    report_person_name = fields.Char(string="报告人花名",compute=_compute_reportor_info)
    job_number = fields.Char(string="工号",compute=_compute_reportor_info,store=True)
    department = fields.Char(string="部门",compute=_compute_reportor_info,store=True)
    week = fields.Integer(string="周别")

    name = fields.Char('个人周报',default="个人周报")
    report_start_time = fields.Date(string="周报开始日期")
    report_end_time = fields.Date(string="周报结束日期")
    zhengwu_project = fields.One2many("zhengwu.system.project","zhengwu_project_id",copy=True)
    zhengwu_total_space = fields.Char("项目个数")
    zhengwu_total_project = fields.Float("整体空间(万元)")
    zhengwu_important_project = fields.Char("重大项目个数")
    zhengwu_important_space = fields.Float("重大整体空间(万元)")

    zhengfa_project = fields.One2many("zhengfa.system.project","zhengfa_project_id")
    zhengfa_total_space = fields.Char("项目个数")
    zhengfa_total_project = fields.Float("整体空间(万元)")
    zhengfa_important_project = fields.Char("重大项目个数")
    zhengfa_important_space = fields.Float("重大整体空间(万元)")

    shared_project = fields.One2many("shared.business.project","shared_project_id")
    shared_total_space = fields.Char("项目个数")
    shared_total_project = fields.Float("整体空间(万元)")
    shared_important_project = fields.Char("重大项目个数")
    shared_important_space = fields.Float("重大整体空间(万元)")

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

    # 新建时更新项目进展
    # @api.model
    # def create(self, vals):
    #     result = super(dtdream_sale_own_report, self).create(vals)
    #     if len(result.zhengwu_project) > 0 :
    #         for rec in result.zhengwu_project:
    #             if rec.add_project_process != False:
    #                 crm_rec = self.env['crm.lead'].search([('project_number','=',rec.project_number)])[0]
    #                 crm_rec.des_records.create({"name":rec.add_project_process,"des_id":crm_rec.id})
    #                 rec.project_process = rec.add_project_process + ";" + rec.project_process
    #                 rec.add_project_process = False
    #     return result

    # @api.multi
    # def write(self, vals):
    #     if vals.has_key('zhengwu_project'):
    #         for rec in vals['zhengwu_project']:
    #             if rec[2] != False:
    #                 process_rec = self.env['zhengwu.system.project'].search([('id','=',rec[1])])[0]
    #                 if rec[2].get('add_project_process',False) != False:
    #                     crm_rec = self.env['crm.lead'].search([('project_number','=',process_rec.project_number)])[0]
    #                     crm_rec.des_records.create({"name":rec[2].get('add_project_process'),"des_id":crm_rec.id})
    #                     rec[2]['project_process'] = rec[2].get('add_project_process') + ";" + process_rec.project_process
    #                     rec[2]['add_project_process'] = False
    #     result = super(dtdream_sale_own_report, self).write(vals)
    #     return result

# 政务系统部项目
class zhengwu_system_project(models.Model):
    _name = 'zhengwu.system.project'
    _description = u"政务系统部项目"

    zhengwu_project_id = fields.Many2one("dtdream.sale.own.report",string="个人周报")
    manager_zhengwu_project_id = fields.Many2one("dtdream.sale.own.report",string="主管周报")
    next_zhengwu_project_id = fields.Many2one("dtdream.sale.own.report",string="个人周报")
    manager_next_zhengwu_project_id = fields.Many2one("dtdream.sale.own.report",string="主管周报")

    @api.onchange('project_id')
    def _onchange_project_info(self):
        for rec in self:
            rec.office_id = rec.project_id.office_id.name
            rec.sale_apply_id = rec.project_id.sale_apply_id.name
            rec.space_total = rec.project_id.space_total
            rec.project_master_degree = rec.project_id.project_master_degree
            rec.bidding_time = rec.project_id.bidding_time
            rec.project_number = rec.project_id.project_number
            rec.project_leave = rec.project_id.project_leave
            if datetime.weekday(datetime.now()) >= 4:
                report_end_time = datetime.now() - relativedelta(days=((datetime.weekday(datetime.now())) - 4))
            else:
                report_end_time = datetime.now() + relativedelta(days=(4-7-datetime.weekday(datetime.now())))
            str = ""
            for recc in rec.project_id.des_records:
                if recc.create_date[:10] <= report_end_time.strftime('%Y-%m-%d') and recc.create_date[:10] >= (report_end_time - relativedelta(days=7)).strftime('%Y-%m-%d'):
                    if recc.name != False:
                        str = str + recc.name + u";"
            rec.project_process = str


    office_id = fields.Char(string="办事处")
    project_id = fields.Many2one('crm.lead',string="项目名称")
    sale_apply_id = fields.Char(string="营销责任人")
    space_total = fields.Float(string="项目空间")
    project_master_degree = fields.Selection([
        ('1', 'A'),
        ('2', 'B'),
        ('3', 'C'),
        ('4', 'D'),
    ],'项目把握度')
    bidding_time = fields.Char(string="预计投标日期")
    project_process = fields.Text(string="上周项目进展")
    next_process = fields.Text(string="下周项目计划")
    project_number = fields.Char(string="项目编号")
    project_leave = fields.Char(string="项目级别")

class zhengfa_system_project(models.Model):
    _name = 'zhengfa.system.project'
    _description = u"政法系统部项目"

    @api.onchange('project_id')
    def _compute_project_info(self):
        for rec in self:
            rec.office_id = rec.project_id.office_id.name
            rec.sale_apply_id = rec.project_id.sale_apply_id.name
            rec.space_total = rec.project_id.space_total
            rec.project_master_degree = rec.project_id.project_master_degree
            rec.bidding_time = rec.project_id.bidding_time
            rec.project_number = rec.project_id.project_number
            rec.project_leave = rec.project_id.project_leave
            if datetime.weekday(datetime.now()) >= 4:
                report_end_time = datetime.now() - relativedelta(days=((datetime.weekday(datetime.now())) - 4))
            else:
                report_end_time = datetime.now() + relativedelta(days=(4-7-datetime.weekday(datetime.now())))
            str = ""
            for recc in rec.project_id.des_records:
                if recc.create_date[:10] <= report_end_time.strftime('%Y-%m-%d') and recc.create_date[:10] >= (report_end_time - relativedelta(days=7)).strftime('%Y-%m-%d'):
                    if recc.name != False:
                        str = str + recc.name + u";"
            rec.project_process = str

    zhengfa_project_id = fields.Many2one("dtdream.sale.own.report",string="个人周报")
    manager_zhengfa_project_id = fields.Many2one("dtdream.sale.own.report",string="主管周报")
    next_zhengfa_project_id = fields.Many2one("dtdream.sale.own.report",string="个人周报")
    manager_next_zhengfa_project_id = fields.Many2one("dtdream.sale.own.report",string="主管周报")

    office_id = fields.Char(string="办事处")
    project_id = fields.Many2one('crm.lead',string="项目名称")
    sale_apply_id = fields.Char(string="营销责任人")
    space_total = fields.Float(string="项目空间")
    project_master_degree = fields.Selection([
        ('1', 'A'),
        ('2', 'B'),
        ('3', 'C'),
        ('4', 'D'),
    ],'项目把握度')
    bidding_time = fields.Char(string="预计投标日期")
    project_process = fields.Text(string="上周项目进展")
    next_process = fields.Text(string="下周项目计划")
    project_number = fields.Char(string="项目编号")
    project_leave = fields.Char(string="项目级别")

class shared_business_project(models.Model):
    _name = 'shared.business.project'
    _description = u"共享业务部"

    @api.onchange('project_id')
    def _compute_project_info(self):
        for rec in self:
            rec.office_id = rec.project_id.office_id.name
            rec.sale_apply_id = rec.project_id.sale_apply_id.name
            rec.space_total = rec.project_id.space_total
            rec.project_master_degree = rec.project_id.project_master_degree
            rec.bidding_time = rec.project_id.bidding_time
            rec.project_number = rec.project_id.project_number
            rec.project_leave = rec.project_id.project_leave
            if datetime.weekday(datetime.now()) >= 4:
                report_end_time = datetime.now() - relativedelta(days=((datetime.weekday(datetime.now())) - 4))
            else:
                report_end_time = datetime.now() + relativedelta(days=(4-7-datetime.weekday(datetime.now())))
            str = ""
            for recc in rec.project_id.des_records:
                if recc.create_date[:10] <= report_end_time.strftime('%Y-%m-%d') and recc.create_date[:10] >= (report_end_time - relativedelta(days=7)).strftime('%Y-%m-%d'):
                    if recc.name != False:
                        str = str + recc.name + u";"
            rec.project_process = str

    shared_project_id = fields.Many2one("dtdream.sale.own.report",string="个人周报")
    manager_shared_project_id = fields.Many2one("dtdream.sale.own.report",string="主管周报")
    next_shared_project_id = fields.Many2one("dtdream.sale.own.report",string="个人周报")
    manager_next_shared_project_id = fields.Many2one("dtdream.sale.own.report",string="主管周报")
    office_id = fields.Char(string="办事处")
    project_id = fields.Many2one('crm.lead',string="项目名称")
    sale_apply_id = fields.Char(string="营销责任人")
    space_total = fields.Float(string="项目空间")
    project_master_degree = fields.Selection([
        ('1', 'A'),
        ('2', 'B'),
        ('3', 'C'),
        ('4', 'D'),
    ],'项目把握度')
    bidding_time = fields.Char(string="预计投标日期")
    project_process = fields.Text(string="上周项目进展")
    next_process = fields.Text(string="下周项目计划")
    project_number = fields.Char(string="项目编号")
    project_leave = fields.Char(string="项目级别")


# 重大机会点
class lead_project(models.Model):
    _name = 'lead.project'
    _description = u"重大机会点"

    lead_project_id = fields.Many2one("dtdream.sale.own.report",string="个人周报")
    manager_lead_project_id = fields.Many2one("dtdream.sale.own.report",string="主管周报")

    @api.onchange('project_id')
    def _compute_project_info(self):
        for rec in self:
            rec.office_id = rec.project_id.office_id.name
            rec.sale_apply_id = rec.project_id.sale_apply_id.name
            rec.space_total = rec.project_id.space_total
            rec.project_master_degree = rec.project_id.project_master_degree
            rec.bidding_time = rec.project_id.bidding_time
            rec.project_number = rec.project_id.project_number
            if datetime.weekday(datetime.now()) >= 4:
                report_end_time = datetime.now() - relativedelta(days=((datetime.weekday(datetime.now())) - 4))
            else:
                report_end_time = datetime.now() + relativedelta(days=(4-7-datetime.weekday(datetime.now())))
            str = ""
            for recc in rec.project_id.des_records:
                if recc.create_date[:10] <= report_end_time.strftime('%Y-%m-%d') and recc.create_date[:10] >= (report_end_time - relativedelta(days=7)).strftime('%Y-%m-%d'):
                    if recc.name != False:
                        str = str + recc.name + u";"
            rec.project_process = str

    office_id = fields.Char(string="办事处")
    project_id = fields.Many2one('crm.lead',string="项目名称")
    sale_apply_id = fields.Char(string="营销责任人")
    space_total = fields.Float(string="项目空间")
    project_master_degree = fields.Selection([
        ('1', 'A'),
        ('2', 'B'),
        ('3', 'C'),
        ('4', 'D'),
    ],'项目把握度')
    bidding_time = fields.Char(string="预计投标日期")
    project_process = fields.Text(string="项目进展")
    project_number = fields.Char(string="项目编号")


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