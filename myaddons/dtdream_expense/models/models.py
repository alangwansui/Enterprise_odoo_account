# -*- coding: utf-8 -*-

from openerp import models, fields, api,exceptions
from datetime import datetime,time
from openerp .exceptions import ValidationError,Warning
import time

import logging
_logger = logging.getLogger(__name__)

#
# class dtdream_expense_record_baoxiao(models.Model):
#     _name = "dtdream.expense.record.baoxiao"
#
#     @api.onchange('record_id')
#     def _onchange_record_fields(self):
#         for rec in self:
#             rec.state=rec.record_id.state
#             rec.expensecatelog= self.env['dtdream.expense.catelog'].search( [('id', '=', rec.record_id.expensecatelog.id)]).name
#             rec.expensedetail= self.env['dtdream.expense.detail'].search( [('id', '=', rec.record_id.expensedetail.id)]).name
#             rec.invoicevalue = rec.record_id.invoicevalue
#             rec.currentdate = rec.record_id.currentdate
#             rec.create_uid_self=self.env['hr.employee'].search( [('user_id', '=', rec.record_id.create_uid.id)]).full_name
#             #print  rec.create_uid_self
#             rec.create_date_self= rec.record_id.create_date
#
#             rec.outtimenumber = rec.record_id.outtimenumber
#             rec.koujianamount = rec.record_id.koujianamount
#             rec.shibaoamount = rec.record_id.shibaoamount
#
#
#     def _filter_expense_record(self):
#
#         return [('id', 'not in', [cr.record_id.id for cr in self.search([])]),('create_uid','=',self.env.user.id),('state','=','draft')]
#
#
#     _sql_constraints = [
#         ('record_id_unique','UNIQUE(record_id)',"消费明细重复，请重新选择！"),
#     ]
#
#
#
#
#     # create_uid   创建人
#     # create_date  创建时间
#     report_id = fields.Many2one("dtdream.expense.report", string="报销单ID")
#
#     record_id = fields.Many2one("dtdream.expense.record",string="记录名称",domain=_filter_expense_record)
#
#
#
#     #state = fields.Char(string="状态",compute=_compute_record_fields)
#     state = fields.Selection(
#         [('draft', '草稿'), ('xingzheng', '行政助理审批'), ('zhuguan', '主管审批'), ('quanqianren', '权签人审批'),
#          ('jiekoukuaiji', '接口会计审批'), ('daifukuan', '待付款'), ('yifukuan', '已付款')], string="状态")
#     expensecatelog = fields.Char(string="费用类别")
#     expensedetail = fields.Char(string="费用明细")
#
#     invoicevalue = fields.Float(digits=(11, 2), string='票据金额')
#
#     currentdate = fields.Date(string="费用发生日期")
#     create_uid_self = fields.Char(string="创建人")
#     create_date_self = fields.Date(string="创建时间")
#
#     outtimenumber = fields.Float(digits=(11,2),string="超期时长")
#     koujianamount = fields.Float(digits=(11, 2), string="扣减金额")
#     shibaoamount = fields.Float(digits=(11, 2), string="实报金额")
#
#     @api.multi
#     def write(self, vals):
#         if vals.has_key('record_id'):
#             if vals['record_id']:
#                 rec = self.record_id.search([('id', '=', vals['record_id'])])[0]
#
#                 vals['state'] = rec.state
#                 vals['expensecatelog'] = rec.expensecatelog.name
#                 vals['expensedetail'] = rec.expensedetail.name
#                 vals['invoicevalue'] = rec.invoicevalue
#                 vals['currentdate'] = rec.currentdate
#                 vals['create_uid_self'] = self.env['hr.employee'].search( [('user_id', '=', rec.create_uid.id)]).full_name
#                 vals['create_date_self'] =rec.create_date
#                 vals['outtimenumber'] = rec.outtimenumber
#                 vals['koujianamount'] = rec.koujianamount
#                 vals['shibaoamount'] = rec.shibaoamount
#         result = super(dtdream_expense_record_baoxiao, self).write(vals)
#         return result
#
#     @api.model
#     def create(self, vals):
#         if vals.has_key('record_id'):
#             if vals['record_id']:
#                 rec = self.record_id.search([('id', '=', vals['record_id'])])[0]
#
#                 vals['state'] = rec.state
#                 vals['expensecatelog'] = rec.expensecatelog.name
#                 vals['expensedetail'] = rec.expensedetail.name
#                 vals['invoicevalue'] = rec.invoicevalue
#                 vals['currentdate'] = rec.currentdate
#                 vals['create_uid_self'] = self.env['hr.employee'].search(
#                     [('user_id', '=', rec.create_uid.id)]).full_name
#                 vals['create_date_self'] = rec.create_date
#                 vals['outtimenumber'] = rec.outtimenumber
#                 vals['koujianamount'] = rec.koujianamount
#                 vals['shibaoamount'] = rec.shibaoamount
#         result = super(dtdream_expense_record_baoxiao, self).create(vals)
#         return result


