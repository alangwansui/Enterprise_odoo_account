# -*- coding: utf-8 -*-

from openerp import models, fields, api
from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp.exceptions import ValidationError
from openerp.osv import expression
from openerp.exceptions import AccessError

class dtdream_sale_own_report(models.Model):
    _name = 'dtdream.sale.own.report'
    _description = u"个人周报"
    _order = "report_start_time desc"

    @api.multi
    def read(self, fields=None, load='_classic_read'):
        domain = self.get_access_domain(domain=[])
        access_records = [rec.id for rec in self.sudo().search(domain)]
        for record in self:
            if record.id not in access_records:
                raise AccessError(u"您无权限访问该记录。")
        return super(dtdream_sale_own_report, self).read(fields=fields, load=load)

    def get_access_domain(self,domain):
        ex_domain = [("create_uid",'=',self._uid)]
        ex_domain = expression.OR([['&',("department",'in',[x.name for x in self.env.user.user_access_department]),('state','=','submit')],ex_domain])
        if self.user_has_groups('dtdream_sale.group_dtdream_sale_high_manager') or self.user_has_groups('dtdream_sale.group_dtdream_weekly_report_manager') or self.user_has_groups('dtdream_sale.group_dtdream_company_manager') or self.user_has_groups('dtdream_sale.group_dtdream_market_manager'):
                ex_domain = []
        return expression.AND([ex_domain,domain])

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        domain = self.get_access_domain(domain)
        return super(dtdream_sale_own_report, self).search_read(domain=domain, fields=fields, offset=offset,
                                                           limit=limit, order=order)
    state = fields.Selection(
        [('0', '草稿'),
         ('submit', '已提交')], string="状态", default="0",track_visibility='onchange')

    @api.model
    def default_get(self,fields):
        report_person = self.env['hr.employee'].search([('login','=',self.env.user.login)])
        if not (report_person.name and report_person.full_name and report_person.job_number):
            raise ValidationError("请先完成员工与用户的关联。")
        res = super(dtdream_sale_own_report, self).default_get(fields)
        return res

    @api.depends('report_person')
    def _compute_reportor_info(self):
        for ref in self:
            ref.report_person_name = ref.report_person.name+"."+ref.report_person.full_name+"  "+ref.report_person.job_number
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
                ref.week = int(datetime.strftime(report_end_time,"%W"))
                ref.compute_project_info(report_end_time)

    def compute_project_info(self,report_end_time):
        if report_end_time:
            zhengwu_recs = self.env["crm.lead"].search([('stage_id.name','in',(u'项目启动',u'技术和商务交流',u'项目招投标')),('sale_apply_id.user_id.id','=',self._uid),('type','=','opportunity'),('bidding_time','<=',(report_end_time + relativedelta(months=3)))], order="system_department_id desc")
            list = []
            for rec in zhengwu_recs:
                str = ""
                for recc in rec.des_records:
                    if recc.create_date[:10] <= report_end_time.strftime('%Y-%m-%d') and recc.create_date[:10] > (report_end_time - relativedelta(days=7)).strftime('%Y-%m-%d'):
                        if recc.name != False and recc.week != int(self.week):
                            str = str + recc.name + u";"
                project_process = str
                list.append((0,0,{"project_id":rec.id,"office_id":rec.office_id,"sale_apply_id":rec.sale_apply_id.name+"."+rec.sale_apply_id.full_name+" "+rec.sale_apply_id.job_number,"space_total":rec.space_total,
                                      "project_master_degree":rec.project_master_degree,"bidding_time":rec.bidding_time,"project_number":rec.project_number,
                                      "project_process":project_process,'project_leave':rec.project_leave,'system_department_id':rec.system_department_id,'industry_id':rec.industry_id}))
            self.zhengwu_project = False
            self.zhengwu_project = list
            lead_recs = self.env["crm.lead"].search([('sale_apply_id.user_id.id','=',self._uid),('type','=','lead'),('bidding_time','<=',(report_end_time + relativedelta(months=3)))], order="system_department_id desc")
            alist = []
            for reca in lead_recs:
                str = ""
                for recc in reca.des_records:
                    if recc.create_date[:10] <= report_end_time.strftime('%Y-%m-%d') and recc.create_date[:10] > (report_end_time - relativedelta(days=7)).strftime('%Y-%m-%d'):
                        if recc.name != False and recc.week != int(self.week):
                            str = str + recc.name + u";"
                a_project_process = str
                alist.append((0,0,{"project_id":reca.id,"office_id":reca.office_id,"sale_apply_id":reca.sale_apply_id.name+"."+reca.sale_apply_id.full_name+" "+reca.sale_apply_id.job_number,"space_total":reca.space_total,
                                      "project_master_degree":reca.project_master_degree,"bidding_time":reca.bidding_time,"project_number":reca.project_number,
                                      "project_process":a_project_process,'project_leave':reca.project_leave,'system_department_id':reca.system_department_id,'industry_id':reca.industry_id}))
            self.lead_project = False
            self.lead_project = alist

    @api.onchange("week")
    @api.depends("week")
    def _onchange_week(self):
        if datetime.weekday(datetime.now()) >= 4:
            report_end_time = datetime.now() - relativedelta(days=((datetime.weekday(datetime.now())) - 4))
            report_end_time = report_end_time
        else:
            report_end_time = datetime.now() + relativedelta(days=(4-7-datetime.weekday(datetime.now())))
            report_end_time = report_end_time
        report_start_time = report_end_time - relativedelta(days=7)
        week = int(datetime.strftime(report_end_time,"%W"))
        self.report_start_time = report_start_time
        a_report_end_time = report_end_time - relativedelta(days=(week-int(self.week.name))*7)
        self.report_end_time = a_report_end_time
        self.report_start_time = report_start_time - relativedelta(days=(week-int(self.week.name))*7)
        try:
            self.id - self.id
        except:
            self.compute_project_info(a_report_end_time)

    @api.onchange('to_compute_zongjie')
    def _onchange_zhengwu_project(self):
        zhengwu_project_total = 0
        zhengwu_space_total = 0
        zhengwu_important_project = 0
        zhengwu_important_space = 0
        leads_project_total = 0
        leads_space_total = 0
        leads_important_project = 0
        leads_important_space = 0
        week_add_spaces = 0
        monthly_lead_project_totals = 0
        weekly_project_totals = 0
        sys_list = []
        projects_in_operation = self.env['crm.lead'].search([('sale_apply_id.user_id.id','=',self._uid),('stage_id.name','in',('项目启动','技术和商务交流','项目招投标'))])
        for rec in projects_in_operation:
            if rec.id != False:
                zhengwu_project_total = zhengwu_project_total +1
            if rec.system_department_id not in sys_list and rec.id != False:
                sys_list.append(rec.system_department_id)
            zhengwu_space_total = zhengwu_space_total + rec.space_total
            if rec.project_leave in ('company_leave','department_leave'):
                zhengwu_important_project = zhengwu_important_project + 1;
                zhengwu_important_space = zhengwu_important_space + rec.space_total
            if rec.create_date:
                if rec.create_date[:10] > self.report_start_time and rec.create_date[:10] <= self.report_end_time:
                    week_add_spaces = week_add_spaces + rec.space_total
            if rec.write_date:
                if rec.write_date[:10] > self.report_start_time and rec.write_date[:10] <= self.report_end_time:
                    weekly_project_totals = weekly_project_totals + 1
        projects_in_lead_stage = self.env['crm.lead'].search([('sale_apply_id.user_id.id','=',self._uid),('stage_id.name','=','机会点')])
        for recc in projects_in_lead_stage:
            if recc.id != False:
                leads_project_total = leads_project_total +1
            if recc.system_department_id not in sys_list and recc.id != False:
                sys_list.append(recc.system_department_id)
            leads_space_total = leads_space_total + recc.space_total
            if recc.project_leave in ('company_leave','department_leave'):
                leads_important_project = leads_important_project + 1;
                leads_important_space = leads_important_space + recc.space_total
            if recc.create_date:
                if recc.create_date[:10] > self.report_start_time and recc.create_date[:10] <= self.report_end_time:
                    week_add_spaces = week_add_spaces + recc.space_total
            if recc.write_date:
                if recc.write_date[:10] >= (datetime.strptime(self.report_end_time+ " 00:00:00","%Y-%m-%d %H:%M:%S") - relativedelta(months=1)).strftime('%Y-%m-%d'):
                    monthly_lead_project_totals = monthly_lead_project_totals + 1
        sys_compute_list = []
        for sys_name in sys_list:
            project_total = 0
            lead_project_total = 0
            space_total = 0
            important_project = 0
            important_space = 0
            lead_important_project = 0
            lead_important_space = 0
            lead_space_total = 0
            week_new_space = 0
            weekly_project_total = 0
            monthly_lead_project_total = 0
            for rec in projects_in_operation:
                if rec.system_department_id == sys_name and rec.id != False:
                    project_total = project_total + 1
                    space_total = space_total + rec.space_total
                    if rec.project_leave in ('company_leave','department_leave'):
                        important_project = important_project + 1;
                        important_space = important_space + rec.space_total
                    if rec.create_date:
                        if rec.create_date[:10] > self.report_start_time and rec.create_date[:10] <= self.report_end_time:
                            week_new_space = week_new_space + rec.space_total
                    if rec.write_date:
                        if rec.write_date[:10] > self.report_start_time and rec.write_date[:10] <= self.report_end_time:
                            weekly_project_total = weekly_project_total + 1
            for lead_rec in projects_in_lead_stage:
                if lead_rec.system_department_id == sys_name and lead_rec.id != False:
                    lead_project_total = lead_project_total + 1
                    lead_space_total = lead_space_total + lead_rec.space_total
                    if lead_rec.project_leave in ('company_leave','department_leave'):
                        lead_important_project = lead_important_project + 1;
                        lead_important_space = lead_important_space + lead_rec.space_total
                    if lead_rec.create_date:
                        if lead_rec.create_date[:10] > self.report_start_time and lead_rec.create_date[:10] <= self.report_end_time:
                            week_new_space = week_new_space + lead_rec.space_total
                    if lead_rec.write_date:
                        if lead_rec.write_date[:10] >= (datetime.strptime(self.report_end_time+ " 00:00:00","%Y-%m-%d %H:%M:%S") - relativedelta(months=1)).strftime('%Y-%m-%d'):
                            monthly_lead_project_total = monthly_lead_project_total + 1
            if lead_project_total != 0:
                monthly_laed_refresh_rate = float(monthly_lead_project_total)/lead_project_total*100
            else:
                monthly_laed_refresh_rate = 0
            if project_total != 0:
                weekly_refresh_rate = float(weekly_project_total)/project_total*100
            else:
                weekly_refresh_rate = 0
            sys_compute_list.append({"project_total":(project_total+lead_project_total),"weekly_refresh_rate":weekly_refresh_rate,"monthly_laed_refresh_rate":monthly_laed_refresh_rate,"week_new_space":week_new_space,"project_count":space_total+lead_space_total,"space_total":space_total,"important_project":important_project,"important_space":important_space,"system_name":sys_name.name,"lead_project_total":lead_project_total,"lead_space_total":lead_space_total,"lead_important_project":lead_important_project,"lead_important_space":lead_important_space})
        if zhengwu_project_total != 0:
            weekly_refresh_rate = float(weekly_project_totals)/(zhengwu_project_total)*100
        else:
            weekly_refresh_rate = 0
        if leads_project_total != 0:
            monthly_laed_refresh_rate = float(monthly_lead_project_totals)/(leads_project_total)*100
        else:
            monthly_laed_refresh_rate = 0
        if len(sys_compute_list) > 0:
            self.project_total = zhengwu_project_total+leads_project_total
            self.weekly_refresh_rate = weekly_refresh_rate
            self.monthly_laed_refresh_rate = monthly_laed_refresh_rate
            self.week_new_space = week_new_space
            self.project_count = zhengwu_space_total+leads_space_total
            self.space_total = zhengwu_space_total
            self.lead_space_total = leads_space_total

        if len(self.sys_compute_lists)>0:
            for sys_record in self.sys_compute_lists:
                for sys_rec in sys_compute_list:
                    if sys_rec["system_name"] == sys_record.system_name:
                        sys_rec["bid_amount"] = sys_record.bid_amount
                        sys_rec["contract_signing_amount"] = sys_record.contract_signing_amount
                        sys_rec["received"] = sys_record.received
                        sys_rec["accounts_payable"] = sys_record.accounts_payable
            self.write({'sys_compute_lists':[(6,0,[])]})
        self.sys_compute_lists = sys_compute_list

    @api.multi
    def btn_submit(self):
        self.write({'state':'submit','submit_date':datetime.now()})
        if self.env['hr.employee'].search([('login','=',self.create_uid.login)]).department_id.parent_id.id:
            department_name = self.env['hr.employee'].search([('login','=',self.create_uid.login)]).department_id.name
            real_department = self.env['hr.department'].search([('name','=',department_name),('parent_id.name','=',u'市场部')])
            manager_id = real_department.manager_id
            assitant_id = real_department.assitant_id
            if len(manager_id) > 0:
                self.dtdream_send_submit_mail(u"{0}于{1}提交了第{2}周个人周报,请您查阅!".format(self.env['hr.employee'].search([('login','=',self.create_uid.login)]).name, self.create_date[:10],self.week.name),
                               u"%s提交了第%s周个人周报,等待您查阅批复" %(self.env['hr.employee'].search([('login','=',self.create_uid.login)]).name,self.week.name), email_to=manager_id.work_email,
                               appellation = u'{0},您好：'.format(manager_id.name))
            if len(assitant_id) > 0:
                self.dtdream_send_submit_mail(u"{0}于{1}提交了第{2}周个人周报,请您查阅!".format(self.env['hr.employee'].search([('login','=',self.create_uid.login)]).name, self.create_date[:10],self.week.name),
                               u"%s提交了第%s周个人周报,等待您查阅批复" %(self.env['hr.employee'].search([('login','=',self.create_uid.login)]).name,self.week.name), email_to=assitant_id.work_email,
                               appellation = u'{0},您好：'.format(assitant_id.name))
        if len(self.visit_customer) > 0:
            person_list = []
            arr = {}
            for rec in self.visit_customer:
                for person in rec.send_person:
                    if person.name not in person_list:
                        person_list.append(person.name)
                        arr[person.name] = [{"partner_id":rec.partner_id.name,"system_department_id":rec.system_department_id.name,"office_id":rec.office_id.name,"industry_id":rec.industry_id.name,"visit_date":rec.visit_date,"visit_object":rec.visit_object,"content":rec.content,"next_plan":rec.next_plan,"ask_help":rec.ask_help,"work_email":person.work_email}]
                    else:
                        arr[person.name].append({"partner_id":rec.partner_id.name,"system_department_id":rec.system_department_id.name,"office_id":rec.office_id.name,"industry_id":rec.industry_id.name,"visit_date":rec.visit_date,"visit_object":rec.visit_object,"content":rec.content,"next_plan":rec.next_plan,"ask_help":rec.ask_help,"work_email":person.work_email})
            for rec in arr:
                body_html = u"""<table border="1px" width="800px" style="border-collapse: collapse;"><thead>
                                <th>客户名称</th>
                                <th>系统部</th>
                                <th>办事处</th>
                                <th>行业</th>
                                <th>拜访时间</th>
                                <th>拜访对象</th>
                                <th width="20%">交流主要内容</th>
                                <th width="20%">下一步计划</th>
                                <th width="25%">困难求助</th>
                                </thead><tbody>"""
                for a_rec in arr[rec]:
                    work_email = a_rec['work_email']
                    body_html = body_html + u"<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>"%(a_rec['partner_id'],a_rec['system_department_id'],a_rec['office_id'],a_rec['industry_id'],a_rec['visit_date'],a_rec['visit_object'],a_rec['content'],a_rec['next_plan'],a_rec['ask_help'])
                body_html = body_html + u"</tbody></table>"
                self.dtdream_send_mail(u"{0}于{1}提交了个人周报,并向您发起困难求助!".format(self.env['hr.employee'].search([('login','=',self.create_uid.login)]).name, self.create_date[:10]),
                   u"%s提交了个人周报,并就以下困难向您求助" % self.env['hr.employee'].search([('login','=',self.create_uid.login)]).name, email_to=work_email,email_from=self.env['hr.employee'].search([('login','=',self.create_uid.login)]).work_email,reply_to=self.env['hr.employee'].search([('login','=',self.create_uid.login)]).work_email,
                   appellation = u'{0},您好：'.format(rec),body_html = body_html)

        if len(self.dtdream_problem_help) > 0:
            person_list = []
            arr = {}
            for rec in self.dtdream_problem_help:
                for person in rec.report_help_people:
                    if person.name not in person_list:
                        person_list.append(person.name)
                        arr[person.name] = [{"type":rec.type.name,"name":rec.name,"work_email":person.work_email}]
                    else:
                        arr[person.name].append({"type":rec.type.name,"name":rec.name,"work_email":person.work_email})
            for rec in arr:
                body_html = u"""<table border="1px" width="600px"  style="border-collapse: collapse;"><thead>
                                <th width="30%">问题类型</th>
                                <th width="70%">问题详情</th>
                                </thead><tbody>"""
                for a_rec in arr[rec]:
                    work_email = a_rec['work_email']
                    body_html = body_html + u"<tr><td>%s</td><td>%s</td></tr>"%(a_rec['type'],a_rec['name'])
                body_html = body_html + u"</tbody></table>"
                self.dtdream_send_mail(u"{0}于{1}提交了个人周报,并向您发起问题求助!".format(self.env['hr.employee'].search([('login','=',self.create_uid.login)]).name, self.create_date[:10]),
                   u"%s提交了个人周报,并就以下问题向您求助" % self.env['hr.employee'].search([('login','=',self.create_uid.login)]).name, email_to=work_email,email_from=self.env['hr.employee'].search([('login','=',self.create_uid.login)]).work_email,reply_to=self.env['hr.employee'].search([('login','=',self.create_uid.login)]).work_email,
                   appellation = u'{0},您好：'.format(rec),body_html = body_html)

    def domain_week(self):
        if datetime.weekday(datetime.now()) >= 4:
            report_end_time = datetime.now() - relativedelta(days=((datetime.weekday(datetime.now())) - 4))
        else:
            report_end_time = datetime.now() + relativedelta(days=(4-7-datetime.weekday(datetime.now())))
        end_week = datetime.strftime(report_end_time,"%W")
        start_week = int(end_week) - 3
        return [('id','>=',start_week),('id','<=',end_week)]


    to_compute_zongjie = fields.Char(string="隐藏字段，用于计算空间情况总结")
    project_total = fields.Integer(string="项目个数")
    lead_space_total = fields.Integer(string="机会点空间(万元)")
    week_new_space = fields.Integer(string="本周新增项目空间(万元)")
    space_total = fields.Integer(string="项目空间(万元)")
    project_count = fields.Integer(string="小计(万元)")
    weekly_refresh_rate = fields.Integer("项目周刷新率(%)")
    monthly_laed_refresh_rate = fields.Integer("机会点月刷新率(%)")
    bid_amount = fields.Integer(string="中标金额(万元)")
    contract_signing_amount = fields.Integer(string="合同签订额(万元)")
    received = fields.Integer(string="已收款(万元)")
    accounts_payable = fields.Integer(string="应付款(万元)")
    bid_amount = fields.Integer(string="中标金额(万元)")
    contract_signing_amount = fields.Integer(string="合同签订额(万元)")
    received = fields.Integer(string="已收款(万元)")
    accounts_payable = fields.Integer(string="应付款(万元)")
    submit_date = fields.Datetime(string="提交时间")

    report_person = fields.Many2one('hr.employee','报告人',default=lambda self:self.env['hr.employee'].search([('login','=',self.env.user.login)]))
    report_person_name = fields.Char(string="报告人",compute=_compute_reportor_info,store=True)
    job_number = fields.Char(string="工号",compute=_compute_reportor_info,store=True)
    department = fields.Char(string="部门",compute=_compute_reportor_info,store=True)
    week = fields.Many2one("report.week",string="周别",help="默认为当前周，可往前取三周。",domain=domain_week)

    name = fields.Char('个人周报',default="个人周报")
    report_start_time = fields.Date(string="周报开始日期",compute=_onchange_week,store=True)
    report_end_time = fields.Date(string="周报结束日期",compute=_onchange_week,store=True)
    zhengwu_project = fields.One2many("zhengwu.system.project","zhengwu_project_id")
    zhengwu_total_space = fields.Char("项目个数")
    zhengwu_total_project = fields.Float("整体空间(万元)")
    zhengwu_important_project = fields.Char("重大项目个数")
    zhengwu_important_space = fields.Float("重大整体空间(万元)")

    lead_project = fields.One2many("lead.project","lead_project_id")
    other_project = fields.One2many("other.project","other_project_id")
    sale_channel = fields.One2many("sale.channel","sale_channel_id")
    visit_customer = fields.One2many("visit.customer","visit_customer_id")
    competitor_situation = fields.One2many("competitor.situation","competitor_situation_id")
    sale_other = fields.One2many("sale.other","sale_other_id")

    dtdream_problem_help = fields.One2many("problem.help","problem_help_id")

    next_zhengwu_project = fields.One2many("zhengwu.system.project","next_zhengwu_project_id")

    customer_visit_plan = fields.One2many("customer.visit.plan","customer_visit_plan_id")

    next_sale_other = fields.One2many("sale.other","next_sale_other_id")
    sys_compute_lists = fields.One2many("sys.list","rec_id",string="系统部列表")

    reply_list = fields.One2many("reply.list","reply_list_to_own_report_id",string="周报批复区")

    @api.constrains("sys_compute_lists")
    def _cons_sys_compute_lists(self):
        self._onchange_compute_total()

    @api.onchange("sys_compute_lists")
    def _onchange_compute_total(self):
        bid_amount_total = 0
        contract_signing_amount_total = 0
        received_total = 0
        accounts_payable_total = 0
        for rec in self.sys_compute_lists:
            if rec.system_name != u"合计":
                bid_amount_total = bid_amount_total + rec.bid_amount
                contract_signing_amount_total = contract_signing_amount_total + rec.contract_signing_amount
                received_total = received_total + rec.received
                accounts_payable_total = accounts_payable_total + rec.accounts_payable
        if bid_amount_total > 0 :
            self.bid_amount = bid_amount_total
            self.contract_signing_amount = contract_signing_amount_total
            self.received = received_total
            self.accounts_payable = accounts_payable_total

    @api.constrains("week")
    def _cons_week(self):
        if len(self.env['dtdream.sale.own.report'].search([('id','!=',self.id),('report_person_name','=',self.report_person_name),('week','=',self.week.id)])) > 0:
            raise ValidationError("每周只能生成一份周报。")
        if datetime.weekday(datetime.now()) >= 4:
            report_end_time = datetime.now() - relativedelta(days=((datetime.weekday(datetime.now())) - 4))
            report_end_time = report_end_time
        else:
            report_end_time = datetime.now() + relativedelta(days=(4-7-datetime.weekday(datetime.now())))
            report_end_time = report_end_time
        report_start_time = report_end_time - relativedelta(days=7)
        week = int(datetime.strftime(report_end_time,"%W"))
        for rec in self:
            rec.report_start_time = report_start_time
            a_report_end_time = report_end_time - relativedelta(days=(week-int(rec.week.name))*7)
            rec.report_end_time = a_report_end_time
            rec.report_start_time = report_start_time - relativedelta(days=(week-int(rec.week.name))*7)

    @api.constrains('zhengwu_project')
    def _cons_zhengwu_project(self):
        list = []
        for rec in self.zhengwu_project:
            if rec.project_id:
                if rec.project_id.id in list:
                    raise ValidationError("近三个月招投标项目重复录入。")
            list.append(rec.project_id.id)
            if len(rec.office_id) == 0:
                rec.project_master_degree = rec.project_id.project_master_degree
                rec.bidding_time = rec.project_id.bidding_time
            rec.system_department_id = rec.project_id.system_department_id
            rec.office_id = rec.project_id.office_id
            if rec.project_id:
                rec.sale_apply_id = rec.project_id.sale_apply_id.name+"."+rec.project_id.sale_apply_id.full_name+" "+rec.project_id.sale_apply_id.job_number
            rec.space_total = rec.project_id.space_total
            rec.industry_id = rec.project_id.industry_id
            report_end_time = self.report_end_time + " 00:00:00"
            if len(rec.project_id) == 0:
                self.zhengwu_project = [(2,rec.id)]
            if rec.project_id.project_number:
                crm_recs = self.env['crm.lead'].search([('project_number','=',rec.project_id.project_number)])
                if crm_recs is None or len(crm_recs) <= 0:
                    return
                crm_rec = crm_recs[0]
                if crm_rec.project_master_degree != rec.project_master_degree:
                    crm_rec.write({"project_master_degree":rec.project_master_degree})
                if crm_rec.bidding_time != rec.bidding_time:
                    crm_rec.write({"bidding_time":rec.bidding_time})
                if rec.project_process != False and rec.project_process.strip() != "":
                    flag = 0
                    for i in crm_rec.des_records:
                        if i.week == int(self.week):
                            i.name = rec.project_process
                            flag = 1
                    if flag == 0:
                        str = ""
                        for recc in crm_rec.des_records:
                            if recc.create_date[:10] <= report_end_time and recc.create_date[:10] > (datetime.strptime(report_end_time,"%Y-%m-%d %H:%M:%S") - relativedelta(days=7)).strftime('%Y-%m-%d'):
                                if recc.name != False:
                                    str = str + recc.name + u";"
                        if str != rec.project_process:
                            crm_rec.des_records.create({"name":rec.project_process,"des_id":crm_rec.id,"week":int(self.week)})
                if rec.bidding_time > (datetime.strptime(report_end_time,"%Y-%m-%d %H:%M:%S") + relativedelta(months=3)).strftime("%Y-%m-%d"):
                    self.zhengwu_project = [(2,rec.id)]

    @api.constrains('lead_project')
    def _cons_lead_project(self):
        list = []
        for rec in self.lead_project:
            if rec.project_id:
                if rec.project_id.id in list:
                    raise ValidationError("近三个月招投标机会点重复录入。")
            list.append(rec.project_id.id)
            if len(rec.office_id) == 0:
                rec.project_master_degree = rec.project_id.project_master_degree
                rec.bidding_time = rec.project_id.bidding_time
            rec.system_department_id = rec.project_id.system_department_id
            rec.office_id = rec.project_id.office_id
            if rec.project_id:
                rec.sale_apply_id = rec.project_id.sale_apply_id.name+"."+rec.project_id.sale_apply_id.full_name+" "+rec.project_id.sale_apply_id.job_number
            rec.space_total = rec.project_id.space_total
            rec.industry_id = rec.project_id.industry_id
            report_end_time = self.report_end_time + " 00:00:00"
            if len(rec.project_id) == 0:
                    self.lead_project = [(2,rec.id)]
            if rec.project_id.project_number:
                crm_recs = self.env['crm.lead'].search([('project_number','=',rec.project_id.project_number)])
                if crm_recs is None or len(crm_recs) <= 0:
                    return
                crm_rec = crm_recs[0]
                if crm_rec.project_master_degree != rec.project_master_degree:
                    crm_rec.write({"project_master_degree":rec.project_master_degree})
                if crm_rec.bidding_time != rec.bidding_time:
                    crm_rec.write({"bidding_time":rec.bidding_time})
                if rec.project_process != False and rec.project_process.strip() != "":
                    flag = 0
                    for i in crm_rec.des_records:
                        if i.week == int(self.week):
                            i.name = rec.project_process
                            flag = 1
                    if flag == 0:
                        str = ""
                        for recc in crm_rec.des_records:
                            if recc.create_date[:10] <= report_end_time and recc.create_date[:10] > (datetime.strptime(report_end_time,"%Y-%m-%d %H:%M:%S") - relativedelta(days=7)).strftime('%Y-%m-%d'):
                                if recc.name != False:
                                    str = str + recc.name + u";"
                        if str != rec.project_process:
                            crm_rec.des_records.create({"name":rec.project_process,"des_id":crm_rec.id,"week":int(self.week)})
                if rec.bidding_time > (datetime.strptime(report_end_time,"%Y-%m-%d %H:%M:%S") + relativedelta(months=3)).strftime("%Y-%m-%d"):
                    self.lead_project = [(2,rec.id)]

    @api.constrains('other_project')
    def _cons_other_project(self):
        list = []
        for rec in self.other_project:
            if rec.project_id:
                if rec.project_id.id in list:
                    raise ValidationError("含投资项目及其他重要项目进展重复录入。")
            list.append(rec.project_id.id)
            # if len(rec.office_id) == 0:
            #     print '-------------------->11',rec.project_master_degree, rec.bidding_time
            #
            #     rec.project_master_degree = rec.project_id.project_master_degree
            #     rec.bidding_time = rec.project_id.bidding_time
            rec.system_department_id = rec.project_id.system_department_id
            rec.office_id = rec.project_id.office_id
            if rec.project_id:
                rec.sale_apply_id = rec.project_id.sale_apply_id.name+"."+rec.project_id.sale_apply_id.full_name+" "+rec.project_id.sale_apply_id.job_number
            rec.space_total = rec.project_id.space_total
            rec.industry_id = rec.project_id.industry_id
            report_end_time = self.report_end_time + " 00:00:00"
            if len(rec.project_id) == 0:
                    self.other_project = [(2,rec.id)]
            if rec.project_id.project_number:
                crm_recs = self.env['crm.lead'].search([('project_number','=',rec.project_id.project_number)])
                if crm_recs is None or len(crm_recs) <= 0:
                    return
                crm_rec = crm_recs[0]
                for a_rec in rec.other_project_id.zhengwu_project:
                    if a_rec.project_id.project_number == rec.project_id.project_number:
                        a_rec.project_master_degree = rec.project_master_degree
                        a_rec.bidding_time = rec.bidding_time
                        a_rec.project_process = rec.project_process
                for b_rec in rec.other_project_id.lead_project:
                    if b_rec.project_id.project_number == rec.project_id.project_number:
                        b_rec.project_master_degree = rec.project_master_degree
                        b_rec.bidding_time = rec.bidding_time
                        b_rec.project_process = rec.project_process
                if crm_rec.project_master_degree != rec.project_master_degree:
                    crm_rec.write({"project_master_degree":rec.project_master_degree})
                if crm_rec.bidding_time != rec.bidding_time:
                    crm_rec.write({"bidding_time":rec.bidding_time})
                if rec.project_process != False and rec.project_process.strip() != "":
                    flag = 0
                    for i in crm_rec.des_records:
                        if i.week == int(self.week):
                            i.name = rec.project_process
                            flag = 1
                    if flag == 0:
                        str = ""
                        for recc in crm_rec.des_records:
                            if recc.create_date[:10] <= report_end_time and recc.create_date[:10] > (datetime.strptime(report_end_time,"%Y-%m-%d %H:%M:%S") - relativedelta(days=7)).strftime('%Y-%m-%d'):
                                if recc.name != False:
                                    str = str + recc.name + u";"
                        if str != rec.project_process:
                            crm_rec.des_records.create({"name":rec.project_process,"des_id":crm_rec.id,"week":int(self.week)})

    @api.constrains('next_zhengwu_project')
    def _cons_next_zhengwu_project(self):
        list = []
        for rec in self.next_zhengwu_project:
            if rec.project_id:
                if rec.project_id.id in list:
                    raise ValidationError("重大项目下周计划重复录入。")
            list.append(rec.project_id.id)
            if len(rec.office_id) == 0:
                rec.project_master_degree = rec.project_id.project_master_degree
                rec.bidding_time = rec.project_id.bidding_time
            rec.system_department_id = rec.project_id.system_department_id
            rec.office_id = rec.project_id.office_id
            if rec.project_id:
                rec.sale_apply_id = rec.project_id.sale_apply_id.name+"."+rec.project_id.sale_apply_id.full_name+" "+rec.project_id.sale_apply_id.job_number
            rec.space_total = rec.project_id.space_total
            rec.industry_id = rec.project_id.industry_id
            report_end_time = self.report_end_time + " 00:00:00"
            if len(rec.project_id) == 0:
                    self.next_zhengwu_project = [(2,rec.id)]
            if rec.project_id.project_number:
                crm_recs = self.env['crm.lead'].search([('project_number','=',rec.project_id.project_number)])
                if crm_recs is None or len(crm_recs) <= 0:
                    return
                crm_rec = crm_recs[0]
                if crm_rec.project_master_degree != rec.project_master_degree:
                    crm_rec.write({"project_master_degree":rec.project_master_degree})
                if crm_rec.bidding_time != rec.bidding_time:
                    crm_rec.write({"bidding_time":rec.bidding_time})
                if rec.project_process != False and rec.project_process.strip() != "":
                    flag = 0
                    for i in crm_rec.des_records:
                        if i.week == int(self.week):
                            i.name = rec.project_process
                            flag = 1
                    if flag == 0:
                        str = ""
                        for recc in crm_rec.des_records:
                            if recc.create_date[:10] <= report_end_time and recc.create_date[:10] > (datetime.strptime(report_end_time,"%Y-%m-%d %H:%M:%S") - relativedelta(days=7)).strftime('%Y-%m-%d'):
                                if recc.name != False:
                                    str = str + recc.name + u";"
                        if str != rec.project_process:
                            crm_rec.des_records.create({"name":rec.project_process,"des_id":crm_rec.id,"week":int(self.week)})

    def get_mail_server_name(self):
        return self.env['ir.mail_server'].search([], limit=1).smtp_user

    def dtdream_send_mail(self, subject, content, email_to,email_from,reply_to,appellation,body_html=""):
        email_to = email_to
        subject = subject
        content = content
        self.env['mail.mail'].create({
                'body_html': u'''<p>%s</p>
                                <p>%s</p>
                                <p>%s</p>
                                <p>dodo</p>
                                <p>万千业务，简单有do</p>
                                <p>%s</p>''' % (appellation, content, body_html,self.write_date[:10]),
                'subject': '%s' % subject,
                'email_from': '%s' % email_from,
                'reply_to': '%s' % reply_to,
                'email_to': '%s' % email_to,
                'auto_delete': False,
            }).send()

    def get_base_url(self, cr, uid):
        base_url = self.pool.get('ir.config_parameter').get_param(cr, uid, 'web.base.url')
        return base_url

    def get_mail_server_name(self):
        return self.env['ir.mail_server'].search([], limit=1).smtp_user

    def dtdream_send_submit_mail(self, subject, content, email_to,appellation):
        base_url = self.get_base_url()
        url = base_url + '/web#id=%s&view_type=form&model=dtdream.sale.own.report' % self.id
        email_to = email_to
        subject = subject
        content = content
        self.env['mail.mail'].create({
                'body_html': u'''<p>%s</p>
                                <p>%s</p>
                                <a href="%s">点击进入查看</a></p>
                                <br/>
                                <br/>
                                <br/>
                                <p>dodo</p>
                                <p>万千业务，简单有do</p>
                                <p>%s</p>''' % (appellation, content, url, self.write_date[:10]),
                'subject': '%s' % subject,
                'email_from': self.get_mail_server_name(),
                'email_to': '%s' % email_to,
                'auto_delete': False,
            }).send()

