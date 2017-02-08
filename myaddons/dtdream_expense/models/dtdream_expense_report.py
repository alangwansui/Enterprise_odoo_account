# -*- coding: utf-8 -*-

from openerp import models, fields, api,exceptions
from datetime import datetime, time
from openerp .exceptions import ValidationError,Warning
import time
from lxml import etree

import logging

_logger = logging.getLogger(__name__)


class dtdream_travel_journey(models.Model):
    _inherit = "dtdream.travel.journey"

    report_ids = fields.Many2many("dtdream.expense.report", 'travel_journey_expense_report_ref','report_id','journey_id', string="报销单ID")


# 报销单模型
class dtdream_expense_report(models.Model):
    _name = "dtdream.expense.report"
    _inherit = ['mail.thread']
    _description = u"报销单"

    def _get_default_val(self):
        if self.env['hr.employee'].search([('login', '=', self.env.user.login)]).department_id.assitant_id:
            return self.env['hr.employee'].search([('login', '=', self.env.user.login)]).department_id.assitant_id[0].id

    job_number = fields.Char(string=u"员工工号",default=lambda self:self.env['hr.employee'].search([('login','=',self.env.user.login)]).job_number)
    full_name = fields.Char(string=u"姓名", default=lambda self: self.env['hr.employee'].search( [('login', '=', self.env.user.login)]).full_name)
    work_place = fields.Char(string=u"工作常驻地", default=lambda self:  self.env['hr.employee'].search( [('login', '=', self.env.user.login)]).work_place)
    department_id = fields.Many2one('hr.department', string=u'所属部门',default=lambda self: self.env['hr.employee'].search( [('login', '=', self.env.user.login)]).department_id)
    department_number = fields.Char(string=u"部门编码",default=lambda self: self.env['hr.employee'].search( [('login', '=', self.env.user.login)]).department_id.code)
    paytype = fields.Selection([('yinhangzhuanzhang',u'银行转账'),('hexiaobeiyongjin',u'核销备用金')],string=u"支付方式",default = 'yinhangzhuanzhang')
    paycatelog = fields.Selection([('fukuangeiyuangong',u'付款给员工'),('fukuangeigongyingshang',u'付款给供应商')],string=u"支付类别",required=True,default='fukuangeiyuangong')
    shoukuanrenxinming = fields.Char(string=u'收款人姓名',default=lambda self:self.env['hr.employee'].search( [('login', '=', self.env.user.login)]).full_name)
    kaihuhang = fields.Char(string="开户行",default=lambda self:self.env['hr.employee'].search([('login', '=', self.env.user.login)]).bankaddr)
    yinhangkahao = fields.Char(string=u'银行卡号',default=lambda  self:self.env['hr.employee'].search([('login', '=', self.env.user.login)]).bankcardno)
    expensereason = fields.Text(string=u'报销事由')
    name = fields.Char(string=u'单据号')
    title = fields.Char(string=u"标题", default=lambda self: self.env['hr.employee'].search([('login', '=', self.env.user.login)]).name + u"的报销单")
    benefitdep_ids  =fields.One2many("dtdream.expense.benefitdep","report_id",string=u"受益部门分摊比例")
    project_ids = fields.One2many("dtdream.expense.project","report_id",string="项目分摊比例")

    @api.constrains('project_ids')
    def check_project_ids(self):
        if self.project_ids:
            crm_lead_list = []
            total_percent = 0
            for rec in self.project_ids:
                crm_lead_list.append(rec.name.id)
                total_percent += rec.share_percent
            if len(crm_lead_list) != len(set(crm_lead_list)):
                raise ValidationError("不能有重复的项目!")
            else:
                if total_percent != 100:
                    raise ValidationError("项目分摊比例之和必须为100%！")
    record_ids=fields.Many2many('dtdream.expense.record','dtdream_exprense_record_report_ref','record_id','report_id',u'费用明细')
    state = fields.Selection([('draft', u'草稿'), ('xingzheng', u'行政助理审批'), ('zhuguan', u'主管审批'), ('quanqianren', u'权签人审批'),('jiekoukuaiji', u'接口会计审批'), ('daifukuan', u'待付款'),
                              ('yifukuan', u'已付款')], string="状态", default="draft")
    jiekou_approve_time = fields.Datetime(string="接口会计审批时间")
    xingzhengzhuli = fields.Many2one("hr.employee",string=u"部门行政助理",default=_get_default_val,
                                     domain=lambda self:[('id','in',[x.id for x in self.env['hr.employee'].search([('user_id', '=',self.env.user.id)]).department_id.assitant_id])])
    currentauditperson = fields.Many2one("hr.employee",string=u"当前处理人")
    create_uid_self = fields.Many2one("res.users",string=u"申请人",default=lambda self: self.env.user.id)
    chuchaishijian_ids = fields.Many2many('dtdream.travel.journey', 'travel_journey_expense_report_ref','journey_id','report_id', u'出差时间',domain=lambda self:[('travel_id.state','=','99'),('travel_id.name.user_id','=',self.env.user.id)])
    can_pass_jiekoukuaiji = fields.Char(string=u'权签人审批后是否到接口会计', default="0")
    xingzheng2who = fields.Char(string='行政助理到谁',help='1到主管，2到权签人，3到接口会计')
    zhuguan_quanqian_jiekoukuaiji = fields.Char(string=u'主管到权签还是接口会计(1:权签,2:接口会计)', default="0")
    which_quanqianren = fields.Char(string='当前是第几权签人审批',help="1：第一权签人，2：第二权签人，3：总裁")
    hasauditor = fields.Many2many("hr.employee",string=u"已审批过的人")
    showcuiqian= fields.Char(string=u'是否已签收', default="0")
    followers_user = fields.Many2many("res.users", "dtdream_expense_followers", string="关注者")
    batch = fields.Char(string='批次')
    @api.onchange("record_ids")
    def compute_if_display_zhuanxiang(self):
        if self.record_ids:
            if self.record_ids[0].expensedetail.parentid.name == u"专项业务费":
                self.if_display_zhuanxiang = 1
            else:
                self.if_display_zhuanxiang = 0
        else:
            self.if_display_zhuanxiang = 0
    if_display_zhuanxiang = fields.Integer(string='是否关联专项',help='1关联，0不关联',compute=compute_if_display_zhuanxiang)
    budget_id = fields.Many2one('dtdream.budget',string="预算月份",domain=lambda self:[('applicant.user_id','=',self.env.user.id),('state','=','4')])

    @api.depends('budget_id')
    def get_budget_info(self):
        for report in self:
            if report.budget_id:
                report.budget_mobile = report.budget_id.fee_travel.travel_mobile
                report.budget_bus = report.budget_id.fee_travel.travel_bus
                report.budget_travel = report.budget_id.fee_travel.travel_travel
                report.budget_daily = report.budget_id.fee_daily_total
                report.budget_zhuanx = report.budget_id.fee_zhuanx_total
                report.budget_xingz = report.budget_id.fee_xingz_total
    budget_mobile = fields.Integer(string='手机话费（元）',compute=get_budget_info, store=True)
    budget_bus = fields.Integer(string='市内交通费（元）',compute=get_budget_info, store=True)
    budget_travel = fields.Integer(string='差旅费（元）',compute=get_budget_info, store=True)
    budget_daily = fields.Integer(string='日常业务费（元）',compute=get_budget_info, store=True)
    budget_zhuanx = fields.Integer(string='专项业务费（元）',compute=get_budget_info, store=True)
    budget_xingz = fields.Integer(string='行政平台费（元）',compute=get_budget_info, store=True)
    zhuanxiang_id = fields.Many2one('dtdream.special.approval',string="专项编号",domain=lambda self:[('applicant.user_id','=',self.env.user.id),('state','=','state_05')])

    @api.depends('zhuanxiang_id')
    def get_zhuanxiang_info(self):
        list = []
        for report in self:
            if report.zhuanxiang_id.fee_ids:
                for rec in report.zhuanxiang_id.fee_ids:
                    list.append((0,0,{'fee_type':dict(rec._columns['fee_type'].selection)[rec.fee_type],'fee_amount':rec.money,'fee_description':rec.remark}))
                report.zhuanxiang_fee_ids = list

    zhuanxiang_fee_ids = fields.Many2many('dtdream.expense.zhuanx.record',string='专项费用明细',compute=get_zhuanxiang_info,store=True)

    @api.onchange('create_uid_self')
    def _xingzhengzhuli_domain(self):
        assitand = self.department_id.assitant_id
        _logger.info("----->assitand:"+str(assitand))
        ancestors = []
        if assitand:
            # self.xingzhengzhuli = assitand[0]
            for x in assitand:
                ancestors.append(x.id)
            return {'domain': {'xingzhengzhuli': [('id', 'in', ancestors)]}}
        else:
            # self.xingzhengzhuli = False
            return {'domain': {'xingzhengzhuli': [('id', '=', False)]}}


    @api.constrains('message_follower_ids')
    def _compute_follower(self):
        self.followers_user = False
        for foll in self.message_follower_ids:
            self.write({'followers_user': [(4,foll.partner_id.user_ids.id)]})
            # 关注者删除方法重写

    @api.multi
    def message_unsubscribe(self, partner_ids=None, channel_ids=None, ):
        if not partner_ids and not channel_ids:
            return True
        user_pid = self.env.user.partner_id.id
        if not channel_ids and set(partner_ids) == set([user_pid]):
            self.check_access_rights('read')
            self.check_access_rule('read')
        else:
            self.check_access_rights('write')
            self.check_access_rule('write')
        self.env['mail.followers'].sudo().search([
            ('res_model', '=', self._name),
            ('res_id', 'in', self.ids),
            '|',
            ('partner_id', 'in', partner_ids or []),
            ('channel_id', 'in', channel_ids or [])
        ]).unlink()
        self._compute_follower()

    @api.depends('create_uid_self')
    def _compute_is_zongcai(self):
        for report in self:
            zongcai_id = self.get_user_id(self.get_company_president())
            if self.create_uid_self.id == zongcai_id:
                report.is_zongcai = True
            else:
                report.is_zongcai = False

    is_zongcai=fields.Boolean(u'是否总裁',compute=_compute_is_zongcai)


    @api.onchange('create_uid_self')
    def _onchange_create_uid_self(self):

        iszongcai = False
        return {
            # 'is_zongcai':iszongcai,
            'domain': {
            'record_ids': lambda self: [('create_uid', '=', self.create_uid_self.id), ('report_ids', '=', False)]
        }}


    @api.onchange('create_uid_self')
    def _onchange_create_uid_self(self):
        for report in self:
            if report.create_uid_self:
                report.benefitdep_ids=[(0,0,{
                    'name': self.env['hr.employee'].search( [('login', '=', self.env.user.login)]).department_id.id,
                    'sharepercent':100
                })]

    def getMonth(self,da):
        return str(da)[5:7]
    def getYear(self,da):
        return str(da)[0:4]


    @api.constrains("record_ids")
    def check_length(self):
        records = []
        if not self.record_ids:
            raise ValidationError("请至少保持一条消费明细。")
        for rec in self.record_ids:
            records.append(rec.expensedetail.parentid.id)
        if len(set(records))>1:
            raise ValidationError("请检查费用明细，费用类别必须相同！")

    @api.multi
    @api.depends('record_ids')
    def _compute_total_koujianamount(self):
        for report in self:
            if report.state == "draft" or report.state == "jiekoukuaiji":
                koujian = 0.0
                invoice = 0.0
                #计算消费明细扣罚金额
                if report.record_ids:
                    # 建单日期
                    if not report.create_date:
                        createdate = datetime.now().strftime('%Y-%m-%d')
                    else:
                        createdate = datetime.strptime(report.create_date, '%Y-%m-%d %H:%M:%S')

                    for rd in report.record_ids:
                        maxdate = datetime.strptime(rd.currentdate, '%Y-%m-%d')
                        months = (int(self.getYear(createdate)) - int(self.getYear(maxdate))) * 12 + \
                                 (int(self.getMonth(createdate)) - int(self.getMonth(maxdate))) - 1
                        if months <= 1:
                            xishu = 1
                        elif months > 1 and months <= 2:
                            xishu = 0.97
                        elif months > 2 and months <= 3:
                            xishu = 0.96
                        elif months > 3 and months <= 4:
                            xishu = 0.94
                        elif months > 4 and months <= 5:
                            xishu = 0.92
                        elif months > 5 and months <= 6:
                            xishu = 0.90
                        elif months > 6:
                            xishu = 0
                        if months < 0:
                            months = 0

                        # if xishu != 1:
                        r_shibaoamount = (rd.invoicevalue-rd.kuanji_koujian) * xishu
                        r_koujianamount = rd.invoicevalue - r_shibaoamount - rd.kuanji_koujian
                        # rd._cr.execute("update dtdream_expense_record set outtimenumber = %s,koujianamount = %s,shibaoamount = %s",(months,r_koujianamount,r_shibaoamount))
                        rd.write({'outtimenumber':months,'koujianamount':r_koujianamount,'shibaoamount':r_shibaoamount})
                        koujian += rd.koujianamount + rd.kuanji_koujian
                        invoice += rd.invoicevalue
                report.total_koujianamount = koujian
                report.total_invoicevalue = invoice
                report.total_shibaoamount = report.total_invoicevalue - report.total_koujianamount

    total_invoicevalue = fields.Float(digits=(11, 2), string=u"票据总金额(元)",store=True,compute=_compute_total_koujianamount)
    total_koujianamount = fields.Float(digits=(11, 2), string=u"扣减总金额(元)",store=True,compute=_compute_total_koujianamount)
    total_shibaoamount = fields.Float(digits=(11, 2), string=u"实报总金额(元)",store=True,compute=_compute_total_koujianamount)

    @api.depends('create_uid_self')
    def _compute_shenqingren(self):
        self.compute_shenqingren=False
        if int(self.create_uid_self) == int(self.env.user.id):
            self.compute_shenqingren=True

    compute_shenqingren = fields.Boolean(string=u"是否为申请人",compute=_compute_shenqingren)


    @api.depends('currentauditperson')
    def _compute_currentaudit(self):
        self.compute_currentaudit = False

        if int(self.currentauditperson) == int(self.env['hr.employee'].search( [('login', '=', self.env.user.login)]).id):
            self.compute_currentaudit = True

    compute_currentaudit = fields.Boolean(string=u"是否为当前处理人",compute=_compute_currentaudit)

    @api.onchange('paycatelog')
    def _clear_bank_info(self):
        if self.paycatelog=='fukuangeigongyingshang':
            self.shoukuanrenxinming=''
            self.kaihuhang=''
            self.yinhangkahao=''
        elif self.paycatelog=='fukuangeiyuangong':
            self.shoukuanrenxinming=self.env['hr.employee'].search( [('login', '=', self.env.user.login)]).full_name
            self.kaihuhang= self.env['hr.employee'].search( [('login', '=', self.env.user.login)]).bankaddr
            self.yinhangkahao= self.env['hr.employee'].search( [('login', '=', self.env.user.login)]).bankcardno

    @api.model
    def create(self,vals):
        #计算单号
        if ('name' not in vals) or (vals.get('name') in ('/', False)):
            vals['name'] = self.env['ir.sequence'].next_by_code('dtdream.expense.report')
        result = super(dtdream_expense_report, self).create(vals)
        return result

    def get_base_url(self, cr, uid):
        base_url = self.pool.get('ir.config_parameter').get_param(cr, uid, 'web.base.url')
        return base_url
    def get_mail_server_name(self):
        return self.env['ir.mail_server'].search([], limit=1).smtp_user

    def send_mail(self, subject, content, email_to, email_cc="", wait=False):
        base_url = self.get_base_url()
        action = self.env['ir.model.data'].search([('name','=','action_dtdream_expense_pending')]).res_id
        menu_id = self.env['ir.ui.menu'].search([('name','=','费用报销')]).id
        link = '/web#id=%s&view_type=form&model=dtdream.expense.report&action=%s&menu_id=%s' % (self.id,action,menu_id)
        url = base_url + link
        email_to = email_to
        email_cc = "" if email_cc == email_to else email_cc
        subject = subject
        if wait:
            appellation = u'{0},您好：'.format(self.name.user_id.name)
        else:
            #appellation = u'{0},您好：'.format(self.currentauditperson.user_id.name)
            appellation = u'您好：'
        content = content
        self.env['mail.mail'].create({
            'body_html': u'''<p>%s</p>
                                <p>%s</p>
                                <a href="%s">点击链接进入查看</a></p>
                                <p>dodo</p>
                                <p>万千业务，简单有do</p>
                                <p>%s</p>''' % (appellation, content, url, self.write_date[:10]),
            'subject': '%s' % subject,
            'email_from': self.get_mail_server_name(),
            'email_to': '%s' % email_to,
            'auto_delete': False,
        }).send()

    def check_report_params(self, report):
        if report.paycatelog == "fukuangeigongyingshang":
            error_shoukuanren = u'请填写收款人姓名!'
            error_kaihuhang = u'请填写收款人开户行!'
            error_yinhangkahao = u'请填写收款人银行卡号!'
        else:
            error_shoukuanren = u'请联系管理到员工模块-公开信息处填写姓名!'
            error_kaihuhang = u'请到员工模块-自助信息填写开户行!'
            error_yinhangkahao = u'请到员工模块-自助信息填写银行卡号!'

            report.shoukuanrenxinming = self.env['hr.employee'].search( [('login', '=', report.create_uid.login)]).full_name
            report.kaihuhang = self.env['hr.employee'].search([('login', '=', report.create_uid.login)]).bankaddr
            report.yinhangkahao = self.env['hr.employee'].search([('login', '=', report.create_uid.login)]).bankcardno

        if report.shoukuanrenxinming == False:
            raise Warning(error_shoukuanren)
        if report.kaihuhang == False or report.kaihuhang.strip() == "":
            raise Warning(error_kaihuhang)
        if report.yinhangkahao == False or report.yinhangkahao.strip() == "":
            raise Warning(error_yinhangkahao)

        # 主管和总裁不需要填写出差申请
        zongcai_hr_employee_id = self.get_company_president()  # 总裁在hr.employee中的id
        zhuguan_id_hr_employee = self.get_zhuguan(report.create_uid.id)  # 主管hr.employee中id
        if report.create_uid.id != zongcai_hr_employee_id or report.create_uid.id != zhuguan_id_hr_employee:
            if len(report.record_ids) < 1:
                raise Warning(u'请选择消费明细!')

    def send_dingding_msg(self, report, user_id, content=None, model="receipts", action="approval"):
        from openerp.dtdream.dingding.message import send as ding

        if content == None:
            content = u"%s提交的费用报销单,等待您的审批!" % report.create_uid.name

        import redis
        import openerp

        token = ""
        try:
            redis_host = openerp.tools.config['redis_host']
            redis_port = openerp.tools.config['redis_port']
            redis_pass = openerp.tools.config['redis_pass']
            r = redis.Redis(host=redis_host, password=redis_pass, port=redis_port, db=0)
            if r.get("dtdream.dingtalk.token"):
                token = r.get("dtdream.dingtalk.token")
        except Exception, e:
            print "get token from redis failed"
            pass

        agentid = self.env['ir.config_parameter'].get_param('dtdream.expense.agentId', default="")
        url = self.env['ir.config_parameter'].get_param('dtdream.expense.agentUrl', default="")
        url = "%s?model=%s&action=%s&id=%d" % (url, model, action, report.id)

        text = u"数梦报销"
        oa = {
            "message_url": url,
            "head": {
                "bgcolor": "51bcec",
                "text": text
            },
            "body": {
                "form": [
                    {"key": u"具体信息如下:", "value": ""},
                    {"key": u"单据号:", "value": report.name},
                    {"key": u"报销人:", "value": report.create_uid.name},
                    {"key": u"创建时间:", "value": report.create_date[:10]},
                    {"key": u"报销金额:", "value": report.total_shibaoamount}
                ],
                "content": content
            }
        }

        dd_id = self.env['res.users'].search([('id', '=', user_id)]).dd_userid
        try:
            print "Begin to send dingding message to %s" % (dd_id)
            ding(token, dd_id, '', 'oa', oa, agentid)
            print "End to send dingding message to %s" % (dd_id)
        except Exception,e:
            print "Only support operate in ding ding"
            pass

    # -*- coding: utf-8 -*-


    ###################公用函数定义区##################################################

    # 获取公司总裁在hr.employee中的id,模型名称:dtdream.expense.president
    def get_company_president(self):
        re = self.env['dtdream.expense.president'].search([('type', '=', 'zongcai')])
        return re.name.id

    # 根据uid（res.users中的id）获取登录账号
    def get_users_login(self, uuid):
        re = self.env['res.users'].search([('id', '=', uuid)])
        return re.login

    # 根据id(hr.employee)获取登录账号
    def get_employee_login(self, hrid):
        re = self.env['hr.employee'].search([('id', '=', hrid)])
        return re.login

    # 根据登录账号获取员工所在部门id
    def get_employee_departmentid(self, loginid):
        re = self.env['hr.employee'].search([('login', '=', loginid)])
        return re.department_id[0].id

    # 根据登录账号获取员工所在部门的上级部门id
    def get_employee_parentdepartmentid(self, loginid):
        re = self.env['hr.employee'].search([('login', '=', loginid)])
        return re.department_id[0].parent_id.id

    # 根据uid(res.users)获取hr.employee 的id
    def get_employee_id(self, uuid):
        res = self.env['res.users'].search([('id', '=', uuid)])
        re = self.env['hr.employee'].search([('login', '=', res.login)])
        return re.id

    # 根据hr.employee 的id获取uid(res.users)
    def get_user_id(self, hrid):

        re = self.env['hr.employee'].search([('id', '=', hrid)])

        res = self.env['res.users'].search([('login', '=', re.login)])

        return res.id

    # 根据uid（res.users中的id）获取直接主管
    def get_zhuguan(self, uuid):
        hr_employee_login = self.get_users_login(uuid)
        depid = self.get_employee_departmentid(hr_employee_login)
        re = self.env['hr.department'].search([('id', '=', depid)])
        return re.manager_id[0].id

    # 根据departmentid 获取直接主管
    def get_zhuguanfromdepid(self, depid):

        re = self.env['hr.department'].search([('id', '=', depid)])
        return re.manager_id[0].id

    # 根据uid（res.users中的id）获取第一审批人
    def get_no_one_auditor(self, uuid):
        hr_employee_login = self.get_users_login(uuid)
        depid = self.get_employee_departmentid(hr_employee_login)
        re = self.env['hr.department'].search([('id', '=', depid)])
        return re.no_one_auditor[0].id

    # 根据uid（res.users中的id）获取第一审批人上限金额
    def get_no_one_auditor_amount(self, uuid):
        hr_employee_login = self.get_users_login(uuid)
        depid = self.get_employee_departmentid(hr_employee_login)
        re = self.env['hr.department'].search([('id', '=', depid)])
        return re.no_one_auditor_amount

    # 根据uid（res.users中的id）获取第二审批人
    def get_no_two_auditor(self, uuid):
        hr_employee_login = self.get_users_login(uuid)
        depid = self.get_employee_departmentid(hr_employee_login)
        re = self.env['hr.department'].search([('id', '=', depid)])
        return re.no_two_auditor[0].id

    # 根据uid（res.users中的id）获取接口会计
    def get_jiekoukuaiji(self, uuid):
        hr_employee_login = self.get_users_login(uuid)
        depid = self.get_employee_departmentid(hr_employee_login)
        re = self.env['hr.department'].search([('id', '=', depid)])
        return re.jiekoukuaiji[0].id

    # 根据uid（res.users中的id）获取出纳会计
    def get_chuna(self, uuid):
        hr_employee_login = self.get_users_login(uuid)
        depid = self.get_employee_departmentid(hr_employee_login)
        re = self.env['hr.department'].search([('id', '=', depid)])
        return re.chunakuaiji[0].id

    # 根据uid（res.users中的id）获取行政助理
    def get_xingzheng(self, uuid):
        hr_employee_login = self.get_users_login(uuid)
        depid = self.get_employee_departmentid(hr_employee_login)
        re = self.env['hr.department'].search([('id', '=', depid)])
        return re.assitant_id[0].id

    # 根据uid（res.users中的id）获取第二审批人上限金额
    def get_no_two_auditor_amount(self, uuid):
        hr_employee_login = self.get_users_login(uuid)
        depid = self.get_employee_departmentid(hr_employee_login)
        re = self.env['hr.department'].search([('id', '=', depid)])
        return re.no_two_auditor_amount

    ##################################################################################
    @api.multi
    def action_draft(self):
        for report in self:
            if report.currentauditperson:
                report.write({"hasauditor": [(4, report.currentauditperson.id)]})
            if report.state != 'draft':
                report.send_dingding_msg(report, report.create_uid.id, content=u"您提交的报销单被驳回到草稿了。")
            report.write({'state': 'draft', 'currentauditperson': False})

        # 同步更新消费记录状态
            for rc in report.record_ids:
                rc.write({'state': 'draft'})

    @api.multi
    def action_xingzheng(self):
    #提交单据
        for report in self:
            try:
                zongcai_hr_employee_id = self.get_company_president()  # 总裁在hr.employee中的id
                xingzheng_id_hr_employee=report.xingzhengzhuli.id
                no_one_auditor_hr_employee = self.get_no_one_auditor(report.create_uid.id)  # 第一审批人在hr.employee中id
                no_one_auditor_amount = self.get_no_one_auditor_amount(report.create_uid.id)  # 第一审批人上限金额
                no_two_auditor_hr_employee = self.get_no_two_auditor(report.create_uid.id)  # 第二审批人在hr.employee中id
                no_two_auditor_amount = self.get_no_two_auditor_amount(report.create_uid.id)  # 第二审批人上限金额
                jiekoukuaiji = self.get_jiekoukuaiji(report.create_uid.id)  # 接口会计
                zhuguan_id_hr_employee = self.get_zhuguan(report.create_uid.id)  # 主管hr.employee中id
            except:
                raise Warning(u'参数配置不全,请联系管理员!')

            if report.state == 'draft':
                if report.xingzhengzhuli.id == False:
                    raise Warning(u'请选择行政助理!')
                if not report.budget_id and self.env['dtdream.expense.operation.management'].search([('name', '=', 'budget')]):
                    if report.department_id in self.env['dtdream.expense.operation.management'].search([('name', '=', 'budget')])[0].dep_name \
                            and not report.create_uid_self.has_group('dtdream_expense.group_dtdream_expense_no_budget') \
                            and report.paycatelog == 'fukuangeiyuangong':
                        raise Warning(u'请选择预算月份!')
                if report.if_display_zhuanxiang == 1 and not report.project_ids \
                        and self.env['dtdream.expense.operation.management'].search([('name', '=', 'project')]) \
                        and report.department_id in self.env['dtdream.expense.operation.management'].search([('name', '=', 'project')])[0].dep_name \
                        and not report.create_uid_self.has_group('dtdream_expense.group_dtdream_expense_no_project'):
                        raise Warning(u'请填写项目分摊比例!')
                if not report.zhuanxiang_id and report.if_display_zhuanxiang == 1 \
                        and not report.create_uid_self.has_group('dtdream_expense.group_dtdream_expense_no_zhuanx'):
                    raise Warning(u'请选择专项编号!')
                if not report.expensereason:
                    raise ValidationError("请填写报销事由！")
                self.check_report_params(report)

                a=[]#存储费用类别，一张报销单只能有一个费用类别
                b=[]#存储受益部门名称
                for dep in report.benefitdep_ids:
                    b.append(dep.name)

                for rs in report.record_ids:
                    if rs.invoicevalue == False:
                        raise exceptions.ValidationError(u'消费明细不能有空记录，请选择或删除！')
                    a.append(rs.expensecatelog.id)  #将类别ID存入list进行循环检查是否相等。

                s_len = len(set(a))
                if s_len != 1:
                    raise exceptions.ValidationError(u"请检查费用类别，一张单据费用类别必须相同！")

                if len(report.benefitdep_ids)<1:
                    raise exceptions.ValidationError(u"请选择受益部门！")

                if len(report.benefitdep_ids) != len(set(b)):
                    raise exceptions.ValidationError(u"部门重复,请重新选择！")

                total_sharepercent = 0
                for rec in report.benefitdep_ids:
                    if rec.name.id==False:
                        raise exceptions.ValidationError(u'受益部门不能有空记录，请选择或删除！')
                    total_sharepercent = total_sharepercent + float(rec.sharepercent)
                    if float(rec.sharepercent) <= 0 or float(rec.sharepercent) > 100:
                        raise exceptions.ValidationError(u'受益部门分摊比例不能大于100或小于0！')

                if total_sharepercent != 100:
                    raise exceptions.ValidationError(u'受益部门分摊比例总和为100%！')

                import sys
                reload(sys)
                sys.setdefaultencoding('utf-8')

                for rs in report.record_ids:
                    if rs.expensecatelog.name == u"差旅费" and len(report.chuchaishijian_ids) < 1:
                        if not self.create_uid.has_group("dtdream_expense.group_dtdream_expense_ali"):
                            if rs.expensedetail.name !=u"市内交通费" and rs.expensedetail.name !=u"手机话费" and rs.expensedetail.name !=u"过路费":
                                raise exceptions.ValidationError(u'请选择出差申请单！')

                message = u"申请人提交报销单，状态：草稿---->行政助理审批。"
                report.message_post(body=message)
            elif report.state != "draft":
                report.write({"hasauditor": [(4, report.currentauditperson.id)]})

            report.write({'state':'xingzheng','currentauditperson':report.xingzhengzhuli.id})

            report.send_mail(u"【提醒】{0}于{1}提交的费用报销单,请您审批!".format(report.create_uid.name, report.create_date[:10]),
                           u"%s提交的费用报销单,等待您的审批!" % report.create_uid.name,
                           email_to=report.currentauditperson.work_email)

            report.send_dingding_msg(report, report.currentauditperson.user_id.id)
            report.send_dingding_msg(report, report.create_uid.id, content=u"您提交的报销单到了行政助理审批阶段")
            #同步更新消费记录状态
            for rc in report.record_ids:
                rc.write({'state': 'xingzheng'})

    @api.multi
    def action_zhuguan(self):

        for report in self:
            try:
                zongcai_hr_employee_id = self.get_company_president()  # 总裁在hr.employee中的id
                zhuguan_id_hr_employee = self.get_zhuguan(report.create_uid.id)  # 主管hr.employee中id
                create_hr_id = self.get_employee_id(report.create_uid.id)  # 本单创建人hr.employee中id
            except:
                raise Warning(u'参数配置不全,请联系管理员!')

            if create_hr_id==zhuguan_id_hr_employee:
                #一级主管提交到总裁,二级主管不走主管审批
                re_currentauditperson = zongcai_hr_employee_id

            else:#员工提交到部门主管
                re_currentauditperson = zhuguan_id_hr_employee

            # 更新报销单
            report.write({"hasauditor": [(4, report.currentauditperson.id)]})
            report.write({'state': 'zhuguan', 'currentauditperson': re_currentauditperson})
            report.send_mail(u"【提醒】{0}于{1}提交的费用报销单,请您审批!".format(report.create_uid.name, report.create_date[:10]),
                           u"%s提交的费用报销单,等待您的审批!" % report.create_uid.name,
                           email_to=report.currentauditperson.work_email)
            self.send_dingding_msg(report, report.currentauditperson.user_id.id)
            self.send_dingding_msg(report, report.create_uid.id, content=u"您提交的报销单到了主管审批阶段")

            # 更新消费记录状态
            for rc in report.record_ids:
                rc.write({'state': 'zhuguan'})

    @api.multi
    def action_quanqianren(self):

        for report in self:
            try:
                zongcai_hr_employee_id = self.get_company_president()  #总裁在hr.employee中的id
                zhuguan_id_hr_employee = self.get_zhuguan(report.create_uid.id)  #主管hr.employee中id
                no_one_auditor_hr_employee =  self.get_no_one_auditor(report.create_uid.id) #第一审批人在hr.employee中id
                no_one_auditor_amount =  self.get_no_one_auditor_amount(report.create_uid.id)    #第一审批人上限金额
                no_two_auditor_hr_employee = self.get_no_two_auditor(report.create_uid.id)  # 第二审批人在hr.employee中id
                no_two_auditor_amount =  self.get_no_two_auditor_amount(report.create_uid.id)  # 第二审批人上限金额
                zhuguan_login = self.get_employee_login(zhuguan_id_hr_employee)
                parentdepartmentid = self.get_employee_parentdepartmentid(zhuguan_login)  # 上级部门是否为空，为空则为一级，否则为二级
                create_hr_id = self.get_employee_id(report.create_uid.id)  # 本单创建人hr.employee中id
            except:
                raise Warning(u'参数配置不全,请联系管理员!')

            if create_hr_id == zhuguan_id_hr_employee:
                if parentdepartmentid != False:
                    # 二级部门主管没有经过主管审批，取自己和权签人比较决定权签阶段的审批人
                    compare_person = create_hr_id
                else:  # 一级主管提交到总裁
                    compare_person = zongcai_hr_employee_id
            else:  # 员工提交到二级主管
                compare_person = zhuguan_id_hr_employee
            # 判断申请人或者是主管审批阶段审批人和权签人的关系
            if compare_person == no_two_auditor_hr_employee and report.total_invoicevalue > no_two_auditor_amount:
                # 和第二审批人重复，且超出第二审批人金额，进入总裁审批
                re_currentauditperson = zongcai_hr_employee_id
                report.which_quanqianren = '3'
            elif compare_person == no_one_auditor_hr_employee and report.total_invoicevalue > no_one_auditor_amount:
                # 第一审批人重复，且超出第一审批人金额，进入第二权签人审批
                re_currentauditperson = no_two_auditor_hr_employee
                report.which_quanqianren = '2'
            else:
                # 未重复的到第一权签人审批
                re_currentauditperson = no_one_auditor_hr_employee
                report.which_quanqianren = '1'

            #更新报销单
            report.write({"hasauditor": [(4, self.currentauditperson.id)]})
            report.write({'state': 'quanqianren', 'currentauditperson': re_currentauditperson})
            report.send_mail(u"【提醒】{0}于{1}提交的费用报销单,请您审批!".format(report.create_uid.name, report.create_date[:10]),
                           u"%s提交的费用报销单,等待您的审批!" % report.create_uid.name,
                           email_to=report.currentauditperson.work_email)
            self.send_dingding_msg(report, report.currentauditperson.user_id.id)
            self.send_dingding_msg(report, report.create_uid.id, content=u"您提交的报销单到了权签人审批阶段")

            for rc in report.record_ids:
                rc.write({'state': 'quanqianren'})


    @api.multi
    def action_jiekoukuaiji(self):

        for report in self:
            if report.xingzhengzhuli.id == False:
                raise Warning(u'请选择行政助理!')
            self.check_report_params(report)
            try:
                jiekoukuaiji  = self.get_jiekoukuaiji(report.create_uid.id) # 接口会计
            except:
                raise Warning(u'接口会计没有配置,请联系管理员!')
            if report.state != "draft":
                report.write({"hasauditor": [(4, report.currentauditperson.id)]})
            else:
                message = u"申请人提交报销单，状态：草稿---->接口会计审批。"
                report.message_post(body=message)
            report.write({'state': 'jiekoukuaiji', 'currentauditperson': jiekoukuaiji})
            report.send_mail(u"【提醒】{0}于{1}提交的费用报销单,请您审批!".format(report.create_uid.name, report.create_date[:10]),
                           u"%s提交的费用报销单,等待您的审批!" % report.create_uid.name,
                           email_to=report.currentauditperson.work_email)
            report.send_dingding_msg(report, report.currentauditperson.user_id.id)
            self.send_dingding_msg(report, report.create_uid.id, content=u"您提交的报销单到了接口会计审批阶段")
            # 更新消费记录状态
            for rc in report.record_ids:
                rc.write({'state': 'jiekoukuaiji'})


    @api.multi
    def action_daifukuan(self):

        for report in self:
            # 根据提交人的部门查找当前处理人
            try:
                hr_employee_login = self.env['res.users'].search([('id', '=', report.create_uid.id)]).login
                depid = self.env['hr.employee'].search([('login', '=', hr_employee_login)]).department_id[0].id
                assistant_ids = self.env['hr.department'].search([('id', '=', depid)]).chunakuaiji[0].id
            except:
                raise Warning(u'参数配置不全,请联系管理员!')
            report.write({"hasauditor": [(4, report.currentauditperson.id)],'jiekou_approve_time':datetime.now()})
            report.write({'state': 'daifukuan', 'currentauditperson': assistant_ids})
            report.send_mail(u"【提醒】{0}于{1}提交的费用报销单,发生扣款!".format(report.create_uid.name, report.create_date[:10]),
                           u"您提交的费用报销单%s,发生了%s元扣款!" % (report.name,report.total_koujianamount),
                           email_to=self.env['hr.employee'].search([('user_id','=',report.create_uid.id)]).work_email)
            self.send_dingding_msg(report, report.currentauditperson.user_id.id)
            content = u"您提交的报销单到了待付款阶段"
            if report.total_koujianamount > 0:
                content = u"您提交的报销单到了待付款阶段,发生%s元扣款！" % report.total_koujianamount
                report.send_mail(u"【提醒】{0}于{1}提交的费用报销单,请您审批!".format(report.create_uid.name, report.create_date[:10]),
                           u"%s提交的费用报销单,等待您的审批!" % report.create_uid.name,
                           email_to=report.currentauditperson.work_email)
            self.send_dingding_msg(report, report.create_uid.id, content=content)
            for rc in report.record_ids:
                rc.write({'state': 'daifukuan'})


    @api.multi
    def action_yifukuan(self):

        for report in self:
            report.write({"hasauditor": [(4, self.currentauditperson.id)]})
            report.write({'state': 'yifukuan', 'currentauditperson': ''})
            content = u"您于{0}提交的费用报销单已完成审批!".format(report.create_date[:10])
            self.send_dingding_msg(report, report.create_uid.id, content=content, action="view")
            for rc in report.record_ids:
                rc.write({'state': 'yifukuan'})

    @api.multi
    def btn_checkpaper(self):
        for report in self:
            if report.state=="xingzheng":
                message = u"行政助理已签收纸件。"
                self.message_post(body=message)
                report.showcuiqian="1"
                # send dingding msg
                content = message
                self.send_dingding_msg(report, report.create_uid.id, content=content, action="view")
            elif report.state=="jiekoukuaiji":
                message = u"接口会计已签收纸件。"
                self.message_post(body=message)
                report.showcuiqian = "2"
                # send dingding msg
                content = message
                self.send_dingding_msg(report, report.create_uid.id, content=content, action="view")

    @api.multi
    def btn_cuiqian(self):
        for report in self:
            self.send_mail(u"【邮催】{0}于{1}提交的费用报销单,请您尽快审批!".format(report.create_uid.name, report.create_date[:10]),u"%s提交的费用报销单,等待您的审批" % self.create_uid.name, email_to=self.currentauditperson.work_email)
            message = u"申请人发送了邮催。"
            self.message_post(body=message)
            # send dingding msg
            content = u"{0}于{1}提交的费用报销单,请您尽快审批!".format(report.create_uid.name, report.create_date[:10])
            self.send_dingding_msg(report, self.currentauditperson.user_id.id, content=content)

    @api.multi
    def unlink(self):
        for report in self:
            if report.state != "draft":
                raise Warning("只能删除草稿状态的报销单!")
            if report.create_uid.id != self.env.user.id:
                raise Warning(u'只能删除自己的报销单!')
            res = super(dtdream_expense_report, self).unlink()
            return res
    is_outtime=fields.Boolean(u'已超期',compute="_cal_outtime",store=True)
    outtime_amount=fields.Float(u'超期金额',compute="_cal_outtime",store=True)

    @api.multi
    @api.depends('record_ids')
    def _cal_outtime(self):
        for report in self:
            outtime_amount=0;
            if report.record_ids:
                for record in report.record_ids:
                    if record.outtimenumber>0:
                        report.is_outtime=True
                        outtime_amount+=record.invoicevalue

            report.outtime_amount=outtime_amount

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):

        params = self._context.get('params', None)
        action = params.get("action", 0) if params else 0
        my_action = self.env["ir.actions.act_window"].search([('id', '=', action)])
        res = super(dtdream_expense_report, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=False)
        doc = etree.XML(res['arch'])
        if my_action.name != u"我的申请":
            if res['type'] == "form":
                doc.xpath("//form")[0].set("create", "false")
            if res['type'] == "tree":
                doc.xpath("//tree")[0].set("create", "false")
            if res['type'] == "kanban":
                doc.xpath("//kanban")[0].set("create", "false")
        res['arch'] = etree.tostring(doc)
        return res

    @api.model
    def if_in_jiekoukuaiji(self):
        return self.env.user.has_group("dtdream_expense.group_dtdream_expense_jiekoukuaiji")

