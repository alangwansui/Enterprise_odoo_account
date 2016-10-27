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

    #budgetmonth = fields.Selection([('1','一月份'),('2','二月份')],string ="对应预算月份")
    benefitdep_ids  =fields.One2many("dtdream.expense.benefitdep","report_id",string=u"受益部门分摊比例")

    record_ids=fields.Many2many('dtdream.expense.record','dtdream_exprense_record_report_ref','record_id','report_id',u'费用明细')

    state = fields.Selection([('draft', u'草稿'), ('xingzheng', u'行政助理审批'), ('zhuguan', u'主管审批'), ('quanqianren', u'权签人审批'),('jiekoukuaiji', u'接口会计审批'), ('daifukuan', u'待付款'),
                              ('yifukuan', u'已付款')], string="状态", default="draft")
    #create_uid   申请人
    #create_date  申请时间

    xingzhengzhuli = fields.Many2one("hr.employee",string=u"部门行政助理",default=_get_default_val,
                                     domain=lambda self:[('id','in',[x.id for x in self.env['hr.employee'].search([('user_id', '=',self.env.user.id)]).department_id.assitant_id])])
    currentauditperson = fields.Many2one("hr.employee",string=u"当前处理人")
    currentauditperson_userid = fields.Integer(string=u"当前处理人uid")
    # chuchaishijian_ids = fields.One2many("dtdream.expense.chuchai","report_id",string=u"出差时间")
    chuchaishijian_ids = fields.Many2many('dtdream.travel.journey', 'travel_journey_expense_report_ref','journey_id','report_id', u'出差时间')
    #zhuanxiangshiqianshenpidanhao = fields.Selection([('1','SQ11020101'),('2','SQ11020102')],string="专项事前审批单号")
    create_uid_self = fields.Many2one("res.users",string=u"申请人",default=lambda self: self.env.user.id)
    can_pass_jiekoukuaiji = fields.Char(string=u'权签人审批后是否到接口会计', default="0")
    zhuguan_quanqian_jiekoukuaiji = fields.Char(string=u'主管到权签还是接口会计(1:权签,2:接口会计)', default="0")
    hasauditor = fields.Many2many("hr.employee",string=u"已审批过的人")
    showcuiqian= fields.Char(string=u'是否已签收', default="0")
    followers_user = fields.Many2many("res.users", "dtdream_expense_followers", string="关注者")

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
            # _logger.info("zongcai_id:" + str(zongcai_id))
            # _logger.info("user Id:" + str(self.env.user.id))
            if self.create_uid_self.id == zongcai_id:
                report.is_zongcai = True
            else:
                report.is_zongcai = False

    is_zongcai=fields.Boolean(u'是否总裁',compute='_compute_is_zongcai')
    # @api.constrains('record_ids')
    # def _constrains_record_ids(self):
    #     for report in self:
    #         for record in report.record_ids:
    #             if len(record.report_ids)>1:
    #                 raise ValueError("%s 费用明细已经存在报销单中" %(record.name))



    @api.onchange('create_uid_self')
    def _onchange_create_uid_self(self):

        iszongcai = False

        # if self.create_uid ==self.get_user_id(self.get_company_president):
        #     iszongcai = True

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
        # _logger.info('---->da'+str(da))
        return str(da)[0:4]


    @api.constrains("record_ids")
    def check_length(self):
        if not self.record_ids:
            raise ValidationError("请至少保持一条消费明细。")

    @api.multi
    @api.depends('record_ids')
    def _compute_total_koujianamount(self):
      #  _logger.info("comput........")
        for report in self:
            if report.state == "draft":
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
                        r_shibaoamount = rd.invoicevalue * xishu
                        r_koujianamount = rd.invoicevalue - r_shibaoamount
                        # rd._cr.execute("update dtdream_expense_record set outtimenumber = %s,koujianamount = %s,shibaoamount = %s",(months,r_koujianamount,r_shibaoamount))
                        rd.write({'outtimenumber':months,'koujianamount':r_koujianamount,'shibaoamount':r_shibaoamount})
                        koujian += rd.koujianamount
                        invoice += rd.invoicevalue
                report.total_koujianamount = koujian
                report.total_invoicevalue = invoice
                report.total_shibaoamount = report.total_invoicevalue - report.total_koujianamount
            if report.state == "jiekoukuaiji":
                koujian = 0.0
                invoice = 0.0
                if report.record_ids:
                    for rd in report.record_ids:
                        koujian += rd.koujianamount
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
        # print  self.paycatelog

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
        link = '/web#id=%s&view_type=form&model=dtdream.expense.report' % self.id
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
           #驳回到申请人时，修改状态为草稿，当前处理人为空。
            if report.state !="draft":
                report.write({"hasauditor": [(4, self.currentauditperson.id)]})
                report.write({'state': 'draft', 'currentauditperson': False,'currentauditperson_userid': False})
           # 同步更新消费记录状态

            #record_ids = self.env['dtdream.expense.record'].search([('report_ids', '=', self.id)])
            for rc in report.record_ids:
                rc.write({'state': 'draft'})


    @api.multi
    def action_xingzheng(self):


        re_state = ''
        re_currentauditperson = ''
        re_currentauditperson_userid = ''
        message=''
        emailto=''


    #提交单据

        for report in self:
            # self.
            # report.kaihuhang = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)]).bankaddr
            # report.yinhangkahao = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)]).bankcardno
            try:
                zongcai_hr_employee_id = self.get_company_president()  # 总裁在hr.employee中的id
                # xingzheng_id_hr_employee = self.get_xingzheng(report.create_uid.id)  # 行政助理hr.employee中id
                xingzheng_id_hr_employee=report.xingzhengzhuli.id
                jiekoukuaiji = self.get_jiekoukuaiji(report.create_uid.id)  # 接口会计
                zhuguan_id_hr_employee = self.get_zhuguan(report.create_uid.id)  # 主管hr.employee中id
            except :
                raise Warning(u'参数配置不全,请联系管理员!')



            if report.state == 'draft':

                # _logger.info("report.xingzhengzhuli---------"+str(report.xingzhengzhuli.id))

                if report.xingzhengzhuli.id == False:
                    raise Warning(u'请选择行政助理!')

                self.check_report_params(report)


                a=[]#存储费用类别，一张报销单只能有一个费用类别
                b=[]#存储受益部门名称
                for dep in report.benefitdep_ids:
                    b.append(dep.name)

                for rs in report.record_ids:
                    if rs.invoicevalue == False:
                        raise exceptions.ValidationError(u'消费明细不能有空记录，请选择或删除！')
                    # if float(rs.invoicevalue) >= 5000:
                    #     raise exceptions.ValidationError(u'消费明细金额大于等于5000的记录需走专项申请，请删除！')
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

                    total_sharepercent = total_sharepercent + int(rec.sharepercent)
                    if int(rec.sharepercent) <= 0 or int(rec.sharepercent) > 100:
                        raise exceptions.ValidationError(u'受益部门分摊比例不能大于100或小于0！')

                if total_sharepercent != 100:
                    raise exceptions.ValidationError(u'受益部门分摊比例总和为100%！')


                # for rc in report.chuchaishijian_ids:
                #     if rc.name.id==False:
                #         raise exceptions.ValidationError(u'出差申请单不能有空记录，请选择或删除！')


                import sys
                reload(sys)
                sys.setdefaultencoding('utf-8')

                for rs in report.record_ids:
                    if rs.expensecatelog.name == u"差旅费" and len(report.chuchaishijian_ids) < 1:
                        if rs.expensedetail.name !=u"市内交通费" and rs.expensedetail.name !=u"手机话费":
                            raise exceptions.ValidationError(u'请选择出差申请单！')




                #如果是总裁提交直接到接口会计，否则到行政助理处审批。
                if zongcai_hr_employee_id ==self.get_employee_id(report.create_uid.id):
                    re_state = 'jiekoukuaiji'
                    re_currentauditperson = jiekoukuaiji
                    re_currentauditperson_userid = self.get_user_id(jiekoukuaiji)
                    message = u"申请人提交报销单，状态：草稿---->接口会计审批。"
                    emailto = self.env['hr.employee'].search([('id', '=', jiekoukuaiji)]).work_email
                else:
                    re_state = 'xingzheng'
                    re_currentauditperson = xingzheng_id_hr_employee
                    re_currentauditperson_userid = self.get_user_id(xingzheng_id_hr_employee)
                    message = u"申请人提交报销单，状态：草稿---->行政助理审批。"
                    emailto=self.env['hr.employee'].search([('id', '=', xingzheng_id_hr_employee)]).work_email

                self.message_post(body=message)

                self.send_mail(u"【提醒】{0}于{1}提交的费用报销单,请您审批!".format(report.create_uid.name, report.create_date[:10]),
                               u"%s提交的费用报销单,等待您的审批!" % report.create_uid.name,
                               email_to=emailto)

                # send dingding msg
                user_id = self.env['hr.employee'].search([('id', '=', xingzheng_id_hr_employee)]).user_id.id
                self.send_dingding_msg(report, user_id)

                #更新报销单状态及处理人，待审批人
                report.write({'state':re_state,'currentauditperson':re_currentauditperson,'currentauditperson_userid':re_currentauditperson_userid})

                #同步更新消费记录状态
                for rc in report.record_ids:
                    rc.write({'state': re_state})


            #主管,权签人，接口会计，驳回到行政助理
            elif report.state == 'zhuguan' or report.state == 'quanqianren' or report.state == 'jiekoukuaiji':

                re_state = 'xingzheng'
                re_currentauditperson = xingzheng_id_hr_employee
                re_currentauditperson_userid = self.get_user_id(xingzheng_id_hr_employee)

                # 更新报销单状态及处理人，待审批人
                report.write({"hasauditor": [(4, report.currentauditperson.id)]})
                report.write({'state': re_state, 'currentauditperson': re_currentauditperson,
                            'currentauditperson_userid': re_currentauditperson_userid})

                # 同步更新消费记录状态
                #record_ids = self.env['dtdream.expense.record'].search([('report_id', '=', self.id)])
                for rc in report.record_ids:
                    rc.write({'state': re_state})

    def check_report_params(self, report):
        if report.paycatelog == "fukuangeigongyingshang":
            error_shoukuanren = u'请填写收款人姓名!'
            error_kaihuhang = u'请填写收款人开户行!'
            error_yinhangkahao = u'请填写收款人银行卡号!'
        else:
            error_shoukuanren = u'请联系管理到员工模块-公开信息处填写姓名!'
            error_kaihuhang = u'请到员工模块-自动信息填写开户行!'
            error_yinhangkahao = u'请到员工模块-自动信息填写银行卡号!'

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
        from openerp.dingding.message import send as ding

        if content == None:
            content = u"%s提交了费用报销单,等待您的审批!" % report.create_uid.name

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

    @api.multi
    def action_zhuguan(self):

        for report in self:
            try:
                zongcai_hr_employee_id = self.get_company_president()  # 总裁在hr.employee中的id
                zhuguan_id_hr_employee = self.get_zhuguan(report.create_uid.id)  # 主管hr.employee中id
                no_one_auditor_hr_employee = self.get_no_one_auditor(report.create_uid.id)  # 第一审批人在hr.employee中id
                no_one_auditor_amount = self.get_no_one_auditor_amount(report.create_uid.id)  # 第一审批人上限金额
                no_two_auditor_hr_employee = self.get_no_two_auditor(report.create_uid.id)  # 第二审批人在hr.employee中id
                no_two_auditor_amount = self.get_no_two_auditor_amount(report.create_uid.id)  # 第二审批人上限金额
                jiekoukuaiji = self.get_jiekoukuaiji(report.create_uid.id)  # 接口会计
                # currentauditperson = self.currentauditperson.id  # 本单当前处理人
                zhuguan_login = self.get_employee_login(zhuguan_id_hr_employee)
                parentdepartmentid = self.get_employee_parentdepartmentid(zhuguan_login)  # 上级部门是否为空，为空则为一级，否则为二级
                create_hr_id = self.get_employee_id(report.create_uid.id)  # 本单创建人hr.employee中id
                xingzheng_id_hr_employee = self.get_xingzheng(report.create_uid.id)  # 行政助理hr.employee中id
            except:
                raise Warning(u'参数配置不全,请联系管理员!')

            re_state = ''
            re_currentauditperson = ''
            re_currentauditperson_userid = ''
            if create_hr_id==zhuguan_id_hr_employee:
                if parentdepartmentid !=False:#二级主管提交到一级主管

                    re_state = 'zhuguan'
                    re_currentauditperson = self.get_zhuguanfromdepid(parentdepartmentid)
                    re_currentauditperson_userid = self.get_user_id(re_currentauditperson)


                else:#一级主管提交到总裁
                    re_state = 'zhuguan'
                    re_currentauditperson = self.env['dtdream.expense.president'].search([('type','=','zongcai')]).name.id
                    re_currentauditperson_userid = self.get_user_id(re_currentauditperson)


            else:#员工提交到二级主管
                re_state = 'zhuguan'
                re_currentauditperson = zhuguan_id_hr_employee
                re_currentauditperson_userid = self.get_user_id(re_currentauditperson)

            # send dingding msg
            self.send_dingding_msg(report, re_currentauditperson_userid)

            # 更新报销单
            report.write({"hasauditor": [(4, report.currentauditperson.id)]})
            report.write({'state': re_state, 'currentauditperson': re_currentauditperson,
                    'currentauditperson_userid': re_currentauditperson_userid})

            # 更新消费记录状态
            for rc in report.record_ids:
                rc.write({'state': re_state})


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
                jiekoukuaiji  = self.get_jiekoukuaiji(report.create_uid.id) # 接口会计
                zhuguan_login = self.get_employee_login(zhuguan_id_hr_employee)
                parentdepartmentid = self.get_employee_parentdepartmentid(zhuguan_login)  # 上级部门是否为空，为空则为一级，否则为二级
                create_hr_id = self.get_employee_id(report.create_uid.id)  # 本单创建人hr.employee中id
            except:
                raise Warning(u'参数配置不全,请联系管理员!')

            re_state = ''
            re_currentauditperson=''
            re_currentauditperson_userid=''

            #判断该单审批主管
            try:
                if create_hr_id == zhuguan_id_hr_employee:
                    if parentdepartmentid != False:  # 二级主管提交到一级主管
                        zhuguanauditperson = self.get_zhuguanfromdepid(parentdepartmentid)
                    else:  # 一级主管提交到总裁
                        zhuguanauditperson = self.env['dtdream.expense.president'].search([('type', '=', 'zongcai')]).name.id
                else:  # 员工提交到二级主管
                    zhuguanauditperson = zhuguan_id_hr_employee

                if zhuguanauditperson == zongcai_hr_employee_id:   #主管审批环节，如果处理人是总裁的话则直接到接口会计
                    re_state = 'jiekoukuaiji'
                    re_currentauditperson = jiekoukuaiji
                    re_currentauditperson_userid = self.get_user_id(jiekoukuaiji)
                elif zhuguanauditperson == no_two_auditor_hr_employee and report.total_invoicevalue<=no_two_auditor_amount:  # 如果是一级主管到接口会计
                    re_state = 'jiekoukuaiji'
                    re_currentauditperson = jiekoukuaiji
                    re_currentauditperson_userid = self.get_user_id(jiekoukuaiji)
                elif zhuguanauditperson == no_two_auditor_hr_employee and report.total_invoicevalue > no_two_auditor_amount:  # 如果是一级主管到接口会计
                    re_state = 'quanqianren'
                    re_currentauditperson = zongcai_hr_employee_id
                    re_currentauditperson_userid = self.get_user_id(zongcai_hr_employee_id)
                elif zhuguanauditperson == no_one_auditor_hr_employee and report.total_invoicevalue<=no_one_auditor_amount:
                    re_state = 'jiekoukuaiji'
                    re_currentauditperson = jiekoukuaiji
                    re_currentauditperson_userid = self.get_user_id(jiekoukuaiji)
                elif zhuguanauditperson == no_one_auditor_hr_employee and report.total_invoicevalue > no_one_auditor_amount:
                    re_state = 'quanqianren'
                    re_currentauditperson = no_two_auditor_hr_employee
                    re_currentauditperson_userid = self.get_user_id(no_two_auditor_hr_employee)
                else:
                    re_state = 'quanqianren'
                    re_currentauditperson = no_one_auditor_hr_employee
                    re_currentauditperson_userid = self.get_user_id(no_one_auditor_hr_employee)

            except:
                raise Warning(u'参数配置不全,请联系管理员!')

            # send dingding msg
            self.send_dingding_msg(report, re_currentauditperson_userid)

            #更新报销单
            report.write({"hasauditor": [(4, self.currentauditperson.id)]})
            report.write({'state': re_state, 'currentauditperson': re_currentauditperson,'currentauditperson_userid': re_currentauditperson_userid})

            # 更新消费记录状态
            #record_ids = self.env['dtdream.expense.record'].search([('report_id', '=', self.id)])
            for rc in report.record_ids:
                rc.write({'state': re_state})


    @api.multi
    def action_jiekoukuaiji(self):

        for report in self:

            if report.xingzhengzhuli.id == False:
                raise Warning(u'请选择行政助理!')

            self.check_report_params(report)

            try:
                jiekoukuaiji  = self.get_jiekoukuaiji(report.create_uid.id) # 接口会计
                re_state = 'jiekoukuaiji'
                re_currentauditperson = jiekoukuaiji
                re_currentauditperson_userid = self.get_user_id(jiekoukuaiji)
            except:
                raise Warning(u'参数配置不全,请联系管理员!')

            # send dingding msg
            self.send_dingding_msg(report, re_currentauditperson_userid)

            if report.state != "draft":
                report.write({"hasauditor": [(4, report.currentauditperson.id)]}) # 更新报销单
            report.write({'state': re_state, 'currentauditperson': re_currentauditperson,
                        'currentauditperson_userid': re_currentauditperson_userid})

            # 更新消费记录状态
            for rc in report.record_ids:
                rc.write({'state': re_state})


    @api.multi
    def action_daifukuan(self):

        for report in self:
            # 根据提交人的部门查找当前处理人
            try:
                hr_employee_login = self.env['res.users'].search([('id', '=', report.create_uid.id)]).login

                depid = self.env['hr.employee'].search([('login', '=', hr_employee_login)]).department_id[0].id
                assistant_ids = self.env['hr.department'].search([('id', '=', depid)]).chunakuaiji[0].id  ############

                assistant_login = self.env['hr.department'].search([('id', '=', depid)]).chunakuaiji[0].login  ############
                # print assistant_login

                currentauditpersonuserid = self.env['res.users'].search([('login', '=',
                                                                          assistant_login)]).id  # currentauditperson字段存的是hr.employee的id，视图中的uid是res.users的id，故需转换，方便在视图待我审批菜单使用。
                # print self.env['res.users'].search( [('login', '=', assistant_login)])
            except:
                raise Warning(u'参数配置不全,请联系管理员!')

            # send dingding msg
            self.send_dingding_msg(report, currentauditpersonuserid)

            report.write({"hasauditor": [(4, report.currentauditperson.id)]})
            report.write({'state': 'daifukuan', 'currentauditperson': assistant_ids,
                        'currentauditperson_userid': currentauditpersonuserid})

            # 同步更新消费记录状态

            for rc in report.record_ids:
                rc.write({'state': 'daifukuan'})


    @api.multi
    def action_yifukuan(self):

        for report in self:
            # 同步更新消费记录状态

            for rc in report.record_ids:
                rc.write({'state': 'yifukuan'})

            if report.state =="daifukuan":
                message = u"出纳确认付款，状态：待付款---->已付款。"
                self.message_post(body=message)

            report.write({"hasauditor": [(4, self.currentauditperson.id)]})
            report.write({'state': 'yifukuan', 'currentauditperson': '', 'currentauditperson_userid': ''})

            #发送邮件
            hr_employee_login = self.env['res.users'].search([('id', '=', report.create_uid.id)]).login

            shenqinren = self.env['hr.employee'].search([('login', '=', hr_employee_login)])

            self.send_mail(u"【提醒】您于{0}提交的费用报销单已完成审批!".format(report.create_date[:10]),u"您提交的费用报销单已完成审批，请等待付款。" , email_to=shenqinren.work_email)

            # send dingding msg
            content = u"您于{0}提交的费用报销单已完成审批!".format(report.create_date[:10])
            self.send_dingding_msg(report, report.create_uid.id, content=content, action="view")

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
        if my_action.name != u"我的消费明细":
            if res['type'] == "form":
                doc.xpath("//form")[0].set("create", "false")
            if res['type'] == "tree":
                doc.xpath("//tree")[0].set("create", "false")
            if res['type'] == "kanban":
                doc.xpath("//kanban")[0].set("create", "false")
        res['arch'] = etree.tostring(doc)
        return res