class reply_list(models.Model):
    _name = "reply.list"

    def _get_default_person(self):
        if self._context.get('default_reply_list_to_own_report_id'):
            reporot_rec_id = self._context.get('default_reply_list_to_own_report_id')
            return self.env['dtdream.sale.own.report'].search([('id','=',reporot_rec_id)]).report_person
        else:
            reporot_rec_id = self._context.get('default_reply_list_to_manager_report_id')
            return self.env['dtdream.sale.manager.report'].search([('id','=',reporot_rec_id)]).report_person

    def _get_default_week(self):
        if self._context.get('default_reply_list_to_own_report_id'):
            reporot_rec_id = self._context.get('default_reply_list_to_own_report_id')
            return self.env['dtdream.sale.own.report'].search([('id','=',reporot_rec_id)]).week.name
        else:
            reporot_rec_id = self._context.get('default_reply_list_to_manager_report_id')
            return self.env['dtdream.sale.manager.report'].search([('id','=',reporot_rec_id)]).week.name

    # 返回批复类型，0为个人周报批复，1为主管周报批复
    def _get_default_type(self):
        if self._context.get('default_reply_list_to_own_report_id'):
            return 0
        else:
            return 1

    reply_report_type = fields.Integer(string="批复周报类型",default=_get_default_type)
    reply_report_week = fields.Char(string="批复周报周别",default=_get_default_week)
    report_creator = fields.Many2one("hr.employee",string="周报创建人",default=_get_default_person)
    reply_list_to_own_report_id = fields.Many2one("dtdream.sale.own.report",string="关联个人周报")
    reply_list_to_manager_report_id = fields.Many2one("dtdream.sale.manager.report",string="关联主管周报")
    reply_text = fields.Text(string="批复内容",required=True)
    mail_persons = fields.Many2many("hr.employee",string="批复发送对象",default=_get_default_person,required=True)
    reply_person = fields.Many2one("hr.employee",string="批复人", default=lambda self:self.env['hr.employee'].search([('login','=',self.env.user.login)]), readonly=1)

    def get_base_url(self, cr, uid):
        base_url = self.pool.get('ir.config_parameter').get_param(cr, uid, 'web.base.url')
        return base_url

    def get_mail_server_name(self):
        return self.env['ir.mail_server'].search([], limit=1).smtp_user

    def dtdream_reply_mail_to_creator(self, subject, content, email_to,appellation,link):
        base_url = self.get_base_url()
        url = base_url+link
        email_to = email_to
        subject = subject
        content = content
        self.env['mail.mail'].create({
                'body_html': u'''<p>%s</p>
                                <p>%s</p>
                                <a href="%s">点击进入查看</a></p>
                                <br/>
                                <br/>
                                <br/>
                                <p>dodo</p>
                                <p>万千业务，简单有do</p>
                                <p>%s</p>''' % (appellation, content, url, self.write_date[:10]),
                'subject': '%s' % subject,
                'email_from': self.get_mail_server_name(),
                'email_to': '%s' % email_to,
                'auto_delete': False,
            }).send()

    def dtdream_reply_mail_to_mail_persons(self, subject, content, email_to,appellation):
        email_to = email_to
        subject = subject
        content = content
        self.env['mail.mail'].create({
                'body_html': u'''<p>%s</p>
                                <p>%s</p>
                                <br/>
                                <br/>
                                <br/>
                                <p>dodo</p>
                                <p>万千业务，简单有do</p>
                                <p>%s</p>''' % (appellation, content, self.write_date[:10]),
                'subject': '%s' % subject,
                'email_from': self.get_mail_server_name(),
                'email_to': '%s' % email_to,
                'auto_delete': False,
            }).send()

    @api.one
    def btn_confirm(self):
        email_to = ""
        for person in self.mail_persons:
            if person != self.report_creator:
                email_to = email_to + person.work_email+";"
        if self.reply_report_type == 0:
            if self.env['hr.employee'].search([('login','=',self.create_uid.login)]) != self.report_creator:
                self.dtdream_reply_mail_to_creator(u"{0}，{1}对您第{2}周的个人周报进行了批复!".format(self.create_date,self.env['hr.employee'].search([('login','=',self.create_uid.login)]).name, self.reply_report_week),
                        content=self.reply_text,email_to=self.report_creator.work_email,appellation = u'您好,批复内容如下:',link = '/web#id=%s&view_type=form&model=dtdream.sale.own.report' % self.reply_list_to_own_report_id.id)
            self.dtdream_reply_mail_to_mail_persons(u"{0}，{1}对{2}第{3}周的个人周报进行了批复!".format(self.create_date,self.env['hr.employee'].search([('login','=',self.create_uid.login)]).name, self.report_creator.name,self.reply_report_week),
                       content=self.reply_text, email_to=email_to,
                       appellation = u'您好,批复内容如下:')
        else:
            if self.env['hr.employee'].search([('login','=',self.create_uid.login)]) != self.report_creator:
                self.dtdream_reply_mail_to_creator(u"{0}，{1}对您第{2}周的主管周报进行了批复!".format(self.create_date,self.env['hr.employee'].search([('login','=',self.create_uid.login)]).name, self.reply_report_week),
                        content=self.reply_text,email_to=self.report_creator.work_email,appellation = u'您好,批复内容如下:',link = '/web#id=%s&view_type=form&model=dtdream.sale.own.report' % self.reply_list_to_own_report_id.id)
            self.dtdream_reply_mail_to_mail_persons(u"{0}，{1}对{2}第{3}周的主管周报进行了批复!".format(self.create_date,self.env['hr.employee'].search([('login','=',self.create_uid.login)]).name, self.report_creator.name,self.reply_report_week),
                       content=self.reply_text, email_to=email_to,
                       appellation = u'您好,批复内容如下:')