#消费记录模型，created by lucongjin 20160612
class dtdream_expense_record(models.Model):

    _name = "dtdream.expense.record"
    _inherit = ['mail.thread']


#获取创建人上次录入的城市
    def _get_recently_city(self):

        re = self.env['dtdream.expense.record'].search([('create_uid', '=', self.env.user.id)], limit=1,order='id desc')
        return re.city


    @api.onchange('koujianamount')
    def _compute_shibaoamount(self):
        self.shibaoamount=self.invoicevalue - self.koujianamount




    name = fields.Char(string="记录标题")  #没用，仅为了链接不显示模型名称

    #create_uid   创建人
    #create_date  创建时间

    state = fields.Selection([('draft','草稿'),('xingzheng','行政助理审批'),('zhuguan','主管审批'),('quanqianren','权签人审批'),('jiekoukuaiji','接口会计审批'),('daifukuan','待付款'),('yifukuan','已付款')],string="状态",default="draft")

    expensecatelog = fields.Many2one("dtdream.expense.catelog",string="费用类别",required=True,track_visibility='onchange')
    expensedetail = fields.Many2one("dtdream.expense.detail",string="费用明细",required=True,track_visibility='onchange')

    invoicevalue = fields.Float(digits=(11,2),required=True,string='票据金额',track_visibility='onchange')
    outtimenumber = fields.Float(digits=(11,2),string="超期时长")
    koujianamount = fields.Float(digits=(11,2),string="扣减金额",track_visibility='onchange')
    shibaoamount = fields.Float(digits=(11,2),string="实报金额")
    currentdate = fields.Date(string="费用发生日期",default=lambda self:datetime.now(),track_visibility='onchange')
    #expenseenddate = fields.Date(string="费用发生结束日期" ,default=lambda self:datetime.now())
    city = fields.Char(string="费用发生城市",track_visibility='onchange',default=_get_recently_city)
    attachment = fields.Binary(store=True,string="附件",track_visibility='onchange')

    report_id = fields.Many2one("dtdream.expense.report",string="报销单ID")


    @api.model
    def create_expense_record_baoxiao(self):
        context = dict(self._context or {})
        active_model = context.get('active_model')
        active_ids = context.get("active_ids")
        expense_ids=self.browse(active_ids)
        record_ids=[]
        for expense in expense_ids:
            if expense.create_uid.id !=self.env.user.id:
                raise Warning(u'只能对自己的费用明细生成报销单')
            if expense.report_id:
                raise Warning(u'%s 已经生成了报销单' %(expense.name))

        vals={
            'record_ids':[(6,0,active_ids)],
        }

        _logger.info("vals:"+ str(vals))
        report_id=self.env['dtdream.expense.report'].create(vals)

        _logger.info("report_id:"+ str(report_id))

        return {
            'type': 'ir.actions.act_window',
            'name': u'我的报销单',
            'res_model': 'dtdream.expense.report',
            'view_type': 'form',
            'view_mode':'tree,form',
            'view_id':False,
            'domain': [('id', '=', report_id.id)],
            'target': 'current',
        }

    @api.constrains('invoicevalue')
    def _check_invoicevalue_record(self):

        for rec in self:
            if int(rec.invoicevalue) <= 0:
                raise exceptions.ValidationError('票据金额不能小于等于0！')

    @api.model
    def create(self, vals):
        #print type(str(vals['currentdate']))

        if vals.has_key('expensedetail'):
            full_name=self.env['hr.employee'].search( [('login', '=', self.env.user.login)]).full_name
            if not full_name:
                raise Warning(u'请先在员工档案中维护当前用户的员工信息。')
            recordname =full_name+'-'+ self.env['dtdream.expense.detail'].search([('id','=',vals['expensedetail'])])[0].name+'('+time.strftime('%Y%m%d',time.strptime(vals['currentdate'],'%Y-%m-%d')) +')'
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

#权签授权模型
class dtdream_expense_quanqian(models.Model):
    _inherit = 'hr.department'

    no_one_auditor = fields.Many2one("hr.employee", string="第一审批人", help="正常情况下是二级部门主管。",track_visibility='onchange')
    no_one_auditor_amount = fields.Integer(string="第一审批人权签金额",track_visibility='onchange')
    no_two_auditor = fields.Many2one("hr.employee",string="第二审批人",help="正常情况下是一级部门主管。",track_visibility='onchange')
    no_two_auditor_amount = fields.Integer(string="第二审批人权签金额",track_visibility='onchange')
    no_three_auditor = fields.Many2one("hr.employee",string="第三审批人",help="正常情况下是公司级权力最大的总裁，该字段预留，暂时不用，请到配置处获取总裁信息。",track_visibility='onchange')

    jiekoukuaiji = fields.Many2one("hr.employee",string="接口会计",track_visibility='onchange')
    chunakuaiji = fields.Many2one("hr.employee", string="出纳会计",track_visibility='onchange')


