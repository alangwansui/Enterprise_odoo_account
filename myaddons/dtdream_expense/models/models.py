# -*- coding: utf-8 -*-

from openerp import models, fields, api,exceptions
from datetime import datetime,time
from openerp .exceptions import ValidationError
import time

class dtdream_expense_record_baoxiao(models.Model):
    _name = "dtdream.expense.record.baoxiao"

    @api.depends('record_id')
    def _compute_record_fields(self):
        for rec in self:
            rec.state=rec.record_id.state
            rec.expensecatelog= self.env['dtdream.expense.catelog'].search( [('id', '=', rec.record_id.expensecatelog.id)]).name
            rec.expensedetail= self.env['dtdream.expense.detail'].search( [('id', '=', rec.record_id.expensedetail.id)]).name
            rec.invoicevalue = rec.record_id.invoicevalue
            rec.currentdate = rec.record_id.currentdate
            rec.create_uid=self.env['hr.employee'].search( [('user_id', '=', rec.record_id.create_uid.id)]).full_name
            rec.create_date = rec.record_id.create_date


    @api.onchange('record_id')
    def _filter_expense_record(self):

        domain = [('id', 'not in', [cr.record_id.id for cr in self.search([])]),('create_uid','=',self.env.user.id),('id','not in',[cr.id for cr in self.record_id])]
        return {
            'domain': {
                "record_id": domain
            }
        }


    _sql_constraints = [
        ('record_id_unique','UNIQUE(record_id)',"消费明细重复，请重新选择！"),
    ]


    # create_uid   创建人
    # create_date  创建时间
    report_id = fields.Many2one("dtdream.expense.report", string="报销单ID")

    record_id = fields.Many2one("dtdream.expense.record",string="记录名称")



    #state = fields.Char(string="状态",compute=_compute_record_fields)
    state = fields.Selection(
        [('draft', '草稿'), ('xingzheng', '待行政助理审批'), ('zhuguan', '待主管审批'), ('quanqianren', '待权签人审批'),
         ('jiekoukuaiji', '待接口会计审批'), ('daifukuan', '待付款'), ('yifukuan', '已付款')], string="状态", compute=_compute_record_fields)
    expensecatelog = fields.Char(string="费用类别", compute=_compute_record_fields)
    expensedetail = fields.Char(string="费用明细", compute=_compute_record_fields)

    invoicevalue = fields.Float(digits=(11, 2),compute=_compute_record_fields, string='票据金额')

    currentdate = fields.Date(string="费用发生日期", compute=_compute_record_fields)
    create_uid = fields.Char(string="创建人",compute=_compute_record_fields)
    create_date = fields.Date(string="创建时间", compute=_compute_record_fields)




#消费记录模型，created by lucongjin 20160612
class dtdream_expense_record(models.Model):

    _name = "dtdream.expense.record"

    name = fields.Char(string="记录标题")  #没用，仅为了链接不显示模型名称

    #create_uid   创建人
    #create_date  创建时间

    state = fields.Selection([('draft','草稿'),('xingzheng','待行政助理审批'),('zhuguan','待主管审批'),('quanqianren','待权签人审批'),('jiekoukuaiji','待接口会计审批'),('daifukuan','待付款'),('yifukuan','已付款')],string="状态",default="draft")

    expensecatelog = fields.Many2one("dtdream.expense.catelog",string="费用类别",required=True)
    expensedetail = fields.Many2one("dtdream.expense.detail",string="费用明细",required=True)

    invoicevalue = fields.Float(digits=(11,2),required=True,string='票据金额')
    outtimenumber = fields.Integer(string="超期时长")
    koujianamount = fields.Float(digits=(11,2),string="扣减金额")
    shibaoamount = fields.Float(digits=(11,2),string="实报金额")
    currentdate = fields.Date(string="费用发生日期",default=lambda self:datetime.now())
    #expenseenddate = fields.Date(string="费用发生结束日期" ,default=lambda self:datetime.now())
    city = fields.Char(string="费用发生城市")
    attachment = fields.Binary(store=True,string="附件")
    #report_id = fields.Many2one("dtdream.expense.report",string="报销单ID")
    @api.model
    def create(self, vals):
        print type(str(vals['currentdate']))

        if vals.has_key('expensedetail'):
            recordname = self.env['hr.employee'].search( [('login', '=', self.env.user.login)]).full_name+'-'+ self.env['dtdream.expense.detail'].search([('id','=',vals['expensedetail'])])[0].name+'('+time.strftime('%Y%m%d',time.strptime(vals['currentdate'],'%Y-%m-%d')) +')'
        vals['name'] = recordname
        result = super(dtdream_expense_record, self).create(vals)
        return result


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