class report_week(models.Model):
    _name = "report.week"
    _order = "id desc"

    name = fields.Char(string="周别")

    @api.multi
    def name_get(self):
        list = []
        for cat in self:
            flag = 0
            if cat.id == int(datetime.strftime(datetime.now(),"%W")):
                list.append((cat.id,u"第%s周(本周)"%cat.name))
                flag = 1
            if cat.id == int(datetime.strftime(datetime.now(),"%W"))-1:
                list.append((cat.id,u"第%s周(上周)"%cat.name))
                flag = 1
            if cat.id == int(datetime.strftime(datetime.now(),"%W"))-2:
                list.append((cat.id,u"第%s周(上二周)"%cat.name))
                flag = 1
            if cat.id == int(datetime.strftime(datetime.now(),"%W"))-3:
                list.append((cat.id,u"第%s周(上三周)"%cat.name))
                flag = 1
            if cat.id == int(datetime.strftime(datetime.now(),"%W"))-4:
                list.append((cat.id,u"第%s周(上四周)"%cat.name))
                flag = 1
            if flag == 0:
                list.append((cat.id,u"第%s周"%cat.name))
        return list

class sys_list(models.Model):
    _name = "sys.list"

    rec_id = fields.Many2one("dtdream.sale.own.report")
    project_total = fields.Integer(string="项目个数")
    space_total = fields.Integer(string="项目空间(万元)")
    important_project = fields.Integer(string="重大项目个数")
    important_space = fields.Integer(string="重大项目空间(万元)")
    lead_project_total = fields.Integer(string="机会点个数")
    lead_space_total = fields.Integer(string="机会点空间(万元)")
    lead_important_project = fields.Integer(string="重大机会点个数")
    lead_important_space = fields.Integer(string="重大机会点空间(万元)")
    system_name = fields.Char(string="系统部")
    project_count = fields.Integer(string="小计(万元)")
    week_new_space = fields.Integer(string="本周新增项目空间(万元)")
    weekly_refresh_rate = fields.Integer("项目周刷新率(%)")
    monthly_laed_refresh_rate = fields.Integer("机会点月刷新率(%)")
    bid_amount = fields.Integer(string="中标金额(万元)")
    contract_signing_amount = fields.Integer(string="合同签订额(万元)")
    received = fields.Integer(string="已收款(万元)")
    accounts_payable = fields.Integer(string="应付款(万元)")

    @api.onchange("bid_amount","contract_signing_amount","accounts_payable","received")
    def _check_integer(self):
        if self.bid_amount < 0 :
            self.bid_amount = False
            return {'warning': {
                "title": u"提示",
                "message": u"请勿输入负值"
            }}
        if self.contract_signing_amount < 0 :
            self.contract_signing_amount = 0
            return {'warning': {
                "title": u"提示",
                "message": u"请勿输入负值"
            }}
        if self.accounts_payable < 0 :
            self.accounts_payable = 0
            return {'warning': {
                "title": u"提示",
                "message": u"请勿输入负值"
            }}
        if self.received < 0 :
            self.received = 0
            return {'warning': {
                "title": u"提示",
                "message": u"请勿输入负值"
            }}