#报销单模型
class dtdream_expense_report(models.Model):
    _name = "dtdream.expense.report"
    _inherit = ['mail.thread']


    job_number = fields.Char(string="员工工号",default=lambda self:self.env['hr.employee'].search([('login','=',self.env.user.login)]).job_number)
    full_name = fields.Char(string="姓名", default=lambda self: self.env['hr.employee'].search( [('login', '=', self.env.user.login)]).full_name)
    work_place = fields.Char(string="工作常驻地", default=lambda self:'' and  self.env['hr.employee'].search( [('login', '=', self.env.user.login)]).work_place)

    department_id = fields.Many2one('hr.department', string='所属部门',default=lambda self: self.env['hr.employee'].search( [('login', '=', self.env.user.login)]).department_id)
    department_number = fields.Char(string="部门编码",default=lambda self: self.env['hr.employee'].search( [('login', '=', self.env.user.login)]).department_id.code)

    paytype = fields.Selection([('yinhangzhuanzhang','银行转账'),('hexiaobeiyongjin','核销备用金')],string="支付方式",default = 'yinhangzhuanzhang')
    paycatelog = fields.Selection([('fukuangeiyuangong','付款给员工'),('fukuangeigongyingshang','付款给供应商')],string="支付类别",required=True,default='fukuangeiyuangong')

    shoukuanrenxinming = fields.Char(string='收款人姓名',required=True,default=lambda self: self.env['hr.employee'].search( [('login', '=', self.env.user.login)]).full_name)
    kaihuhang = fields.Char(string="开户行",required=True,default=lambda self:'' and  self.env['hr.employee'].search( [('login', '=', self.env.user.login)]).bankaddr)
    yinhangkahao = fields.Char(string='银行卡号',required=True,default=lambda  self: '' and self.env['hr.employee'].search( [('login', '=', self.env.user.login)]).bankcardno)
    expensereason = fields.Text(string='报销事由')

    expensecode = fields.Char(string='单据号')

    name = fields.Char(string="标题", default=lambda self: self.env['hr.employee'].search([('login', '=', self.env.user.login)]).name + u"的报销单")
    #budgetmonth = fields.Selection([('1','一月份'),('2','二月份')],string ="对应预算月份")
    benefitdep_ids  =fields.One2many("dtdream.expense.benefitdep","report_id",string="受益部门分摊比例")

    record_ids=fields.One2many('dtdream.expense.record','report_id',u'费用明细')

    state = fields.Selection([('draft', '草稿'), ('xingzheng', '行政助理审批'), ('zhuguan', '主管审批'), ('quanqianren', '权签人审批'),('jiekoukuaiji', '接口会计审批'), ('daifukuan', '待付款'), ('yifukuan', '已付款')], string="状态", default="draft")
    #create_uid   申请人
    #create_date  申请时间
    currentauditperson = fields.Many2one("hr.employee",string="当前处理人")
    currentauditperson_userid = fields.Integer(string="当前处理人uid")
    chuchaishijian_ids = fields.One2many("dtdream.expense.chuchai","report_id",string="出差时间")
    #zhuanxiangshiqianshenpidanhao = fields.Selection([('1','SQ11020101'),('2','SQ11020102')],string="专项事前审批单号")
    create_uid_self = fields.Many2one("res.users",string="申请人",default=lambda self: self.env.user.id)
    can_pass_jiekoukuaiji = fields.Char(string='权签人审批后是否到接口会计', default="0")
    hasauditor = fields.Many2many("hr.employee",string="已审批过的人")
    showcuiqian = fields.Char(string='纸件是否已签收', default="0",help='1:行政助理已签收2：接口会计已签收')

    def getMonth(self,da):
        return str(da)[5:7]


    @api.depends('record_ids')
    def _compute_total_koujianamount(self):

        #计算消费明细扣罚金额
        if len(self.record_ids)>0:
            for ra in self:
                # longtime = datetime.strptime('1900-08-15', '%Y-%m-%d')
                a = []
                for rb in ra.record_ids:
                    a.append(datetime.strptime(rb.currentdate, '%Y-%m-%d'))

                # 最大日期
                maxdate = max(a)

                # 建单日期
                if not ra.create_date:
                    createdate = datetime.now().strftime('%Y-%m-%d')
                else:
                    createdate = datetime.strptime(ra.create_date, '%Y-%m-%d %H:%M:%S')
                #createdate=ra.create_date

                print '-------------',type(maxdate)
                print '-------------',type(createdate)

                # 计算保存时间与最大值差。
                months =int(self.getMonth(createdate)) -int(self.getMonth(maxdate))

                print  'months:',months
                # 计算超期罚款系数
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


                    # 循环计算消费记录的超期时长及罚款金额
                total_invoice = 0.0
                total_koujian = 0.0
                total_shibao = 0.0
                for rd in ra.record_ids:
                    print '------------------------1'
                    print 'rd:',rd
                    r_shibaoamount = rd.invoicevalue * xishu
                    r_koujianamount = rd.invoicevalue - r_shibaoamount

                    # rd.outtimenumber = months
                    # rd.koujianamount = r_koujianamount
                    # rd.shibaoamount = r_shibaoamount
                    rd.write({'outtimenumber':months,'koujianamount':r_koujianamount,'shibaoamount':r_shibaoamount})


            #计算整单相关金额
            koujian=0.0
            invoice = 0.0
            for r in self.record_ids:
                koujian +=r.koujianamount
                invoice += r.invoicevalue
            self.total_koujianamount=koujian
            self.total_invoicevalue = invoice
            self.total_shibaoamount = self.total_invoicevalue - self.total_koujianamount
            print '-------------------2'





    total_invoicevalue = fields.Float(digits=(11, 2), string="票据总金额",store=True,compute=_compute_total_koujianamount)
    total_koujianamount = fields.Float(digits=(11, 2), string="扣减总金额",store=True,compute=_compute_total_koujianamount)
    total_shibaoamount = fields.Float(digits=(11, 2), string="实报总金额",store=True,compute=_compute_total_koujianamount)





    @api.depends('create_uid_self')
    def _compute_shenqingren(self):
        self.compute_shenqingren=False

        if int(self.create_uid_self) == int(self.env.user.id):

            self.compute_shenqingren=True

        #print self.compute_shenqingren

    compute_shenqingren = fields.Boolean(string="是否为申请人",compute=_compute_shenqingren)

    @api.depends('currentauditperson')
    def _compute_currentaudit(self):
        self.compute_currentaudit = False

        if int(self.currentauditperson) == int(self.env['hr.employee'].search( [('login', '=', self.env.user.login)]).id):
            self.compute_currentaudit = True

       # print  self.env['hr.employee'].search( [('login', '=', self.env.user.login)]).id
        #print self.currentauditperson

    compute_currentaudit = fields.Boolean(string="是否为当前处理人",compute=_compute_currentaudit)

    @api.constrains('record_ids')
    def _check1_invoicevalue(self):
        # pass
        # _logger.info("val:"+ str(self.record_ids))

        if len(self.record_ids) < 1:
            raise exceptions.ValidationError("请选择消费明细！")

        for rec in self:
            a=[]#存储费用类别，一张报销单只能有一个费用类别
            for rs in rec.record_ids:
                if rs.invoicevalue == False:
                    raise exceptions.ValidationError('消费明细不能有空记录，请选择或删除！')
                if float(rs.invoicevalue) >= 5000:
                    raise exceptions.ValidationError('消费明细金额大于等于5000的记录需走专项申请，请删除！')
                a.append(rs.expensecatelog.id)  #将类别ID存入list进行循环检查是否相等。

            s_len = len(set(a))
            if s_len != 1:
                raise exceptions.ValidationError("请检查费用类别，一张单据费用类别必须相同！")


    @api.constrains('benefitdep_ids')
    def _check2_benefitdep(self):
        if len(self.benefitdep_ids)<1:
            raise exceptions.ValidationError("请选择受益部门！")


        total_sharepercent = 0
        for rec in self.benefitdep_ids:

            if rec.name.id==False:
                raise exceptions.ValidationError('受益部门不能有空记录，请选择或删除！')

            total_sharepercent = total_sharepercent + int(rec.sharepercent)
            if int(rec.sharepercent) <= 0 or int(rec.sharepercent) > 100:
                raise exceptions.ValidationError('受益部门分摊比例不能大于100或小于0！')

        if total_sharepercent != 100:
            raise exceptions.ValidationError('受益部门分摊比例总和为100%！')

    @api.constrains('chuchaishijian_ids','record_ids')
    def _check3_chuchai(self):
        for rc in self.chuchaishijian_ids:
            if rc.name.id==False:
                raise exceptions.ValidationError('出差申请单不能有空记录，请选择或删除！')


        for rec in self:
            for rs in rec.record_ids:

                if rs.expensecatelog.name == u"差旅费" and len(self.chuchaishijian_ids) < 1:
                    raise exceptions.ValidationError('请选择出差申请单！')



    @api.onchange('paycatelog')
    def _clear_bank_info(self):
        # print  self.paycatelog

        if self.paycatelog=='fukuangeigongyingshang':
            self.shoukuanrenxinming=''
            self.kaihuhang=''
            self.yinhangkahao=''
        elif self.paycatelog=='fukuangeiyuangong':
            self.shoukuanrenxinming=self.env['hr.employee'].search( [('login', '=', self.env.user.login)]).full_name
            self.kaihuhang='' and self.env['hr.employee'].search( [('login', '=', self.env.user.login)]).bankaddr
            self.yinhangkahao='' and self.env['hr.employee'].search( [('login', '=', self.env.user.login)]).bankcardno


    @api.model
    def create(self,vals):

        #计算单号

         baseid = 'BX' + time.strftime("%Y%m%d", time.localtime())

         r = self.env['dtdream.expense.report'].search([('create_date','like',datetime.now().strftime('%Y-%m-%d')+"%")],limit=1,order='id desc').id+1

         if r < 10:
             baseid += '00' + str(r)
         elif r >= 10 and r < 100:
             baseid += '0' + str(r)
         else:
             baseid +=str(r)

         vals['expensecode']=baseid


         result = super(dtdream_expense_report, self).create(vals)