#审批记录模型
# class dtdream_expense_auditlog(models.Model):
#     _name = "dtdream.expense.auditlog"
#
#     id = fields.Many2one("dtdream_expense_report",string="报销单ID")
#     state = fields.Char(string="状态")
#     auditperson = fields.Char(string="审批人")
#     auditresult  =fields.Char(string="审批结果")
#     auditadvice = fields.Char(string="审批意见")
#     arrivetime = fields.Datetime(string="到达时间")
#     audittime = fields.Datetime(string = "审批时间")
#     elapsedtime = fields.datetime(string = "耗时",store = True ,compute= '_get_elapsedtime')
#
#     @api.depends('arrivetime','audittime')
#     def _get_elapsedtime(self):
#         self.elapsedtime = self.audittime - self.arrivetime
#

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

    shoukuanrenxinming = fields.Char(string='收款人姓名',required=True,default=lambda self: self.env['hr.employee'].search( [('login', '=', self.env.user.login)]).full_name)
    kaihuhang = fields.Char(string="开户行",required=True,default=lambda self: self.env['hr.employee'].search( [('login', '=', self.env.user.login)]).bankaddr)
    yinhangkahao = fields.Char(string='银行卡号',required=True,default=lambda self: self.env['hr.employee'].search( [('login', '=', self.env.user.login)]).bankcardno)
    expensereason = fields.Text(string='报销事由')

    expensecode = fields.Char(string='单据号')

    name = fields.Char(string="标题", default=lambda self: self.env['hr.employee'].search([('login', '=', self.env.user.login)]).name + u"的报销单")
    budgetmonth = fields.Selection([('1','一月份'),('2','二月份')],string ="对应预算月份")
    benefitdep_ids  =fields.One2many("dtdream.expense.benefitdep","report_id",string="受益部门分摊比例")
    record_ids = fields.One2many("dtdream.expense.record.baoxiao","report_id",string="费用明细")

    state = fields.Selection([('draft', '草稿'), ('xingzheng', '待行政助理审批'), ('zhuguan', '待主管审批'), ('quanqianren', '待权签人审批'),('jiekoukuaiji', '待接口会计审批'), ('daifukuan', '待付款'), ('yifukuan', '已付款')], string="状态", default="draft")
    #create_uid   申请人
    #create_date  申请时间
    currentauditperson = fields.Many2one("hr.employee",string="当前处理人")
    chuchaishijian_ids = fields.One2many("dtdream.expense.chuchai","report_id",string="出差时间")
    zhuanxiangshiqianshenpidanhao = fields.Selection([('1','SQ11020101'),('2','SQ11020102')],string="专项事前审批单号")

    @api.constrains('benefitdep_ids')
    def _check_depcount(self):
        if len(self.benefitdep_ids)<1:
            raise exceptions.ValidationError("请选择受益部门！")

    @api.constrains('benefitdep_ids')
    def _onchange_benefitdep_ids(self):
        total_sharepercent = 0
        for rec in self.benefitdep_ids:

            total_sharepercent = total_sharepercent + int(rec.sharepercent)
            if int(rec.sharepercent)<=0 or int(rec.sharepercent)>100:
                raise exceptions.ValidationError('受益部门分摊比例不能大于100或小于0！')

        if total_sharepercent != 100:
            raise exceptions.ValidationError('受益部门分摊比例总和为100%！')

    @api.constrains(record_ids)
    def _check_invoicevalue(self):

        for rec in self.record_ids:
            print self.record_ids

            if int(rec.invoicevalue)<=0:
                raise exceptions.ValidationError('票据金额不能为0！')


    @api.onchange('paycatelog')
    def _clear_bank_info(self):
        # print  self.paycatelog

        if self.paycatelog=='fukuangeigongyingshang':
            self.shoukuanrenxinming=''
            self.kaihuhang=''
            self.yinhangkahao=''
        elif self.paycatelog=='fukuangeiyuangong':
            self.shoukuanrenxinming=self.env['hr.employee'].search( [('login', '=', self.env.user.login)]).full_name
            self.kaihuhang=self.env['hr.employee'].search( [('login', '=', self.env.user.login)]).bankaddr
            self.yinhangkahao=self.env['hr.employee'].search( [('login', '=', self.env.user.login)]).bankcardno


    @api.model
    def create(self,vals):

         baseid = 'BX' + time.strftime("%Y%m%d", time.localtime())

         r = self.env['dtdream.expense.report'].search([('create_date','like',datetime.now().strftime('%Y-%m-%d')+"%")],limit=1,order='id desc').id+1

         # print datetime.now().strftime('%Y-%m-%d')
         # print r
         # print self

         if r < 10:
             baseid += '00' + str(r)
         elif r >= 10 and r < 100:
             baseid += '0' + str(r)
         else:
             baseid +=str(r)

         vals['expensecode']=baseid

         result = super(dtdream_expense_report, self).create(vals)

         return result

class dtdream_expense_benefitdep(models.Model):
    _name = "dtdream.expense.benefitdep"

    @api.depends('name')
    def _compute_department_fields(self):
        for rec in self:
            rec.depcode = rec.name.code

    name = fields.Many2one('hr.department',string="受益部门名称",default=lambda self: self.env['hr.employee'].search( [('login', '=', self.env.user.login)]).department_id)
    depcode= fields.Char(string="受益部门编码",compute=_compute_department_fields)
    sharepercent = fields.Char(string="分摊比例",default=100)
    report_id = fields.Many2one("dtdream.expense.report",string="报销单ID")

class dtdream_expense_chuchai(models.Model):
    _name = "dtdream.expense.chuchai"
    # _rec_name = "travel.journey.starttime"


    name = fields.Many2one('dtdream.travel.journey',string="出差时间",domain=lambda self:[('create_uid','=',self.env.user.id)])

    report_id = fields.Many2one("dtdream.expense.report",string="报销单ID")