# 政务系统部项目
class zhengwu_system_project(models.Model):
    _name = 'zhengwu.system.project'
    _description = u"近三个月招投标项目"

    zhengwu_project_id = fields.Many2one("dtdream.sale.own.report",string="个人周报")
    next_zhengwu_project_id = fields.Many2one("dtdream.sale.own.report",string="个人周报")

    @api.onchange('project_id')
    def _onchange_project_info(self):
        for rec in self:
            if rec.project_id.id == False and rec.zhengwu_project_id.id != False:
                date = rec.zhengwu_project_id.report_end_time+" 00:00:00"
                return {
                    'domain': {
                        "project_id":[('type','=','opportunity'),('bidding_time','<=',(datetime.strptime(date,"%Y-%m-%d %H:%M:%S")+ relativedelta(months=3)).strftime("%Y-%m-%d"))]
                    }
                }
            rec.office_id = rec.project_id.office_id
            if rec.project_id:
                rec.sale_apply_id = rec.project_id.sale_apply_id.name+"."+rec.project_id.sale_apply_id.full_name+" "+rec.project_id.sale_apply_id.job_number
            rec.space_total = rec.project_id.space_total
            rec.project_master_degree = rec.project_id.project_master_degree
            rec.bidding_time = rec.project_id.bidding_time
            rec.project_number = rec.project_id.project_number
            rec.project_leave = rec.project_id.project_leave
            rec.system_department_id = rec.project_id.system_department_id
            rec.industry_id = rec.project_id.industry_id
            if datetime.weekday(datetime.now()) >= 4:
                report_end_time = datetime.now() - relativedelta(days=((datetime.weekday(datetime.now())) - 4))
            else:
                report_end_time = datetime.now() + relativedelta(days=(4-7-datetime.weekday(datetime.now())))
            str = ""
            for recc in rec.project_id.des_records:
                if recc.create_date[:10] <= report_end_time.strftime('%Y-%m-%d') and recc.create_date[:10] > (report_end_time - relativedelta(days=7)).strftime('%Y-%m-%d'):
                    if rec.zhengwu_project_id and recc.name != False and recc.week != rec.zhengwu_project_id.week.id:
                        str = str + recc.name + u";"
                    if rec.next_zhengwu_project_id and recc.name != False and recc.week != rec.next_zhengwu_project_id.week.id:
                        str = str + recc.name + u";"
            rec.project_process = str

    office_id = fields.Many2one("dtdream.office", string="办事处",store=True)
    project_id = fields.Many2one('crm.lead',string="项目名称")
    sale_apply_id = fields.Char(string="营销责任人")
    space_total = fields.Integer(string="项目空间(万元)")
    project_master_degree = fields.Selection([
        ('1', 'A'),
        ('2', 'B'),
        ('3', 'C'),
        ('4', 'D'),
    ],'项目把握度')
    bidding_time = fields.Date(string="招标时间")
    project_process = fields.Text(string="上周项目进展")
    next_process = fields.Text(string="下周项目计划")
    project_number = fields.Char(string="项目编号")
    project_leave = fields.Char(string="项目级别")
    system_department_id = fields.Many2one("dtdream.industry", string="系统部",store=True)
    industry_id = fields.Many2one("dtdream.industry",string="行业",store=True)

# 重大机会点
class lead_project(models.Model):
    _name = 'lead.project'
    _description = u"重大机会点"

    lead_project_id = fields.Many2one("dtdream.sale.own.report",string="个人周报")

    @api.onchange('project_id')
    def _compute_project_info(self):
        for rec in self:
            if rec.project_id.id == False:
                date = rec.lead_project_id.report_end_time+" 00:00:00"
                return {
                    'domain': {
                        "project_id":[('type','=','lead'),('bidding_time','<=',(datetime.strptime(date,"%Y-%m-%d %H:%M:%S")+ relativedelta(months=3)).strftime("%Y-%m-%d"))]
                    }
                }
            rec.office_id = rec.project_id.office_id
            if rec.project_id:
                rec.sale_apply_id = rec.project_id.sale_apply_id.name+"."+rec.project_id.sale_apply_id.full_name+" "+rec.project_id.sale_apply_id.job_number
            rec.space_total = rec.project_id.space_total
            rec.project_master_degree = rec.project_id.project_master_degree
            rec.bidding_time = rec.project_id.bidding_time
            rec.project_number = rec.project_id.project_number
            rec.system_department_id = rec.project_id.system_department_id
            rec.industry_id = rec.project_id.industry_id
            if datetime.weekday(datetime.now()) >= 4:
                report_end_time = datetime.now() - relativedelta(days=((datetime.weekday(datetime.now())) - 4))
            else:
                report_end_time = datetime.now() + relativedelta(days=(4-7-datetime.weekday(datetime.now())))
            str = ""
            for recc in rec.project_id.des_records:
                if recc.create_date[:10] <= report_end_time.strftime('%Y-%m-%d') and recc.create_date[:10] > (report_end_time - relativedelta(days=7)).strftime('%Y-%m-%d'):
                    if recc.name != False and recc.week != rec.lead_project_id.week.id:
                        str = str + recc.name + u";"
            rec.project_process = str

    office_id = fields.Many2one("dtdream.office", string="办事处")
    project_id = fields.Many2one('crm.lead',string="项目名称")
    sale_apply_id = fields.Char(string="营销责任人")
    space_total = fields.Integer(string="项目空间(万元)")
    project_master_degree = fields.Selection([
        ('1', 'A'),
        ('2', 'B'),
        ('3', 'C'),
        ('4', 'D'),
    ],'项目把握度')
    project_leave = fields.Char(string="项目级别")
    bidding_time = fields.Date(string="招标时间")
    project_process = fields.Text(string="上周项目进展")
    project_number = fields.Char(string="项目编号")
    system_department_id = fields.Many2one("dtdream.industry", string="系统部")
    industry_id = fields.Many2one("dtdream.industry",string="行业")

# 含投资项目及其他重要项目进展
class other_project(models.Model):
    _name = 'other.project'
    _description = u"含投资项目及其他重要项目进展"

    other_project_id = fields.Many2one("dtdream.sale.own.report",string="个人周报")

    @api.onchange('project_id')
    def _compute_project_info(self):
        for rec in self:
            rec.office_id = rec.project_id.office_id
            if rec.project_id:
                rec.sale_apply_id = rec.project_id.sale_apply_id.name+"."+rec.project_id.sale_apply_id.full_name+" "+rec.project_id.sale_apply_id.job_number
            rec.space_total = rec.project_id.space_total
            rec.project_master_degree = rec.project_id.project_master_degree
            rec.bidding_time = rec.project_id.bidding_time
            rec.project_number = rec.project_id.project_number
            rec.system_department_id = rec.project_id.system_department_id
            rec.industry_id = rec.project_id.industry_id
            if datetime.weekday(datetime.now()) >= 4:
                report_end_time = datetime.now() - relativedelta(days=((datetime.weekday(datetime.now())) - 4))
            else:
                report_end_time = datetime.now() + relativedelta(days=(4-7-datetime.weekday(datetime.now())))
            str = ""
            for recc in rec.project_id.des_records:
                if recc.create_date[:10] <= report_end_time.strftime('%Y-%m-%d') and recc.create_date[:10] > (report_end_time - relativedelta(days=7)).strftime('%Y-%m-%d'):
                    if recc.name != False and recc.week != rec.other_project_id.week.id:
                        str = str + recc.name + u";"
            rec.project_process = str

    def domain_other_project(self):
        return [('is_invest_project','=','1')]

    office_id = fields.Many2one("dtdream.office", string="办事处")
    project_id = fields.Many2one('crm.lead',string="项目名称",domain=domain_other_project)
    sale_apply_id = fields.Char(string="营销责任人")
    space_total = fields.Integer(string="项目空间(万元)")
    project_master_degree = fields.Selection([
        ('1', 'A'),
        ('2', 'B'),
        ('3', 'C'),
        ('4', 'D'),
    ],'项目把握度')
    bidding_time = fields.Date(string="招标时间")
    project_process = fields.Text(string="上周项目进展")
    project_number = fields.Char(string="项目编号")
    system_department_id = fields.Many2one("dtdream.industry", string="系统部")
    industry_id = fields.Many2one("dtdream.industry",string="行业")

# 渠道进展
class sale_channel(models.Model):
    _name = 'sale.channel'
    _description = u"渠道进展"

    @api.onchange("name")
    @api.depends("name")
    def compute_info_by_name(self):
        for i in self:
            if i.name:
                recs = i.env['crm.lead'].search(['&',('sale_channel','like',("%"+i.name+"%")),"|",'&',('type','=','lead'),('sale_apply_id.user_id.id','=',self._uid),'&',('stage_id.name','in',(u'项目启动',u'技术和商务交流',u'项目招投标',u'中标')),'&',('sale_apply_id.user_id.id','=',self._uid),('type','=','opportunity')])
                space_total = 0
                for rec in recs:
                    space_total = space_total + rec.space_total
                i.project_total = len(recs)
                i.project_space_total = space_total

    sale_channel_id = fields.Many2one("dtdream.sale.own.report",string="个人周报")
    name = fields.Char("渠道名称")
    project_id = fields.Many2one("crm.lead",string="关联项目")
    project_total = fields.Integer("关联项目个数",compute=compute_info_by_name,store=True)
    project_space_total = fields.Integer("关联项目空间(万元)",compute=compute_info_by_name,store=True)
    channer_process = fields.Text("渠道拓展进展")

# 客户拜访
class visit_customer(models.Model):
    _name = 'visit.customer'
    _description = u"客户拜访"

    @api.onchange("partner_id")
    @api.depends("partner_id")
    def _onchange_partner_id(self):
        for rec in self:
            rec.system_department_id = rec.partner_id.system_department_id
            rec.industry_id = rec.partner_id.industry_id
            rec.office_id = rec.partner_id.office_id

    visit_customer_id = fields.Many2one("dtdream.sale.own.report",string="个人周报")

    partner_id = fields.Many2one("res.partner","客户名称")
    system_department_id = fields.Many2one("dtdream.industry", string="系统部",compute=_onchange_partner_id,store=True)
    industry_id = fields.Many2one("dtdream.industry",string="行业",compute=_onchange_partner_id,store=True)
    office_id = fields.Many2one("dtdream.office", string="办事处",compute=_onchange_partner_id,store=True)
    visit_date = fields.Date(string="拜访时间")
    visit_object = fields.Char(string="拜访对象")
    content = fields.Text(string="交流主要内容")
    next_plan = fields.Text(string="下一步计划")
    ask_help = fields.Char(string="困难求助")
    send_person = fields.Many2many("hr.employee",string="发送对象")

# 客户拜访
class customer_visit_plan(models.Model):
    _name = 'customer.visit.plan'
    _description = u"重点客户(含阿里)拜访计划"

    @api.onchange("partner_id")
    @api.depends("partner_id")
    def _onchange_partner_id(self):
        for rec in self:
            rec.system_department_id = rec.partner_id.system_department_id
            rec.industry_id = rec.partner_id.industry_id
            rec.office_id = rec.partner_id.office_id

    customer_visit_plan_id = fields.Many2one("dtdream.sale.own.report",string="个人周报")

    partner_id = fields.Many2one("res.partner","客户名称")
    system_department_id = fields.Many2one("dtdream.industry", string="系统部",compute=_onchange_partner_id,store=True)
    industry_id = fields.Many2one("dtdream.industry",string="行业",compute=_onchange_partner_id,store=True)
    visit_date = fields.Date(string="预计拜访时间")
    visit_object = fields.Char(string="拜访对象")
    content = fields.Text(string="交流主要内容")
    office_id = fields.Many2one("dtdream.office", string="办事处",compute=_onchange_partner_id,store=True)


# 竞争对手情况
class competitor_situation(models.Model):
    _name = 'competitor.situation'
    _description = u"竞争对手情况"

    competitor_situation_id = fields.Many2one("dtdream.sale.own.report",string="个人周报")

    name = fields.Char("友商名称")
    recent_dynamics = fields.Char("最近动态")
    compute_strategy = fields.Char("我司竞争策略")

# 其他
class sale_other(models.Model):
    _name = 'sale.other'
    _description = u"其他重要事项"

    sale_other_id = fields.Many2one("dtdream.sale.own.report",string="个人周报")
    next_sale_other_id = fields.Many2one("dtdream.sale.own.report",string="个人周报")

    name = fields.Text("其他重要事项描述")
    week_process = fields.Text("下周工作计划")