# #计算消费明细中发生日期最大值。
#          for ra in result:
#              a = []
#              for rb in ra.record_ids:
#                  a.append(datetime.strptime(rb.currentdate,'%Y-%m-%d'))
#
#
#              #最大日期
#              maxdate =  max(a)
#
#              #建单日期
#              createdate=datetime.strptime(ra.create_date,'%Y-%m-%d %H:%M:%S')
# #计算保存时间与最大值差。
#              months = (createdate-maxdate).days/30.0
# #计算超期罚款系数
#              if months<=1:
#                  xishu=1
#              elif months>1 and months<=2:
#                  xishu=0.97
#              elif months>2 and months<=3:
#                  xishu=0.96
#              elif months>3 and months<=4:
#                  xishu=0.94
#              elif months>4 and months<=5:
#                  xishu=0.92
#              elif months>5 and months<=6:
#                  xishu=0.90
#              elif months>6:
#                  xishu=0
#
#
# #循环计算消费记录的超期时长及罚款金额
#              total_invoice = 0.0
#              total_koujian = 0.0
#              total_shibao = 0.0
#              for rd in ra.record_ids:
#
#                  print '------------------------1'
#                  r_shibaoamount =rd.invoicevalue*xishu
#                  r_koujianamount = rd.invoicevalue-r_shibaoamount
#
#                  rd.outtimenumber=months
#                  rd.koujianamount=r_koujianamount
#                  rd.shibaoamount=r_shibaoamount


             #     total_invoice += rd.invoicevalue
             #     total_koujian += r_koujianamount
             #
             # total_shibao = total_invoice-total_koujian

             # if ra.total_invoicevalue != total_invoice:
             #     ra.total_invoicevalue = total_invoice
             # if ra.total_koujianamount != total_koujian:
             #     ra.total_koujianamount = total_koujian
             #
             # if ra.total_shibaoamount != total_shibao:
             #     ra.total_shibaoamount = total_shibao




         return result

    # @api.multi
    # def write(self, vals):
    #
    #     result = super(dtdream_expense_report, self).write(vals)

        # # # 计算消费明细中发生日期最大值。
        # for ra in self:
        #     if self.state =='draft':
        #
        #         a = []
        #         for rb in ra.record_ids:
        #                 a.append(datetime.strptime(rb.currentdate, '%Y-%m-%d'))
        #
        #                 # print rb.record_id.invoicevalue
        #         maxdate = max(a)
        #         # 建单日期
        #         createdate = datetime.strptime(self.create_date, '%Y-%m-%d %H:%M:%S')
        #         # 计算保存时间与最大值差。
        #         months = (createdate - maxdate).days / 30.0
        #         # 计算超期罚款系数
        #         if months <= 1:
        #             xishu = 1
        #         elif months > 1 and months <= 2:
        #             xishu = 0.97
        #         elif months > 2 and months <= 3:
        #             xishu = 0.96
        #         elif months > 3 and months <= 4:
        #             xishu = 0.94
        #         elif months > 4 and months <= 5:
        #             xishu = 0.92
        #         elif months > 5 and months <= 6:
        #             xishu = 0.90
        #         elif months > 6:
        #             xishu = 0
        #
        #         total_invoice = 0.0
        #         total_koujian = 0.0
        #         total_shibao = 0.0
        #
        #         for rd in ra.record_ids:
        #             r_shibaoamount = rd.invoicevalue * xishu
        #             r_koujianamount = rd.invoicevalue - r_shibaoamount
        #
        #             rd.outtimenumber = months
        #             rd.koujianamount = r_koujianamount
        #             rd.shibaoamount = r_shibaoamount
        #
        #             total_invoice += rd.invoicevalue
        #             total_koujian += r_koujianamount
        #
        #         total_shibao = total_invoice - total_koujian

                #print '-----',ra
                # if ra.total_invoicevalue != total_invoice:
                #
                #     ra.total_invoicevalue = total_invoice
                # if ra.total_koujianamount != total_koujian:
                #
                #     ra.total_koujianamount = total_koujian
                #
                # if ra.total_shibaoamount != total_shibao:
                #     ra.total_shibaoamount = total_shibao

        # return result

    @api.multi
    def unlink(self):

        if self.state == "draft" and self.create_uid.id == self.env.user.id:
            for rec in self:
                # 取消该模型dtdream_expense_record_baoxiao
                # sql = "delete from dtdream_expense_record_baoxiao where report_id =%s" % (rec.id)  # 删除消费明细与报销单的对应关系
                #
                # self.env.cr.execute(sql)

                sql1 = "delete from dtdream_expense_chuchai where report_id =%s" % (rec.id)  # 删除出差单与报销单的对应关系

                self.env.cr.execute(sql1)

                sql2 = "delete from dtdream_expense_benefitdep where report_id =%s" % (rec.id)  # 删除受益部门与报销单的对应关系

                self.env.cr.execute(sql2)

            return super(dtdream_expense_report, self).unlink()
        else:
            raise exceptions.ValidationError('报销单只能在草稿状态下删除！')

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

       #驳回到申请人时，修改状态为草稿，当前处理人为空。
        if self.state !="draft":
           self.write({"hasauditor": [(4, self.currentauditperson.id)]})
        self.write({'state': 'draft', 'currentauditperson': False,'currentauditperson_userid': False})
       # 同步更新消费记录状态

        record_ids = self.env['dtdream.expense.record'].search([('report_id', '=', self.id)])
        for rc in record_ids:
            rc.write({'state': 'draft'})


    @api.multi
    def action_xingzheng(self):
        try:

            zongcai_hr_employee_id = self.get_company_president()  # 总裁在hr.employee中的id
            xingzheng_id_hr_employee = self.get_xingzheng(self.create_uid.id)  # 行政助理hr.employee中id
            jiekoukuaiji = self.get_jiekoukuaiji(self.create_uid.id)  # 接口会计
        except Exception:

            raise exceptions.ValidationError("参数配置不全，请联系管理员！")

        re_state = ''
        re_currentauditperson = ''
        re_currentauditperson_userid = ''
        message=''
        emailto=''
    #提交单据
        if self.state == 'draft':
            #如果是总裁提交直接到接口会计，否则到行政助理处审批。
            if zongcai_hr_employee_id ==self.get_employee_id(self.create_uid.id):
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

            self.send_mail(u"【提醒】{0}于{1}提交的费用报销单,请您审批!".format(self.create_uid.name, self.create_date[:10]),
                           u"%s提交的费用报销单,等待您的审批!" % self.create_uid.name,
                           email_to=emailto)

            #更新报销单状态及处理人，待审批人
            self.write({'state':re_state,'currentauditperson':re_currentauditperson,'currentauditperson_userid':re_currentauditperson_userid})

            #同步更新消费记录状态

            record_ids = self.env['dtdream.expense.record'].search([('report_id', '=', self.id)])
            for rc in record_ids:
                rc.write({'state': re_state})


        #主管,权签人，接口会计，驳回到行政助理
        elif self.state == 'zhuguan' or self.state == 'quanqianren' or self.state == 'jiekoukuaiji':

            re_state = 'xingzheng'
            re_currentauditperson = xingzheng_id_hr_employee
            re_currentauditperson_userid = self.get_user_id(xingzheng_id_hr_employee)

            # 更新报销单状态及处理人，待审批人
            self.write({"hasauditor": [(4, self.currentauditperson.id)]})
            self.write({'state': re_state, 'currentauditperson': re_currentauditperson,
                        'currentauditperson_userid': re_currentauditperson_userid})

            # 同步更新消费记录状态
            record_ids = self.env['dtdream.expense.record'].search([('report_id', '=', self.id)])
            for rc in record_ids:
                rc.write({'state': re_state})


    @api.multi
    def action_zhuguan(self):
        try:

            zongcai_hr_employee_id = self.get_company_president()  # 总裁在hr.employee中的id
            zhuguan_id_hr_employee = self.get_zhuguan(self.create_uid.id)  # 主管hr.employee中id
            no_one_auditor_hr_employee = self.get_no_one_auditor(self.create_uid.id)  # 第一审批人在hr.employee中id
            no_one_auditor_amount = self.get_no_one_auditor_amount(self.create_uid.id)  # 第一审批人上限金额
            no_two_auditor_hr_employee = self.get_no_two_auditor(self.create_uid.id)  # 第二审批人在hr.employee中id
            no_two_auditor_amount = self.get_no_two_auditor_amount(self.create_uid.id)  # 第二审批人上限金额
            jiekoukuaiji = self.get_jiekoukuaiji(self.create_uid.id)  # 接口会计
            # currentauditperson = self.currentauditperson.id  # 本单当前处理人
            zhuguan_login = self.get_employee_login(zhuguan_id_hr_employee)
            parentdepartmentid = self.get_employee_parentdepartmentid(zhuguan_login)  # 上级部门是否为空，为空则为一级，否则为二级
            create_hr_id = self.get_employee_id(self.create_uid.id)  # 本单创建人hr.employee中id
            xingzheng_id_hr_employee = self.get_xingzheng(self.create_uid.id)  # 行政助理hr.employee中id
        except Exception:

            raise exceptions.ValidationError("参数配置不全，请联系管理员！")

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

        # 更新报销单
        self.write({"hasauditor": [(4, self.currentauditperson.id)]})
        self.write({'state': re_state, 'currentauditperson': re_currentauditperson,
                    'currentauditperson_userid': re_currentauditperson_userid})

        # 更新消费记录状态
        record_ids = self.env['dtdream.expense.record'].search([('report_id', '=', self.id)])
        for rc in record_ids:
            rc.write({'state': re_state})


    @api.multi
    def action_quanqianren(self):
        try:

            zongcai_hr_employee_id = self.get_company_president()  #总裁在hr.employee中的id
            zhuguan_id_hr_employee = self.get_zhuguan(self.create_uid.id)  #主管hr.employee中id
            no_one_auditor_hr_employee =  self.get_no_one_auditor(self.create_uid.id) #第一审批人在hr.employee中id
            no_one_auditor_amount =  self.get_no_one_auditor_amount(self.create_uid.id)    #第一审批人上限金额
            no_two_auditor_hr_employee = self.get_no_two_auditor(self.create_uid.id)  # 第二审批人在hr.employee中id
            no_two_auditor_amount =  self.get_no_two_auditor_amount(self.create_uid.id)  # 第二审批人上限金额
            jiekoukuaiji  = self.get_jiekoukuaiji(self.create_uid.id) # 接口会计
            zhuguan_login = self.get_employee_login(zhuguan_id_hr_employee)
            parentdepartmentid = self.get_employee_parentdepartmentid(zhuguan_login)  # 上级部门是否为空，为空则为一级，否则为二级
            create_hr_id = self.get_employee_id(self.create_uid.id)  # 本单创建人hr.employee中id
        except Exception:

            raise exceptions.ValidationError("参数配置不全，请联系管理员！")

        re_state = ''
        re_currentauditperson=''
        re_currentauditperson_userid=''


