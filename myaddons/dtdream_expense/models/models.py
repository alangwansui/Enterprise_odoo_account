# -*- coding: utf-8 -*-

from openerp import models, fields, api
from datetime import datetime


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

    name = fields.Char(string="名称")


#费用明细模型
class dtdream_expense_detail(models.Model):
    _name = "dtdream.expense.detail"

    name = fields.Char(string="名称")
    parentid = fields.Many2one("dtdream.expense.catelog",string="费用类别")