class problem_help(models.Model):
    _name = "problem.help"
    _description = u"问题与求助"

    problem_help_id = fields.Many2one("dtdream.sale.own.report",string="个人周报")
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
    _order = "report_start_time desc"

    @api.onchange("a_week")
    @api.constrains('a_week')
    def _onchange_a_week(self):
        if datetime.weekday(datetime.now()) >= 4:
            report_end_time = datetime.now() - relativedelta(days=((datetime.weekday(datetime.now())) - 4))
            report_end_time = report_end_time
        else:
            report_end_time = datetime.now() + relativedelta(days=(4-7-datetime.weekday(datetime.now())))
            report_end_time = report_end_time
        report_start_time = report_end_time - relativedelta(days=7)
        week = int(datetime.strftime(report_end_time,"%W"))
        a_report_end_time = report_end_time - relativedelta(days=(week-int(self.a_week.name))*7)
        self.a_report_end_time = a_report_end_time
        self.a_report_start_time = report_start_time - relativedelta(days=(week-int(self.a_week.name))*7)
        self.report_end_time = a_report_end_time
        self.report_start_time = report_start_time - relativedelta(days=(week-int(self.a_week.name))*7)

    @api.model
    def default_get(self,fields):
        report_person = self.env['hr.employee'].search([('login','=',self.env.user.login)])
        if not (report_person.name and report_person.full_name and report_person.job_number):
            raise ValidationError("请先完成员工与用户的关联。")
        res = super(dtdream_sale_manager_report, self).default_get(fields)
        return res

    @api.depends('report_person')
    def _compute_reportor_info(self):
        for ref in self:
            ref.report_person_name = ref.report_person.name+"."+ref.report_person.full_name+"  "+ref.report_person.job_number
            ref.job_number = ref.report_person.job_number
            ref.department = ref.report_person.department_id.id
            ref.complete_name = ref.report_person.department_id.complete_name.replace(' ', '')
            if not ref.report_end_time:
                if datetime.weekday(datetime.now()) >= 4:
                    report_end_time = datetime.now() - relativedelta(days=((datetime.weekday(datetime.now())) - 4))
                    ref.a_report_end_time = report_end_time
                else:
                    report_end_time = datetime.now() + relativedelta(days=(4-7-datetime.weekday(datetime.now())))
                    ref.a_report_end_time = report_end_time
                ref.a_report_start_time = report_end_time - relativedelta(days=7)
                ref.a_week = int(datetime.strftime(report_end_time,"%W"))

    @api.onchange('create_office','create_system')
    def _onchange_zhengwu_project(self):
        zhengwu_project_total = 0
        zhengwu_space_total = 0
        zhengwu_important_project = 0
        zhengwu_important_space = 0
        leads_project_total = 0
        leads_space_total = 0
        leads_important_project = 0
        leads_important_space = 0
        week_add_spaces = 0
        monthly_lead_project_totals = 0
        weekly_project_totals = 0
        sys_list = []
        create_office_ids = [rec.id for rec in self.create_office]
        system_department_ids = [recc.id for recc in self.create_system]
        projects_in_operations = self.env['crm.lead'].search([('stage_id.name','in',('项目启动','技术和商务交流','项目招投标')),('office_id.id','in',create_office_ids),('industry_id.id','in',system_department_ids)])
        for rec in projects_in_operations:
            if rec.id != False:
                zhengwu_project_total = zhengwu_project_total +1
            if rec.system_department_id not in sys_list and rec.id != False:
                sys_list.append(rec.system_department_id)
            zhengwu_space_total = zhengwu_space_total + rec.space_total
            if rec.project_leave in ('company_leave','department_leave'):
                zhengwu_important_project = zhengwu_important_project + 1;
                zhengwu_important_space = zhengwu_important_space + rec.space_total
            if rec.create_date:
                if rec.create_date[:10] > self.report_start_time and rec.create_date[:10] <= self.report_end_time:
                    week_add_spaces = week_add_spaces + rec.space_total
            if rec.write_date:
                if rec.write_date[:10] > self.report_start_time and rec.write_date[:10] <= self.report_end_time:
                    weekly_project_totals = weekly_project_totals + 1
        projects_in_lead = self.env['crm.lead'].search([('stage_id.name','=','机会点'),('office_id.id','in',create_office_ids),('industry_id.id','in',system_department_ids)])
        for recc in projects_in_lead:
            if recc.id != False:
                leads_project_total = leads_project_total +1
            if recc.system_department_id not in sys_list and recc.id != False:
                sys_list.append(recc.system_department_id)
            leads_space_total = leads_space_total + recc.space_total
            if recc.project_leave in ('company_leave','department_leave'):
                leads_important_project = leads_important_project + 1;
                leads_important_space = leads_important_space + recc.space_total
            if recc.create_date:
                if recc.create_date[:10] > self.report_start_time and recc.create_date[:10] <= self.report_end_time:
                    week_add_spaces = week_add_spaces + recc.space_total
            if recc.write_date:
                if recc.write_date[:10] >= (datetime.strptime(self.report_end_time + " 00:00:00","%Y-%m-%d %H:%M:%S") - relativedelta(months=1)).strftime('%Y-%m-%d'):
                    monthly_lead_project_totals = monthly_lead_project_totals + 1
        sys_compute_list = []
        lead_project_total = 0
        lead_space_total = 0
        for sys_name in sys_list:
            project_total = 0
            lead_project_total = 0
            space_total = 0
            important_project = 0
            important_space = 0
            lead_important_project = 0
            lead_important_space = 0
            lead_space_total = 0
            week_new_space = 0
            weekly_project_total = 0
            monthly_lead_project_total = 0
            for rec in projects_in_operations:
                if rec.system_department_id == sys_name and rec.id != False:
                    project_total = project_total + 1
                    space_total = space_total + rec.space_total
                    if rec.project_leave in ('company_leave','department_leave'):
                        important_project = important_project + 1;
                        important_space = important_space + rec.space_total
                    if rec.create_date:
                        if rec.create_date[:10] > self.report_start_time and rec.create_date[:10] <= self.report_end_time:
                            week_new_space = week_new_space + rec.space_total
                    if rec.write_date:
                        if rec.write_date[:10] > self.report_start_time and rec.write_date[:10] <= self.report_end_time:
                            weekly_project_total = weekly_project_total + 1
            for lead_rec in projects_in_lead:
                if lead_rec.system_department_id == sys_name and lead_rec.id != False:
                    lead_project_total = lead_project_total + 1
                    lead_space_total = lead_space_total + lead_rec.space_total
                    if lead_rec.project_leave in ('company_leave','department_leave'):
                        lead_important_project = lead_important_project + 1;
                        lead_important_space = lead_important_space + lead_rec.space_total
                    if lead_rec.create_date:
                        if lead_rec.create_date[:10] > self.report_start_time and lead_rec.create_date[:10] <= self.report_end_time:
                            week_new_space = week_new_space + lead_rec.space_total
                    if lead_rec.write_date:
                        if lead_rec.write_date[:10] >= (datetime.strptime(self.report_end_time+ " 00:00:00","%Y-%m-%d %H:%M:%S") - relativedelta(months=1)).strftime('%Y-%m-%d'):
                            monthly_lead_project_total = monthly_lead_project_total + 1
            if lead_project_total != 0:
                monthly_laed_refresh_rate = float(monthly_lead_project_total)/lead_project_total*100
            else:
                monthly_laed_refresh_rate = 0
            if project_total != 0:
                weekly_refresh_rate = float(weekly_project_total)/project_total*100
            else:
                weekly_refresh_rate = 0
            sys_compute_list.append({"project_total":(project_total+lead_project_total),"weekly_refresh_rate":weekly_refresh_rate,"monthly_laed_refresh_rate":monthly_laed_refresh_rate,"week_new_space":week_new_space,"project_count":space_total+lead_space_total,"space_total":space_total,"important_project":important_project,"important_space":important_space,"system_name":sys_name.name,"lead_project_total":lead_project_total,"lead_space_total":lead_space_total,"lead_important_project":lead_important_project,"lead_important_space":lead_important_space})
        if zhengwu_project_total != 0:
            weekly_refresh_rate = float(weekly_project_totals)/(zhengwu_project_total)*100
        else:
            weekly_refresh_rate = 0
        if leads_project_total != 0:
            monthly_laed_refresh_rate = float(monthly_lead_project_totals)/(leads_project_total)*100
        else:
            monthly_laed_refresh_rate = 0
        if len(sys_compute_list) > 0:
            self.project_total = zhengwu_project_total+leads_project_total
            self.weekly_refresh_rate = weekly_refresh_rate
            self.monthly_laed_refresh_rate = monthly_laed_refresh_rate
            self.week_new_space = week_new_space
            self.project_count = zhengwu_space_total+leads_space_total
            self.space_total = zhengwu_space_total
            self.lead_space_total = leads_space_total
        if len(self.sys_compute_lists)>0:
            for sys_record in self.sys_compute_lists:
                for sys_rec in sys_compute_list:
                    if sys_rec["system_name"] == sys_record.system_name:
                        sys_rec["bid_amount"] = sys_record.bid_amount
                        sys_rec["contract_signing_amount"] = sys_record.contract_signing_amount
                        sys_rec["received"] = sys_record.received
                        sys_rec["accounts_payable"] = sys_record.accounts_payable
            self.write({'sys_compute_lists':[(6,0,[])]})
        self.sys_compute_lists = sys_compute_list

    def get_system_domain(self):
        id_list = []
        for rec in self.env['res.users'].search([('id','=',self.env.user.id)]).user_access_industry:
            id_list.append(rec.id)
        return [('id','in',id_list)]

    def get_office_domain(self):
        id_list = []
        for rec in self.env['res.users'].search([('id','=',self.env.user.id)]).user_access_office:
            id_list.append(rec.id)
        return [('id','in',id_list)]

    def domain_week(self):
        if datetime.weekday(datetime.now()) >= 4:
            report_end_time = datetime.now() - relativedelta(days=((datetime.weekday(datetime.now())) - 4))
        else:
            report_end_time = datetime.now() + relativedelta(days=(4-7-datetime.weekday(datetime.now())))
        end_week = datetime.strftime(report_end_time,"%W")
        start_week = int(end_week) - 3
        return [('id','>=',start_week),('id','<=',end_week)]

    def get_system_default(self):
        return self.env['res.users'].search([('id','=',self.env.user.id)]).user_access_industry

    def get_office_default(self):
        return self.env['res.users'].search([('id','=',self.env.user.id)]).user_access_office

    @api.onchange("week")
    @api.depends("week")
    def _onchange_week(self):
        if datetime.weekday(datetime.now()) >= 4:
            report_end_time = datetime.now() - relativedelta(days=((datetime.weekday(datetime.now())) - 4))
            report_end_time = report_end_time
        else:
            report_end_time = datetime.now() + relativedelta(days=(4-7-datetime.weekday(datetime.now())))
            report_end_time = report_end_time
        report_start_time = report_end_time - relativedelta(days=7)
        week = int(datetime.strftime(report_end_time,"%W"))
        self.report_start_time = report_start_time
        if not self.week:
            self.report_end_time = self.a_report_end_time
            self.report_start_time = self.a_report_start_time
        else:
            a_report_end_time = report_end_time - relativedelta(days=(week-int(self.week.name))*7)
            self.report_end_time = a_report_end_time
            self.report_start_time = report_start_time - relativedelta(days=(week-int(self.week.name))*7)
            # self._onchange_zhengwu_project()
            try:
                self.id - self.id
            except:
                self.compute_project_info(int(datetime.strftime(a_report_end_time,"%W")))

    def get_mail_server_name(self):
        return self.env['ir.mail_server'].search([], limit=1).smtp_user

    def dtdream_send_mail(self, subject, content, email_to,email_from,reply_to,appellation,body_html="",email_cc=None):
        email_to = email_to
        subject = subject
        content = content
        self.env['mail.mail'].create({
                'body_html': u'''<p>%s</p>
                                <p>%s</p>
                                <p>%s</p>
                                <p>dodo</p>
                                <p>万千业务，简单有do</p>
                                <p>%s</p>''' % (appellation, content, body_html,self.write_date[:10]),
                'subject': '%s' % subject,
                'email_from': '%s' % email_from,
                'email_to': '%s' % email_to,
                'reply_to': '%s' % reply_to,
                'email_cc': '%s' % email_cc,
                'auto_delete': False,
            }).send()

    @api.multi
    def btn_submit(self):
        self.write({'status':'1','submit_date':datetime.now()})
        if len(self.visit_customer) > 0:
            person_list = []
            arr = {}
            for rec in self.visit_customer:
                for person in rec.send_person:
                    if person.name not in person_list:
                        person_list.append(person.name)
                        arr[person.name] = [{"partner_id":rec.partner_id.name,"system_department_id":rec.system_department_id.name,"office_id":rec.office_id.name,"industry_id":rec.industry_id.name,"visit_date":rec.visit_date,"visit_object":rec.visit_object,"content":rec.content,"next_plan":rec.next_plan,"ask_help":rec.ask_help,"work_email":person.work_email}]
                    else:
                        arr[person.name].append({"partner_id":rec.partner_id.name,"system_department_id":rec.system_department_id.name,"office_id":rec.office_id.name,"industry_id":rec.industry_id.name,"visit_date":rec.visit_date,"visit_object":rec.visit_object,"content":rec.content,"next_plan":rec.next_plan,"ask_help":rec.ask_help,"work_email":person.work_email})
            for rec in arr:
                body_html = u"""<table border="1px" width="800px" style="border-collapse: collapse;"><thead>
                                <th>客户名称</th>
                                <th>系统部</th>
                                <th>办事处</th>
                                <th>行业</th>
                                <th>拜访时间</th>
                                <th>拜访对象</th>
                                <th width="20%">交流主要内容</th>
                                <th width="20%">下一步计划</th>
                                <th width="25%">困难求助</th>
                                </thead><tbody>"""
                for a_rec in arr[rec]:
                    work_email = a_rec['work_email']
                    body_html = body_html + u"<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>"%(a_rec['partner_id'],a_rec['system_department_id'],a_rec['office_id'],a_rec['industry_id'],a_rec['visit_date'],a_rec['visit_object'],a_rec['content'],a_rec['next_plan'],a_rec['ask_help'])
                body_html = body_html + u"</tbody></table>"
                self.dtdream_send_mail(u"{0}于{1}提交了主管周报,并向您发起困难求助!".format(self.env['hr.employee'].search([('login','=',self.create_uid.login)]).name, self.create_date[:10]),
                   u"%s提交了主管周报,并就以下困难向您求助" % self.env['hr.employee'].search([('login','=',self.create_uid.login)]).name, email_to=work_email,email_from=self.env['hr.employee'].search([('login','=',self.create_uid.login)]).work_email,reply_to=self.env['hr.employee'].search([('login','=',self.create_uid.login)]).work_email,
                   appellation = u'{0},您好：'.format(rec),body_html = body_html)

        if len(self.dtdream_problem_help) > 0:
            person_list = []
            arr = {}
            for rec in self.dtdream_problem_help:
                for person in rec.report_help_people:
                    if person.name not in person_list:
                        person_list.append(person.name)
                        arr[person.name] = [{"type":rec.type.name,"name":rec.name,"work_email":person.work_email}]
                    else:
                        arr[person.name].append({"type":rec.type.name,"name":rec.name,"work_email":person.work_email})
            for rec in arr:
                body_html = u"""<table border="1px" width="600px"  style="border-collapse: collapse;"><thead>
                                <th width="30%">问题类型</th>
                                <th width="70%">问题详情</th>
                                </thead><tbody>"""
                for a_rec in arr[rec]:
                    work_email = a_rec['work_email']
                    body_html = body_html + u"<tr><td>%s</td><td>%s</td></tr>"%(a_rec['type'],a_rec['name'])
                body_html = body_html + u"</tbody></table>"
                self.dtdream_send_mail(u"{0}于{1}提交了主管周报,并向您发起问题求助!".format(self.env['hr.employee'].search([('login','=',self.create_uid.login)]).name, self.create_date[:10]),
                   u"%s提交了主管周报,并就以下问题向您求助" % self.env['hr.employee'].search([('login','=',self.create_uid.login)]).name, email_to=work_email,email_from=self.env['hr.employee'].search([('login','=',self.create_uid.login)]).work_email,reply_to=self.env['hr.employee'].search([('login','=',self.create_uid.login)]).work_email,
                   appellation = u'{0},您好：'.format(rec),body_html = body_html)

        email_to = ""
        email_cc = ""
        for user in self.env['res.groups'].search([('name','=',u"营销管理组")])[0].users:
            email_to = email_to +self.env['hr.employee'].search([('login','=',user.login)]).work_email+";"
        for user in self.env['res.groups'].search([('name','=',u"区域管理部部长")])[0].users:
            if str([a.id for a in self.create_office])[1:-1] in str([x.id for x in user.user_access_office])[1:-1]:
                email_cc = email_cc +self.env['hr.employee'].search([('login','=',user.login)]).work_email+";"
        if email_to:
            base_url = self.get_base_url()
            link = '/web#id=%s&view_type=form&model=dtdream.sale.manager.report' % self.id
            url = base_url+link
            email_to = email_to
            subject = u"{0}于{1}提交了主管周报!".format(self.env['hr.employee'].search([('login','=',self.create_uid.login)]).name,self.create_date[:10])
            content = u"%s提交了主管周报" % self.env['hr.employee'].search([('login','=',self.create_uid.login)]).name
            self.env['mail.mail'].create({
                    'body_html': u'''<p>%s</p>
                                    <p>%s</p>
                                    <a href="%s">点击进入查看</a></p>
                                    <p>dodo</p>
                                    <p>万千业务，简单有do</p>
                                    <p>%s</p>''' % (u'您好：', content, url, self.write_date[:10]),
                    'subject': '%s' % subject,
                    'email_from': self.env['hr.employee'].search([('login','=',self.create_uid.login)]).work_email,
                    'reply_to': self.env['hr.employee'].search([('login','=',self.create_uid.login)]).work_email,
                    'email_to': '%s' % email_to,
                    'email_cc': '%s' % email_cc,
                    'auto_delete': False,
                }).send()

    def get_base_url(self, cr, uid):
        base_url = self.pool.get('ir.config_parameter').get_param(cr, uid, 'web.base.url')
        return base_url

    state = fields.Selection(
        [('0', '新建'),
         ('1','草稿')], string="状态", default="0")

    status = fields.Selection(
        [('0', '草稿'),
         ('1', '已提交')],string="状态", default="0",track_visibility='onchange')

    project_total = fields.Integer(string="项目个数")
    lead_space_total = fields.Integer(string="机会点空间(万元)")
    week_new_space = fields.Integer(string="本周新增项目空间(万元)")
    space_total = fields.Integer(string="项目空间(万元)")
    project_count = fields.Integer(string="小计(万元)")
    weekly_refresh_rate = fields.Integer("项目周刷新率(%)")
    monthly_laed_refresh_rate = fields.Integer("机会点月刷新率(%)")
    bid_amount = fields.Integer(string="中标金额(万元)")
    contract_signing_amount = fields.Integer(string="合同签订额(万元)")
    received = fields.Integer(string="已收款(万元)")
    accounts_payable = fields.Integer(string="应付款(万元)")
    bid_amount = fields.Integer(string="中标金额(万元)")
    contract_signing_amount = fields.Integer(string="合同签订额(万元)")
    received = fields.Integer(string="已收款(万元)")
    accounts_payable = fields.Integer(string="应付款(万元)")

    report_person = fields.Many2one('hr.employee','报告人',default=lambda self:self.env['hr.employee'].search([('login','=',self.env.user.login)]))
    report_person_name = fields.Char(string="报告人",compute=_compute_reportor_info,store=True)
    job_number = fields.Char(string="工号",compute=_compute_reportor_info,store=True)
    department = fields.Many2one("hr.department",string="部门",compute=_compute_reportor_info,store=True)
    week = fields.Many2one("report.week",string="周别",help="默认为当前周，可往前取三周。",domain=domain_week)
    a_week = fields.Many2one("report.week",string="周别",help="默认为当前周，可往前取三周。",domain=domain_week)
    create_system = fields.Many2many("dtdream.industry", string="行业",domain=get_system_domain,default=get_system_default)
    create_office = fields.Many2many("dtdream.office", string="办事处",domain=get_office_domain,default=get_office_default)
    create_office_ids = fields.Char(string='行业集合')
    create_system_ids = fields.Char(string="系统部集合")

    name = fields.Char('主管周报',default="主管周报")
    report_start_time = fields.Date(string="周报开始日期",compute=_onchange_week,store=True)
    report_end_time = fields.Date(string="周报结束日期",compute=_onchange_week,store=True)
    a_report_start_time = fields.Date(string="周报开始日期")
    a_report_end_time = fields.Date(string="周报结束日期")
    zhengwu_project = fields.One2many("manager.zhengwu.system.project","manager_zhengwu_project_id",copy=True)
    zhengwu_total_space = fields.Char("项目个数")
    zhengwu_total_project = fields.Float("整体空间(万元)")
    zhengwu_important_project = fields.Char("重大项目个数")
    zhengwu_important_space = fields.Float("重大整体空间(万元)")

    zhuguan_zongjie = fields.One2many("report.zongjie","zhuguan_zongjie_id",string="周报周报总结")
    zhuguan_qiuzhu = fields.One2many("report.qiuzhu","zhuguan_qiuzhu_id",string="主管求助")

    lead_project = fields.One2many("manager.lead.project","manager_lead_project_id")
    other_project = fields.One2many("manager.other.project","manager_other_project_id")
    sale_channel = fields.One2many("manager.sale.channel","manager_sale_channel_id")
    visit_customer = fields.One2many("manager.visit.customer","manager_visit_customer_id")
    competitor_situation = fields.One2many("manager.competitor.situation","manager_competitor_situation_id")
    sale_other = fields.One2many("manager.sale.other","manager_sale_other_id")

    dtdream_problem_help = fields.One2many("manager.problem.help","manager_problem_help_id")

    next_zhengwu_project = fields.One2many("manager.zhengwu.system.project","manager_next_zhengwu_project_id")

    customer_visit_plan = fields.One2many("manager.customer.visit.plan","manager_customer_visit_plan_id")

    next_sale_other = fields.One2many("manager.sale.other","manager_next_sale_other_id")
    sys_compute_lists = fields.One2many("manager.sys.list","manager_rec_id",string="系统部列表")

    complete_name = fields.Char(string="部门")
    manager_reply_list = fields.One2many("reply.list","reply_list_to_manager_report_id",string="周报批复区")
    submit_date = fields.Datetime(string="提交时间")

    # if_see_manager_report = fields.Char(string="是否可查看主管周报",default="0",compute=_compute_if_see_manager_report,store=True)

    @api.constrains("sys_compute_lists")
    def _cons_sys_compute_lists(self):
        self._onchange_compute_total()

    @api.onchange("sys_compute_lists")
    def _onchange_compute_total(self):
        bid_amount_total = 0
        contract_signing_amount_total = 0
        received_total = 0
        accounts_payable_total = 0
        for rec in self.sys_compute_lists:
            if rec.system_name != u"合计":
                bid_amount_total = bid_amount_total + rec.bid_amount
                contract_signing_amount_total = contract_signing_amount_total + rec.contract_signing_amount
                received_total = received_total + rec.received
                accounts_payable_total = accounts_payable_total + rec.accounts_payable
        if bid_amount_total > 0 :
            self.bid_amount = bid_amount_total
            self.contract_signing_amount = contract_signing_amount_total
            self.received = received_total
            self.accounts_payable = accounts_payable_total

    @api.model
    def create(self,vals):
        result = super(dtdream_sale_manager_report, self).create(vals)
        if len(result.create_office) + len(result.create_system) == 0 :
            raise ValidationError("请至少选择一个办事处或行业。")
        if len(self.env['dtdream.sale.manager.report'].search([('report_person_name','=',result.report_person_name),('week','=',result.a_week.id)])) > 0:
            raise ValidationError(u"每周只能生成一份周报。")
        return result

    @api.constrains("week")
    def _cons_week(self):
        if len(self.env['dtdream.sale.manager.report'].search([('report_person_name','=',self.report_person_name),('week','=',self.week.id)])) > 1:
            raise ValidationError("每周只能生成一份周报。")
        if datetime.weekday(datetime.now()) >= 4:
            report_end_time = datetime.now() - relativedelta(days=((datetime.weekday(datetime.now())) - 4))
            report_end_time = report_end_time
        else:
            report_end_time = datetime.now() + relativedelta(days=(4-7-datetime.weekday(datetime.now())))
            report_end_time = report_end_time
        report_start_time = report_end_time - relativedelta(days=7)
        week = int(datetime.strftime(report_end_time,"%W"))
        for rec in self:
            rec.report_start_time = report_start_time
            a_report_end_time = report_end_time - relativedelta(days=(week-int(rec.week.name))*7)
            rec.report_end_time = a_report_end_time
            rec.report_start_time = report_start_time - relativedelta(days=(week-int(rec.week.name))*7)

    @api.constrains('zhengwu_project')
    def _cons_zhengwu_project(self):
        list = []
        for rec in self.zhengwu_project:
            if rec.project_id:
                if rec.project_id.id in list:
                    raise ValidationError("近三个月招投标项目重复录入。")
            list.append(rec.project_id.id)
            if len(rec.office_id) == 0:
                rec.project_master_degree = rec.project_id.project_master_degree
                rec.bidding_time = rec.project_id.bidding_time
            rec.system_department_id = rec.project_id.system_department_id
            rec.office_id = rec.project_id.office_id
            if rec.project_id:
                rec.sale_apply_id = rec.project_id.sale_apply_id.name+"."+rec.project_id.sale_apply_id.full_name+" "+rec.project_id.sale_apply_id.job_number
            rec.space_total = rec.project_id.space_total
            rec.industry_id = rec.project_id.industry_id
            report_end_time = self.report_end_time + " 00:00:00"
            if len(rec.project_id) == 0:
                    self.zhengwu_project = [(2,rec.id)]
            if rec.project_id.project_number:
                crm_recs = self.env['crm.lead'].search([('project_number', '=', rec.project_id.project_number),('stage_id.name','in',(u'项目启动',u'技术和商务交流',u'项目招投标'))])
                if crm_recs is None or len(crm_recs) <= 0:
                    return
                crm_rec = crm_recs[0]
                if crm_rec.project_master_degree != rec.project_master_degree:
                    crm_rec.write({"project_master_degree":rec.project_master_degree})
                if crm_rec.bidding_time != rec.bidding_time:
                    crm_rec.write({"bidding_time":rec.bidding_time})
                if rec.project_process != False and rec.project_process.strip() != "":
                    flag = 0
                    for i in crm_rec.des_records:
                        if i.week == int(self.week):
                            i.name = rec.project_process
                            flag = 1
                    if flag == 0:
                        str = ""
                        for recc in crm_rec.des_records:
                            if recc.create_date[:10] <= report_end_time and recc.create_date[:10] > (datetime.strptime(report_end_time,"%Y-%m-%d %H:%M:%S") - relativedelta(days=7)).strftime('%Y-%m-%d'):
                                if recc.name != False:
                                    str = str + recc.name + u";"
                        if str != rec.project_process:
                            crm_rec.des_records.create({"name":rec.project_process,"des_id":crm_rec.id,"week":int(self.week)})
                if rec.bidding_time > (datetime.strptime(report_end_time,"%Y-%m-%d %H:%M:%S") + relativedelta(months=3)).strftime("%Y-%m-%d"):
                    self.zhengwu_project = [(2,rec.id)]

    @api.constrains('lead_project')
    def _cons_lead_project(self):
        list = []
        for rec in self.lead_project:
            if rec.project_id:
                if rec.project_id.id in list:
                    raise ValidationError("近三个月招投标机会点重复录入。")
            list.append(rec.project_id.id)
            if len(rec.office_id) == 0:
                rec.project_master_degree = rec.project_id.project_master_degree
                rec.bidding_time = rec.project_id.bidding_time
            rec.system_department_id = rec.project_id.system_department_id
            rec.office_id = rec.project_id.office_id
            if rec.project_id:
                rec.sale_apply_id = rec.project_id.sale_apply_id.name+"."+rec.project_id.sale_apply_id.full_name+" "+rec.project_id.sale_apply_id.job_number
            rec.space_total = rec.project_id.space_total
            rec.industry_id = rec.project_id.industry_id
            report_end_time = self.report_end_time + " 00:00:00"
            if len(rec.project_id) == 0:
                    self.lead_project = [(2,rec.id)]
            if rec.project_id.project_number:
                crm_recs = self.env['crm.lead'].search([('project_number','=',rec.project_id.project_number),('stage_id.name','=',u'机会点')])
                if crm_recs is None or len(crm_recs) <= 0:
                    return
                crm_rec = crm_recs[0]
                if crm_rec.project_master_degree != rec.project_master_degree:
                    crm_rec.write({"project_master_degree":rec.project_master_degree})
                if crm_rec.bidding_time != rec.bidding_time:
                    crm_rec.write({"bidding_time":rec.bidding_time})
                if rec.project_process != False and rec.project_process.strip() != "":
                    flag = 0
                    for i in crm_rec.des_records:
                        if i.week == int(self.week):
                            i.name = rec.project_process
                            flag = 1
                    if flag == 0:
                        str = ""
                        for recc in crm_rec.des_records:
                            if recc.create_date[:10] <= report_end_time and recc.create_date[:10] > (datetime.strptime(report_end_time,"%Y-%m-%d %H:%M:%S") - relativedelta(days=7)).strftime('%Y-%m-%d'):
                                if recc.name != False:
                                    str = str + recc.name + u";"
                        if str != rec.project_process:
                            crm_rec.des_records.create({"name":rec.project_process,"des_id":crm_rec.id,"week":int(self.week)})
                if rec.bidding_time > (datetime.strptime(report_end_time,"%Y-%m-%d %H:%M:%S") + relativedelta(months=3)).strftime("%Y-%m-%d"):
                    self.lead_project = [(2,rec.id)]

    @api.constrains('other_project')
    def _cons_other_project(self):
        list = []
        for rec in self.other_project:
            if rec.project_id:
                if rec.project_id.id in list:
                    raise ValidationError("含投资项目及其他重要项目进展重复录入。")
            list.append(rec.project_id.id)
            # if len(rec.office_id) == 0:
            #     rec.project_master_degree = rec.project_id.project_master_degree
            #     rec.bidding_time = rec.project_id.bidding_time
            rec.system_department_id = rec.project_id.system_department_id
            rec.office_id = rec.project_id.office_id
            if rec.project_id:
                rec.sale_apply_id = rec.project_id.sale_apply_id.name+"."+rec.project_id.sale_apply_id.full_name+" "+rec.project_id.sale_apply_id.job_number
            rec.space_total = rec.project_id.space_total
            rec.industry_id = rec.project_id.industry_id
            report_end_time = self.report_end_time + " 00:00:00"
            if len(rec.project_id) == 0:
                    self.other_project = [(2,rec.id)]
            if rec.project_id.project_number:
                crm_recs = self.env['crm.lead'].search([('project_number','=',rec.project_id.project_number)])
                if crm_recs is None or len(crm_recs) <= 0:
                    return
                crm_rec = crm_recs[0]
                for a_rec in rec.manager_other_project_id.zhengwu_project:
                    if a_rec.project_id.project_number == rec.project_id.project_number:
                        a_rec.project_master_degree = rec.project_master_degree
                        a_rec.bidding_time = rec.bidding_time
                        a_rec.project_process = rec.project_process
                for b_rec in rec.manager_other_project_id.lead_project:
                    if b_rec.project_id.project_number == rec.project_id.project_number:
                        b_rec.project_master_degree = rec.project_master_degree
                        b_rec.bidding_time = rec.bidding_time
                        b_rec.project_process = rec.project_process
                if crm_rec.project_master_degree != rec.project_master_degree:
                    crm_rec.write({"project_master_degree":rec.project_master_degree})
                if crm_rec.bidding_time != rec.bidding_time:
                    crm_rec.write({"bidding_time":rec.bidding_time})
                if rec.project_process != False and rec.project_process.strip() != "":
                    flag = 0
                    for i in crm_rec.des_records:
                        if i.week == int(self.week):
                            i.name = rec.project_process
                            flag = 1
                    if flag == 0:
                        str = ""
                        for recc in crm_rec.des_records:
                            if recc.create_date[:10] <= report_end_time and recc.create_date[:10] > (datetime.strptime(report_end_time,"%Y-%m-%d %H:%M:%S") - relativedelta(days=7)).strftime('%Y-%m-%d'):
                                if recc.name != False:
                                    str = str + recc.name + u";"
                        if str != rec.project_process:
                            crm_rec.des_records.create({"name":rec.project_process,"des_id":crm_rec.id,"week":int(self.week)})

    @api.constrains('next_zhengwu_project')
    def _cons_next_zhengwu_project(self):
        list = []
        for rec in self.next_zhengwu_project:
            if rec.project_id:
                if rec.project_id.id in list:
                    raise ValidationError("重大项目下周计划重复录入。")
            list.append(rec.project_id.id)
            if len(rec.office_id) == 0:
                rec.project_master_degree = rec.project_id.project_master_degree
                rec.bidding_time = rec.project_id.bidding_time
            rec.system_department_id = rec.project_id.system_department_id
            rec.office_id = rec.project_id.office_id
            if rec.project_id:
                rec.sale_apply_id = rec.project_id.sale_apply_id.name+"."+rec.project_id.sale_apply_id.full_name+" "+rec.project_id.sale_apply_id.job_number
            rec.space_total = rec.project_id.space_total
            rec.industry_id = rec.project_id.industry_id
            report_end_time = self.report_end_time + " 00:00:00"
            if len(rec.project_id) == 0:
                    self.next_zhengwu_project = [(2,rec.id)]
            if rec.project_id.project_number:
                crm_recs = self.env['crm.lead'].search([('project_number','=',rec.project_id.project_number)])
                if crm_recs is None or len(crm_recs) <= 0:
                    return
                crm_rec = crm_recs[0]
                if crm_rec.project_master_degree != rec.project_master_degree:
                    crm_rec.write({"project_master_degree":rec.project_master_degree})
                if crm_rec.bidding_time != rec.bidding_time:
                    crm_rec.write({"bidding_time":rec.bidding_time})
                if rec.project_process != False and rec.project_process.strip() != "":
                    flag = 0
                    for i in crm_rec.des_records:
                        if i.week == int(self.week):
                            i.name = rec.project_process
                            flag = 1
                    if flag == 0:
                        str = ""
                        for recc in crm_rec.des_records:
                            if recc.create_date[:10] <= report_end_time and recc.create_date[:10] > (datetime.strptime(report_end_time,"%Y-%m-%d %H:%M:%S") - relativedelta(days=7)).strftime('%Y-%m-%d'):
                                if recc.name != False:
                                    str = str + recc.name + u";"
                        if str != rec.project_process:
                            crm_rec.des_records.create({"name":rec.project_process,"des_id":crm_rec.id,"week":int(self.week)})

    @api.one
    def new_report(self):
        self.week = self.a_week
        self.report_end_time = self.a_report_end_time
        self.report_start_time = self.a_report_start_time
        self.compute_project_info(self.a_week.name)
        self.write({'state':'1'})

    def compute_project_info(self,week):
        create_office_ids = [rec.id for rec in self.create_office]
        system_department_ids = [recc.id for recc in self.create_system]
        self.create_office_ids = str(create_office_ids)[1:-1]
        self.create_system_ids = str(system_department_ids)[1:-1]
        week = str(week)
        # 近三个月招投标项目
        sql = "select z.id from zhengwu_system_project z left join dtdream_sale_own_report d on z.zhengwu_project_id = d.id where d.state = 'submit' and d.week = " + week
        self._cr.execute(sql)
        result = self._cr.fetchall()
        res_ids = [rec[0] for rec in result]
        zhengwu_project = self.env['zhengwu.system.project'].search([('id','in',res_ids),('office_id.id','in',create_office_ids),('industry_id.id','in',system_department_ids)])
        list = []
        list_pro_ids = []
        if len(zhengwu_project) > 0:
            for rec in zhengwu_project:
                if rec.project_id.stage_id.name in (u'项目启动',u'技术和商务交流',u'项目招投标') and rec.project_id.active != False and rec.project_id not in list_pro_ids:
                    list_pro_ids.append(rec.project_id)
                    list.append((0,0,{"project_id":rec.project_id,"office_id":rec.office_id,"sale_apply_id":rec.sale_apply_id,"space_total":rec.space_total,
                                  "project_master_degree":rec.project_master_degree,"bidding_time":rec.bidding_time,"project_number":rec.project_number,
                                  "project_process":rec.project_process,'project_leave':rec.project_leave,'system_department_id':rec.system_department_id,'industry_id':rec.industry_id}))
        self.zhengwu_project = list or False
        # 近三个月招投标机会点
        sql = "select z.id from lead_project z left join dtdream_sale_own_report d on z.lead_project_id = d.id where d.state = 'submit' and d.week = " + week
        self._cr.execute(sql)
        result = self._cr.fetchall()
        res_ids = [rec[0] for rec in result]
        lead_project = self.env['lead.project'].search([('id','in',res_ids),('office_id.id','in',create_office_ids),('industry_id.id','in',system_department_ids)])
        list = []
        list_lead_ids = []
        if len(lead_project) > 0:
            for rec in lead_project:
                if rec.project_id.stage_id.name == u'机会点' and rec.project_id.active != False and rec.project_id not in list_lead_ids:
                    list_lead_ids.append(rec.project_id)
                    list.append((0,0,{"project_id":rec.project_id,"office_id":rec.office_id,"sale_apply_id":rec.sale_apply_id,"space_total":rec.space_total,
                                  "project_master_degree":rec.project_master_degree,"bidding_time":rec.bidding_time,"project_number":rec.project_number,
                                  "project_process":rec.project_process,'system_department_id':rec.system_department_id,'industry_id':rec.industry_id}))
        self.lead_project = list or False
        # 含投资项目及其他重要项目进展
        sql = "select z.id from other_project z left join dtdream_sale_own_report d on z.other_project_id = d.id where d.state = 'submit' and d.week = " + week
        self._cr.execute(sql)
        result = self._cr.fetchall()
        res_ids = [rec[0] for rec in result]
        other_project = self.env['other.project'].search([('id','in',res_ids),('office_id.id','in',create_office_ids),('industry_id.id','in',system_department_ids)])
        list = []
        if len(other_project) > 0:
            for rec in other_project:
                list.append((0,0,{"project_id":rec.project_id,"office_id":rec.office_id,"sale_apply_id":rec.sale_apply_id,"space_total":rec.space_total,
                              "project_master_degree":rec.project_master_degree,"bidding_time":rec.bidding_time,"project_number":rec.project_number,
                              "project_process":rec.project_process,'system_department_id':rec.system_department_id,'industry_id':rec.industry_id}))
        self.other_project = list or False
        # 重点客户高层拜访
        sql = "select z.id from visit_customer z left join dtdream_sale_own_report d on z.visit_customer_id = d.id where d.state = 'submit' and d.week = " + week
        self._cr.execute(sql)
        result = self._cr.fetchall()
        res_ids = [rec[0] for rec in result]
        visit_customer = self.env['visit.customer'].search([('id','in',res_ids),('office_id.id','in',create_office_ids),('industry_id.id','in',system_department_ids)])
        list = []
        if len(visit_customer) > 0:
            for rec in visit_customer:
                list.append((0,0,{"partner_id":rec.partner_id,"system_department_id":rec.system_department_id,"office_id":rec.office_id,"visit_date":rec.visit_date,
                              "visit_object":rec.visit_object,"content":rec.content,"next_plan":rec.next_plan,"ask_help":rec.ask_help,'send_person':rec.send_person,'industry_id':rec.industry_id}))
        self.visit_customer = list or False
        # 重大项目下周计划
        sql = "select z.id from zhengwu_system_project z left join dtdream_sale_own_report d on z.next_zhengwu_project_id = d.id where d.state = 'submit' and d.week = " + week
        self._cr.execute(sql)
        result = self._cr.fetchall()
        res_ids = [rec[0] for rec in result]
        next_zhengwu_project = self.env['zhengwu.system.project'].search([('id','in',res_ids),('office_id.id','in',create_office_ids),('industry_id.id','in',system_department_ids)])
        list = []
        if len(next_zhengwu_project) > 0:
            for rec in next_zhengwu_project:
                list.append((0,0,{"project_id":rec.project_id,"office_id":rec.office_id,"sale_apply_id":rec.sale_apply_id,"space_total":rec.space_total,
                              "project_master_degree":rec.project_master_degree,"bidding_time":rec.bidding_time,"project_number":rec.project_number,
                              "project_process":rec.project_process,'next_process':rec.next_process,'system_department_id':rec.system_department_id,'industry_id':rec.industry_id}))
        self.next_zhengwu_project = list or False
        # 重点客户拜访计划
        sql = "select z.id from customer_visit_plan z left join dtdream_sale_own_report d on z.customer_visit_plan_id = d.id where d.state = 'submit' and d.week = " + week
        self._cr.execute(sql)
        result = self._cr.fetchall()
        res_ids = [rec[0] for rec in result]
        customer_visit_plan = self.env['customer.visit.plan'].search([('id','in',res_ids),('office_id.id','in',create_office_ids),('industry_id.id','in',system_department_ids)])
        list = []
        if len(customer_visit_plan) > 0:
            for rec in customer_visit_plan:
                list.append((0,0,{"partner_id":rec.partner_id,"system_department_id":rec.system_department_id,"office_id":rec.office_id,"visit_date":rec.visit_date,
                              "visit_object":rec.visit_object,"content":rec.content,'industry_id':rec.industry_id}))
        self.customer_visit_plan = list or False

