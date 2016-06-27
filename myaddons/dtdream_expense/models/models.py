# -*- coding: utf-8 -*-

from openerp import models, fields, api
from datetime import datetime
from openerp .exceptions import ValidationError


#消费记录模型，created by lucongjin 20160612
class dtdream_expense_record(models.Model):

    _name = "dtdream.expense.record"

    name = fields.Char()  #没用，仅为了链接不显示模型名称

    state = fields.Selection([('draft','草稿'),('xingzheng','待行政助理审批')],string="状态",default="draft")

    expensecatelog = fields.Many2one("dtdream.expense.catelog",string="费用类别",required=True)
    expensedetail = fields.Many2one("dtdream.expense.detail",string="费用明细",required=True)

    invoicevalue = fields.Float(digits=(11,2),required=True,string='票据金额')
    outtimenumber = fields.Integer(string="超期时长")
    koujianamount = fields.Float(digits=(11,2),string="扣减金额")
    shibaoamount = fields.Float(digits=(11,2),string="实报金额")
    expensestartdate = fields.Date(string="费用发生开始日期",default=lambda self:datetime.now())
    expenseenddate = fields.Date(string="费用发生结束日期" ,default=lambda self:datetime.now())
    city = fields.Char(string="费用发生城市")
    attachment = fields.Binary(store=True,string="附件")


    #费用类别与费用明细联动
    @api.onchange("expensecatelog")
    def onchange_expensecatelog(self):
        if self.expensecatelog:
            if self.expensedetail.parentid != self.expensecatelog:
                self.expensedetail = ""
            return {
                'domain': {
                    "expensedetail":[('parentid','=',self.expensecatelog.id)]
                }
            }

    @api.onchange("expensedetail")
    def onchange_expensedetail(self):
        if self.expensedetail:
            self.expensecatelog = self.expensedetail.parentid



            # if self.expensecatelog != self.expensedetail.parentid:
            #     self.expensecatelog = ""
            # return {
            #     'domain': {
            #         "expensecatelog": [('id', '=', self.expensedetail.parentid)]
            #     }
            # }


#费用类别模型
class dtdream_expense_catelog(models.Model):
    _name = "dtdream.expense.catelog"

    name = fields.Char(string="名称",required=True)

    _sql_constraints = [

        ('name_unique',
         'UNIQUE(name)',
         "名称不能重复，请重新输入！"),
    ]


#费用明细模型
class dtdream_expense_detail(models.Model):
    _name = "dtdream.expense.detail"

    name = fields.Char(string="名称",required=True)
    parentid = fields.Many2one("dtdream.expense.catelog",string="费用类别",required=True)

    _sql_constraints = [

        ('name_unique',
         'UNIQUE(name)',
         "名称不能重复，请重新输入！"),
    ]
    #授权权签人模型，在hr.department上扩展

#权签授权模型
class dtdream_expense_quanqian(models.Model):
    _inherit = 'hr.department'

    quanqianren = fields.Many2one("hr.employee",string="权签人")
    shouquanren1 = fields.Many2one("hr.employee",string="第一授权人")
    amountmin1 = fields.Integer(string="第一授权人最小金额")
    amountmax1 = fields.Integer(string="第一授权人最大金额")

    shouquanren2 = fields.Many2one("hr.employee",string="第二授权人")
    amountmin2 = fields.Integer(string="第二授权人最小金额")
    amountmax2 = fields.Integer(string="第二授权人最大金额")

    jiekoukuaiji = fields.Many2one("hr.employee",string="接口会计")
    chunakuaiji = fields.Many2one("hr.employee", string="出纳会计")

#报销单模型
class dtdream_expense_report(models.Model):
    _name = "dtdream.expense.report"


    job_number = fields.Char(string="员工工号",default=lambda self:self.env['hr.employee'].search([('login','=',self.env.user.login)]).job_number)
    full_name = fields.Char(string="姓名", default=lambda self: self.env['hr.employee'].search( [('login', '=', self.env.user.login)]).full_name)
    work_place = fields.Char(string="工作常驻地", default=lambda self: self.env['hr.employee'].search( [('login', '=', self.env.user.login)]).work_place)

    department_id = fields.Many2one('hr.department', string='所属部门',default=lambda self: self.env['hr.employee'].search( [('login', '=', self.env.user.login)]).department_id)
    department_number = fields.Char(string="部门编码",default=lambda self: self.env['hr.employee'].search( [('login', '=', self.env.user.login)]).department_id.code)

    paytype = fields.Selection([('yinhangzhuanzhang','银行转账'),('hexiaobeiyongjin','核销备用金')],string="支付方式",default = 'yinhangzhuanzhang')
    paycatelog = fields.Selection([('fukuangeiyuangong','付款给员工'),('fukuangeigongyingshang','付款给供应商')],string="支付类别",required=True,default='fukuangeiyuangong')

    shoukuanrenxinming = fields.Char(string='收款人姓名')
    kaihuhang = fields.Char(string="开户行")
    yinhangkahao = fields.Char(string='银行卡号')
    expensereason = fields.Text(string='报销事由')

    expensecode = fields.Char(string='单据号')
    name = fields.Char(string="标题", default=lambda self: self.env['hr.employee'].search(
        [('login', '=', self.env.user.login)]).name + u"的报销单")



