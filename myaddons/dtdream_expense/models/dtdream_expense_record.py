# -*- coding: utf-8 -*-

from openerp import models, fields, api, exceptions, tools
from datetime import datetime, time
from openerp.exceptions import ValidationError, Warning
import time

import logging

_logger = logging.getLogger(__name__)


# 消费记录模型，created by lucongjin 20160612
class dtdream_expense_record(models.Model):
    _name = "dtdream.expense.record"
    _inherit = ['mail.thread']
    _description = u"消费明细"

    @api.multi
    @api.depends('koujianamount', 'invoicevalue')
    def _compute_shibaoamount(self):
        for record in self:
            record.shibaoamount = record.invoicevalue - record.koujianamount

    @api.multi
    @api.depends('report_ids')
    def _compute_report_ids_count(self):
        #_logger.info("calculate.....")
        for record in self:
            if record.report_ids:
                record.report_ids_count = len(record.report_ids)
            else:
                record.report_ids_count = 0


    name = fields.Char(string="记录标题")  # 没用，仅为了链接不显示模型名称
    state = fields.Selection([('draft', '草稿'), ('xingzheng', '行政助理审批'), ('zhuguan', '主管审批'), ('quanqianren', '权签人审批'),
                              ('jiekoukuaiji', '接口会计审批'), ('daifukuan', '待付款'), ('yifukuan', '已付款')], string="状态",
                             default="draft")
    expensecatelog = fields.Many2one("dtdream.expense.catelog", string="费用类别", required=True,
                                     track_visibility='onchange')
    expensedetail = fields.Many2one("dtdream.expense.detail", string="消费明细", required=True, track_visibility='onchange')
    invoicevalue = fields.Float(digits=(11, 2), required=True, string='票据金额(元)', track_visibility='onchange')
    outtimenumber = fields.Float(digits=(11, 2), string="超期时长(月)")
    koujianamount = fields.Float(digits=(11, 2), string="扣减金额(元)", track_visibility='onchange')
    shibaoamount = fields.Float(digits=(11, 2), string="实报金额(元)", compute=_compute_shibaoamount, store=True)
    currentdate = fields.Date(string="发生日期", default=lambda self: datetime.now(), track_visibility='onchange')
    # expenseenddate = fields.Date(string="费用发生结束日期" ,default=lambda self:datetime.now())
    city = fields.Many2one("dtdream.expense.city", string="发生城市", track_visibility='onchange')
    province = fields.Many2one("res.country.state", string="发生省份", track_visibility='onchange')
    # attachment = fields.Binary(store=True,string="附件",track_visibility='onchange')

    attachment_ids = fields.One2many('dtdream.expense.record.attachment', 'record_id', u'附件明细')

    report_ids = fields.Many2many("dtdream.expense.report", "dtdream_exprense_record_report_ref", "report_id",
                                  "record_id", string="报销单ID")

    report_ids_count = fields.Integer(compute=_compute_report_ids_count, store=True)



    @api.multi
    @api.onchange('report_ids', 'koujianamount', 'invoicevalue', 'currentdate')
    def _calaulte_record_ids(self):
        for record in self:
            if record.report_ids:

                for report in record.report_ids:
                    report._compute_total_koujianamount()

    @api.model
    def create_expense_record_baoxiao(self):
        context = dict(self._context or {})
        active_model = context.get('active_model')
        active_ids = context.get("active_ids")
        expense_ids = self.browse(active_ids)
        record_ids = []
        for expense in expense_ids:
            if expense.create_uid.id != self.env.user.id:
                raise Warning(u'只能对自己的费用明细生成报销单')
            if expense.report_ids:
                raise Warning(u'%s 已经生成了报销单' % (expense.expensedetail.name))

        vals = {
            'record_ids': [(6, 0, active_ids)],
            'benefitdep_ids': [(0, 0, {
                'name': self.env['hr.employee'].search([('login', '=', self.env.user.login)]).department_id.id,
                'sharepercent': 100
            })]
        }

        #_logger.info("vals:" + str(vals))
        report_id = self.env['dtdream.expense.report'].create(vals)

        _logger.info("report_id:" + str(report_id))

        return {
            'type': 'ir.actions.act_window',
            'name': u'我的报销单',
            'res_model': 'dtdream.expense.report',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'view_id': False,
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
        # print type(str(vals['currentdate']))

        if vals.has_key('expensedetail'):
            full_name = self.env['hr.employee'].search([('login', '=', self.env.user.login)]).full_name
            if not full_name:
                raise Warning(u'请先在员工档案中维护当前用户的员工信息。')
            recordname = full_name + '-' + \
                         self.env['dtdream.expense.detail'].search([('id', '=', vals['expensedetail'])])[
                             0].name + '(' + time.strftime('%Y%m%d',
                                                           time.strptime(vals['currentdate'], '%Y-%m-%d')) + ')'
            vals['name'] = recordname
        result = super(dtdream_expense_record, self).create(vals)
        return result

    # 费用类别与费用明细联动
    # @api.onchange("expensecatelog")
    # def onchange_expensecatelog(self):
    #     if self.expensecatelog:
    #         if self.expensedetail.parentid != self.expensecatelog:
    #             self.expensedetail = ""
    #         return {
    #             'domain': {
    #                 "expensedetail":[('parentid','=',self.expensecatelog.id)]
    #             }
    #         }

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

    @api.onchange("province")
    def onchange_province(self):
        if self.province:
            if self.city.provinceid != self.city:
                self.city = ""
            return {
                'domain': {
                    "city": [('provinceid', '=', self.province.id)]
                }
            }

    @api.multi
    def unlink(self):
        for record in self:
            if record.report_ids:
                raise Warning("已报销记录不能删除!")
            if record.create_uid.id != self.env.user.id:
                raise Warning(u'只能删除自己的消费记录!')
            res = super(dtdream_expense_record, self).unlink()
            return res