class report_zongjie(models.Model):
    _name = "report.zongjie"

    zhuguan_zongjie_id = fields.Many2one("dtdream.sale.manager.report",string="关联主管周报")
    week_zongjie = fields.Text(string="本周进展总结")
    week_important = fields.Text(string="本周重要事项")
    next_week_plan = fields.Text(string="下周工作计划")

class report_qiuzhu(models.Model):
    _name = "report.qiuzhu"

    zhuguan_qiuzhu_id = fields.Many2one("dtdream.sale.manager.report",string="关联主管周报")
    problem_description = fields.Text(string="问题描述(需公司层面解决的重要问题/求助)")
    problem_content = fields.Text(string="问题的求助内容")

# 渠道进展
class manager_sale_channel(models.Model):
    _name = 'manager.sale.channel'
    _description = u"渠道进展"

    @api.onchange("name")
    @api.depends('name')
    def compute_info_by_name(self):
        for i in self:
            if i.name:
                recs = i.env['crm.lead'].search(['&',('sale_channel','like',("%"+i.name+"%")),"|",('type','=','lead'),'&',('stage_id.name','in',(u'项目启动',u'技术和商务交流',u'项目招投标',u'中标')),('type','=','opportunity')])
                space_total = 0
                for rec in recs:
                    space_total = space_total + rec.space_total
                i.project_total = len(recs)
                i.project_space_total = space_total

    manager_sale_channel_id = fields.Many2one("dtdream.sale.manager.report",string="主管周报")
    name = fields.Char("渠道名称")
    project_total = fields.Integer("关联项目个数",compute=compute_info_by_name,store=True)
    project_space_total = fields.Integer("关联项目空间(万元)",compute=compute_info_by_name,store=True)
    channer_process = fields.Text("渠道拓展进展")