#判断该单审批主管
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
        elif zhuguanauditperson == no_two_auditor_hr_employee and self.total_invoicevalue<=no_two_auditor_amount:  # 如果是一级主管到接口会计
            re_state = 'jiekoukuaiji'
            re_currentauditperson = jiekoukuaiji
            re_currentauditperson_userid = self.get_user_id(jiekoukuaiji)
        elif zhuguanauditperson == no_two_auditor_hr_employee and self.total_invoicevalue > no_two_auditor_amount:  # 如果是一级主管到接口会计
            re_state = 'quanqianren'
            re_currentauditperson = zongcai_hr_employee_id
            re_currentauditperson_userid = self.get_user_id(zongcai_hr_employee_id)
        elif zhuguanauditperson == no_one_auditor_hr_employee and self.total_invoicevalue<=no_one_auditor_amount:
            re_state = 'jiekoukuaiji'
            re_currentauditperson = jiekoukuaiji
            re_currentauditperson_userid = self.get_user_id(jiekoukuaiji)
        elif zhuguanauditperson == no_one_auditor_hr_employee and self.total_invoicevalue > no_one_auditor_amount:
            re_state = 'quanqianren'
            re_currentauditperson = no_two_auditor_hr_employee
            re_currentauditperson_userid = self.get_user_id(no_two_auditor_hr_employee)

        else:
            re_state = 'quanqianren'
            re_currentauditperson = no_one_auditor_hr_employee
            re_currentauditperson_userid = self.get_user_id(no_one_auditor_hr_employee)


        #更新报销单
        self.write({"hasauditor": [(4, self.currentauditperson.id)]})
        self.write({'state': re_state, 'currentauditperson': re_currentauditperson,'currentauditperson_userid': re_currentauditperson_userid})

        # 更新消费记录状态
        record_ids = self.env['dtdream.expense.record'].search([('report_id', '=', self.id)])
        for rc in record_ids:
            rc.write({'state': re_state})


    @api.multi
    def action_jiekoukuaiji(self):
        try:



            jiekoukuaiji  = self.get_jiekoukuaiji(self.create_uid.id) # 接口会计



            re_state = 'jiekoukuaiji'
            re_currentauditperson = jiekoukuaiji
            re_currentauditperson_userid = self.get_user_id(jiekoukuaiji)

        except Exception:

            raise exceptions.ValidationError("参数配置不全，请联系管理员！")

        # 更新报销单

        self.write({'state': re_state, 'currentauditperson': re_currentauditperson,
                    'currentauditperson_userid': re_currentauditperson_userid})

        # 更新消费记录状态
        record_ids = self.env['dtdream.expense.record'].search([('report_id', '=', self.id)])
        for rc in record_ids:
            rc.write({'state': re_state})


    @api.multi
    def action_daifukuan(self):
        # 根据提交人的部门查找当前处理人
        hr_employee_login = self.env['res.users'].search([('id', '=', self.create_uid.id)]).login

        depid = self.env['hr.employee'].search([('login', '=', hr_employee_login)]).department_id[0].id
        assistant_ids = self.env['hr.department'].search([('id', '=', depid)]).chunakuaiji[0].id  ############

        assistant_login = self.env['hr.department'].search([('id', '=', depid)]).chunakuaiji[0].login  ############
        # print assistant_login

        currentauditpersonuserid = self.env['res.users'].search([('login', '=',
                                                                  assistant_login)]).id  # currentauditperson字段存的是hr.employee的id，视图中的uid是res.users的id，故需转换，方便在视图待我审批菜单使用。
        # print self.env['res.users'].search( [('login', '=', assistant_login)])

        self.write({"hasauditor": [(4, self.currentauditperson.id)]})
        self.write({'state': 'daifukuan', 'currentauditperson': assistant_ids,
                    'currentauditperson_userid': currentauditpersonuserid})

        # 同步更新消费记录状态
        record_ids = self.env['dtdream.expense.record'].search([('report_id', '=', self.id)])
        for rc in record_ids:
            rc.write({'state': 'daifukuan'})


    @api.multi
    def action_yifukuan(self):


        # 同步更新消费记录状态
        record_ids = self.env['dtdream.expense.record'].search([('report_id', '=', self.id)])
        for rc in record_ids:
            rc.write({'state': 'yifukuan'})



        if self.state =="daifukuan":
            message = u"出纳确认付款，状态：待付款---->已付款。"
            self.message_post(body=message)

        self.write({"hasauditor": [(4, self.currentauditperson.id)]})
        self.write({'state': 'yifukuan', 'currentauditperson': '', 'currentauditperson_userid': ''})

        #发送邮件
        hr_employee_login = self.env['res.users'].search([('id', '=', self.create_uid.id)]).login

        shenqinren = self.env['hr.employee'].search([('login', '=', hr_employee_login)])

        self.send_mail(u"【提醒】您于{0}提交的费用报销单已完成审批!".format(self.create_date[:10]),u"您提交的费用报销单已完成审批，请等待付款。" , email_to=shenqinren.work_email)

    @api.multi
    def btn_checkpaper(self):
        if self.state=="xingzheng":
            message = u"行政助理已签收纸件。"

            self.showcuiqian='1'
            self.message_post(body=message)
        elif self.state=="jiekoukuaiji":
            message = u"接口会计已签收纸件。"
            self.showcuiqian = '2'
            self.message_post(body=message)

    @api.multi
    def btn_cuiqian(self):
        self.send_mail(u"【邮催】{0}于{1}提交的费用报销单,请您尽快审批!".format(self.create_uid.name, self.create_date[:10]),u"%s提交的费用报销单,等待您的审批" % self.create_uid.name, email_to=self.currentauditperson.work_email)
        message = u"申请人发送了邮催。"
        self.message_post(body=message)



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

    @api.depends('name')
    def _compute_chuchai_fields(self):
        for rec in self:
            rec.endtime = rec.name.endtime
            rec.startaddress = rec.name.startaddress
            rec.endaddress =rec.name.endaddress
            rec.reason = rec.name.reason


    def _filter_chuchai_record(self):
        return [('id', 'not in', [cr.name.id for cr in self.search([])]), ('create_uid', '=', self.env.user.id)]

    name = fields.Many2one('dtdream.travel.journey',string="出差时间" ,domain=_filter_chuchai_record)      #domain=lambda self:[('create_uid','=',self.env.user.id),('name','!=',False)])

    report_id = fields.Many2one("dtdream.expense.report",string="报销单ID")

    endtime = fields.Date(string="结束时间",compute=_compute_chuchai_fields)
    startaddress = fields.Char(string="出发地",compute=_compute_chuchai_fields)
    endaddress = fields.Char(string="目的地",compute=_compute_chuchai_fields)
    reason = fields.Text(string="出差原因",compute=_compute_chuchai_fields)


    _sql_constraints = [
        ('chuchai_id_unique','UNIQUE(name)',"出差时间重复，请重新选择！")
    ]

#公司总裁配置
class dtdream_expense_president(models.Model):
    _name = "dtdream.expense.president"

    name = fields.Many2one("hr.employee",string="姓名")
    type = fields.Selection([('zongcai','总裁'),('fuzongcai','副总裁')])