# 客户拜访
class manager_visit_customer(models.Model):
    _name = 'manager.visit.customer'
    _description = u"客户拜访"

    @api.onchange("partner_id")
    @api.depends("partner_id")
    def _onchange_partner_id(self):
        for rec in self:
            rec.system_department_id = rec.partner_id.system_department_id
            rec.industry_id = rec.partner_id.industry_id
            rec.office_id = rec.partner_id.office_id

    manager_visit_customer_id = fields.Many2one("dtdream.sale.manager.report",string="主管周报")

    partner_id = fields.Many2one("res.partner","客户名称")
    system_department_id = fields.Many2one("dtdream.industry", string="系统部",compute=_onchange_partner_id,store=True)
    industry_id = fields.Many2one("dtdream.industry",string="行业",compute=_onchange_partner_id,store=True)
    visit_date = fields.Date(string="拜访时间")
    visit_object = fields.Char(string="拜访对象")
    content = fields.Text(string="交流主要内容")
    next_plan = fields.Text(string="下一步计划")
    ask_help = fields.Char(string="困难求助")
    send_person = fields.Many2many("hr.employee",string="发送对象")
    office_id = fields.Many2one("dtdream.office", string="办事处",compute=_onchange_partner_id,store=True)


# 重点客户(含阿里)拜访计划
class manager_customer_visit_plan(models.Model):
    _name = 'manager.customer.visit.plan'
    _description = u"重点客户(含阿里)拜访计划"

    @api.onchange("partner_id")
    @api.depends("partner_id")
    def _onchange_partner_id(self):
        for rec in self:
            rec.system_department_id = rec.partner_id.system_department_id
            rec.industry_id = rec.partner_id.industry_id
            rec.office_id = rec.partner_id.office_id

    manager_customer_visit_plan_id = fields.Many2one("dtdream.sale.manager.report",string="主管周报")

    partner_id = fields.Many2one("res.partner","客户名称")
    system_department_id = fields.Many2one("dtdream.industry", string="系统部",compute=_onchange_partner_id,store=True)
    visit_date = fields.Date(string="预计拜访时间")
    visit_object = fields.Char(string="拜访对象")
    content = fields.Text(string="交流主要内容")
    office_id = fields.Many2one("dtdream.office", string="办事处",compute=_onchange_partner_id,store=True)
    industry_id = fields.Many2one("dtdream.industry",string="行业",compute=_onchange_partner_id,store=True)

# 竞争对手情况
class manager_competitor_situation(models.Model):
    _name = 'manager.competitor.situation'
    _description = u"竞争对手情况"

    manager_competitor_situation_id = fields.Many2one("dtdream.sale.manager.report",string="主管周报")

    name = fields.Char("友商名称")
    recent_dynamics = fields.Char("最近动态")
    compute_strategy = fields.Char("我司竞争策略")

# 其他
class manager_sale_other(models.Model):
    _name = 'manager.sale.other'
    _description = u"其他重要事项"

    manager_sale_other_id = fields.Many2one("dtdream.sale.manager.report",string="主管周报")
    manager_next_sale_other_id = fields.Many2one("dtdream.sale.manager.report",string="主管周报")

    name = fields.Text("其他重要事项描述")
    week_process = fields.Text("下周工作计划")

class manager_problem_help(models.Model):
    _name = "manager.problem.help"
    _description = u"问题与求助"

    manager_problem_help_id = fields.Many2one("dtdream.sale.manager.report",string="主管周报")
    name = fields.Char("问题详情")
    type = fields.Many2one('problem.type',string="问题类型")
    report_help_people = fields.Many2many("hr.employee",string="求助对象")

# 重大机会点
class manager_lead_project(models.Model):
    _name = 'manager.lead.project'
    _description = u"重大机会点"

    manager_lead_project_id = fields.Many2one("dtdream.sale.manager.report",string="主管周报")

    @api.onchange('project_id')
    def _compute_project_info(self):
        for rec in self:
            if rec.project_id.id == False:
                date = rec.manager_lead_project_id.report_end_time+" 00:00:00"
                return {
                    'domain': {
                        "project_id":[('type','=','lead'),('bidding_time','<=',(datetime.strptime(date,"%Y-%m-%d %H:%M:%S")+ relativedelta(months=3)).strftime("%Y-%m-%d"))]
                    }
                }
            rec.office_id = rec.project_id.office_id
            if rec.project_id:
                rec.sale_apply_id = rec.project_id.sale_apply_id.name+"."+rec.project_id.sale_apply_id.full_name+" "+rec.project_id.sale_apply_id.job_number
            rec.space_total = rec.project_id.space_total
            rec.project_master_degree = rec.project_id.project_master_degree
            rec.bidding_time = rec.project_id.bidding_time
            rec.project_number = rec.project_id.project_number
            rec.system_department_id = rec.project_id.system_department_id
            if datetime.weekday(datetime.now()) >= 4:
                report_end_time = datetime.now() - relativedelta(days=((datetime.weekday(datetime.now())) - 4))
            else:
                report_end_time = datetime.now() + relativedelta(days=(4-7-datetime.weekday(datetime.now())))
            str = ""
            for recc in rec.project_id.des_records:
                if recc.create_date[:10] <= report_end_time.strftime('%Y-%m-%d') and recc.create_date[:10] > (report_end_time - relativedelta(days=7)).strftime('%Y-%m-%d'):
                    if recc.name != False and recc.week != rec.manager_lead_project_id.week.id:
                        str = str + recc.name + u";"
            rec.project_process = str

    office_id = fields.Many2one("dtdream.office", string="办事处")
    project_id = fields.Many2one('crm.lead',string="项目名称")
    sale_apply_id = fields.Char(string="营销责任人")
    space_total = fields.Integer(string="项目空间(万元)")
    project_master_degree = fields.Selection([
        ('1', 'A'),
        ('2', 'B'),
        ('3', 'C'),
        ('4', 'D'),
    ],'项目把握度')
    bidding_time = fields.Date(string="招标时间")
    project_process = fields.Text(string="上周项目进展")
    project_number = fields.Char(string="项目编号")
    system_department_id = fields.Many2one("dtdream.industry", string="系统部")
    industry_id = fields.Many2one("dtdream.industry",string="行业")
    project_leave = fields.Char(string="项目级别")

# 政务系统部项目
class manager_zhengwu_system_project(models.Model):
    _name = 'manager.zhengwu.system.project'
    _description = u"近三个月招投标项目"

    manager_zhengwu_project_id = fields.Many2one("dtdream.sale.manager.report",string="主管周报")
    manager_next_zhengwu_project_id = fields.Many2one("dtdream.sale.manager.report",string="主管周报")

    @api.onchange('project_id')
    def _onchange_project_info(self):
        for rec in self:
            if rec.project_id.id == False and rec.manager_zhengwu_project_id.id != False:
                date = rec.manager_zhengwu_project_id.report_end_time+" 00:00:00"
                return {
                    'domain': {
                        "project_id":[('type','=','opportunity'),('bidding_time','<=',(datetime.strptime(date,"%Y-%m-%d %H:%M:%S")+ relativedelta(months=3)).strftime("%Y-%m-%d"))]
                    }
                }
            rec.office_id = rec.project_id.office_id
            rec.industry_id = rec.project_id.industry_id
            if rec.project_id:
                rec.sale_apply_id = rec.project_id.sale_apply_id.name+"."+rec.project_id.sale_apply_id.full_name+" "+rec.project_id.sale_apply_id.job_number
            rec.space_total = rec.project_id.space_total
            rec.project_master_degree = rec.project_id.project_master_degree
            rec.bidding_time = rec.project_id.bidding_time
            rec.project_number = rec.project_id.project_number
            rec.project_leave = rec.project_id.project_leave
            rec.system_department_id = rec.project_id.system_department_id
            if datetime.weekday(datetime.now()) >= 4:
                report_end_time = datetime.now() - relativedelta(days=((datetime.weekday(datetime.now())) - 4))
            else:
                report_end_time = datetime.now() + relativedelta(days=(4-7-datetime.weekday(datetime.now())))
            str = ""
            for recc in rec.project_id.des_records:
                if recc.create_date[:10] <= report_end_time.strftime('%Y-%m-%d') and recc.create_date[:10] > (report_end_time - relativedelta(days=7)).strftime('%Y-%m-%d'):
                    if rec.manager_zhengwu_project_id and recc.name != False and recc.week != rec.manager_zhengwu_project_id.week.id:
                        str = str + recc.name + u";"
                    if rec.manager_next_zhengwu_project_id and recc.name != False and recc.week != rec.manager_next_zhengwu_project_id.week.id:
                        str = str + recc.name + u";"
            rec.project_process = str

    office_id = fields.Many2one("dtdream.office", string="办事处",store=True)
    project_id = fields.Many2one('crm.lead',string="项目名称")
    sale_apply_id = fields.Char(string="营销责任人")
    space_total = fields.Integer(string="项目空间(万元)")
    project_master_degree = fields.Selection([
        ('1', 'A'),
        ('2', 'B'),
        ('3', 'C'),
        ('4', 'D'),
    ],'项目把握度')
    bidding_time = fields.Date(string="招标时间")
    project_process = fields.Text(string="上周项目进展")
    next_process = fields.Text(string="下周项目计划")
    project_number = fields.Char(string="项目编号")
    project_leave = fields.Char(string="项目级别")
    system_department_id = fields.Many2one("dtdream.industry", string="系统部",store=True)
    industry_id = fields.Many2one("dtdream.industry",string="行业",store=True)

# 含投资项目及其他重要项目进展
class manager_other_project(models.Model):
    _name = 'manager.other.project'
    _description = u"含投资项目及其他重要项目进展"

    manager_other_project_id = fields.Many2one("dtdream.sale.manager.report",string="主管周报")

    @api.onchange('project_id')
    def _compute_project_info(self):
        for rec in self:
            rec.office_id = rec.project_id.office_id
            if rec.project_id:
                rec.sale_apply_id = rec.project_id.sale_apply_id.name+"."+rec.project_id.sale_apply_id.full_name+" "+rec.project_id.sale_apply_id.job_number
            rec.industry_id = rec.project_id.industry_id
            rec.space_total = rec.project_id.space_total
            rec.project_master_degree = rec.project_id.project_master_degree
            rec.bidding_time = rec.project_id.bidding_time
            rec.project_number = rec.project_id.project_number
            rec.system_department_id = rec.project_id.system_department_id
            if datetime.weekday(datetime.now()) >= 4:
                report_end_time = datetime.now() - relativedelta(days=((datetime.weekday(datetime.now())) - 4))
            else:
                report_end_time = datetime.now() + relativedelta(days=(4-7-datetime.weekday(datetime.now())))
            str = ""
            for recc in rec.project_id.des_records:
                if recc.create_date[:10] <= report_end_time.strftime('%Y-%m-%d') and recc.create_date[:10] > (report_end_time - relativedelta(days=7)).strftime('%Y-%m-%d'):
                    if recc.name != False and recc.week != rec.manager_other_project_id.week.id:
                        str = str + recc.name + u";"
            rec.project_process = str

    def domain_other_project(self):
        return [('is_invest_project','=','1')]

    office_id = fields.Many2one("dtdream.office", string="办事处")
    project_id = fields.Many2one('crm.lead',string="项目名称",domain=domain_other_project)
    industry_id = fields.Many2one("dtdream.industry",string="行业")
    sale_apply_id = fields.Char(string="营销责任人")
    space_total = fields.Integer(string="项目空间(万元)")
    project_master_degree = fields.Selection([
        ('1', 'A'),
        ('2', 'B'),
        ('3', 'C'),
        ('4', 'D'),
    ],'项目把握度')
    bidding_time = fields.Date(string="招标时间")
    project_process = fields.Text(string="上周项目进展")
    project_number = fields.Char(string="项目编号")
    system_department_id = fields.Many2one("dtdream.industry", string="系统部")

class manager_sys_list(models.Model):
    _name = "manager.sys.list"

    manager_rec_id = fields.Many2one("dtdream.sale.manager.report")
    project_total = fields.Integer(string="项目个数")
    space_total = fields.Integer(string="项目空间(万元)")
    important_project = fields.Integer(string="重大项目个数")
    important_space = fields.Integer(string="重大项目空间(万元)")
    lead_project_total = fields.Integer(string="机会点个数")
    lead_space_total = fields.Integer(string="机会点空间(万元)")
    lead_important_project = fields.Integer(string="重大机会点个数")
    lead_important_space = fields.Integer(string="重大机会点空间(万元)")
    system_name = fields.Char(string="系统部")
    project_count = fields.Integer(string="小计(万元)")
    week_new_space = fields.Integer(string="本周新增项目空间(万元)")
    weekly_refresh_rate = fields.Integer("项目周刷新率(%)")
    monthly_laed_refresh_rate = fields.Integer("机会点月刷新率(%)")
    bid_amount = fields.Integer(string="中标金额(万元)")
    contract_signing_amount = fields.Integer(string="合同签订额(万元)")
    received = fields.Integer(string="已收款(万元)")
    accounts_payable = fields.Integer(string="应付款(万元)")

    @api.onchange("bid_amount","contract_signing_amount","accounts_payable","received")
    def _check_integer(self):
        if self.bid_amount < 0 :
            self.bid_amount = False
            return {'warning': {
                "title": u"提示",
                "message": u"请勿输入负值"
            }}
        if self.contract_signing_amount < 0 :
            self.contract_signing_amount = 0
            return {'warning': {
                "title": u"提示",
                "message": u"请勿输入负值"
            }}
        if self.accounts_payable < 0 :
            self.accounts_payable = 0
            return {'warning': {
                "title": u"提示",
                "message": u"请勿输入负值"
            }}
        if self.received < 0 :
            self.received = 0
            return {'warning': {
                "title": u"提示",
                "message": u"请勿输入负值"
            }}
