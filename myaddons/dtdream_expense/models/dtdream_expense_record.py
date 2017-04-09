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
    @api.depends('taxamount', 'invoicevalue','koujianamount','kuanji_koujian')
    def _compute_notaxamount(self):
        for record in self:
            record.shibaoamount = record.invoicevalue - record.koujianamount - record.kuanji_koujian
            record.notaxamount = record.shibaoamount-record.taxamount

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
    applicant = fields.Many2one('hr.employee', string='申请人',
                                default=lambda self: self.env['hr.employee'].search([('user_id', '=', self.env.user.id)]))
    state = fields.Selection([('draft', '草稿'), ('xingzheng', '行政助理审批'), ('zhuguan', '主管审批'), ('quanqianren', '权签人审批'),
                              ('jiekoukuaiji', '接口会计审批'), ('daifukuan', '待付款'), ('yifukuan', '已付款')], string="状态",
                             default="draft")
    expensecatelog = fields.Many2one("dtdream.expense.catelog", string="费用类别", required=True,
                                     track_visibility='onchange')
    expensedetail = fields.Many2one("dtdream.expense.detail", string="消费明细", required=True, track_visibility='onchange')
    invoicevalue = fields.Float(digits=(11, 2), required=True, string='票据金额(元)', track_visibility='onchange')
    outtimenumber = fields.Float(digits=(11, 2), string="超期时长(月)")

    taxamount = fields.Float(digits=(11, 2), string="税金",default = 0)
    notaxamount = fields.Float(digits=(11, 2), string="不含税金额",compute = _compute_notaxamount)
    taxpercent = fields.Selection([('0.03', '3%'), ('0.05', '5%'), ('0.06', '6%'), ('0.11', '11%'),('0.17', '17%')],string='税率')
    koujianamount = fields.Float(digits=(11, 2), string="超期扣款(元)")
    kuanji_koujian = fields.Float(digits=(11, 2),string="接口会计扣款(元)")
    @api.constrains('kuanji_koujian')
    def check_if_gt_invoicevalue(self):
        if self.kuanji_koujian > self.invoicevalue:
            raise ValidationError("接口会计扣款金额不能大于票据金额！")
    shibaoamount = fields.Float(digits=(11, 2), string="实报金额(元)", compute=_compute_notaxamount, store=True)
    currentdate = fields.Date(string="发生日期", default=lambda self: datetime.now(), track_visibility='onchange')
    city = fields.Many2one("dtdream.expense.city",required=True, string="发生城市", track_visibility='onchange',default= lambda self:self.search([('create_uid','=',self.env.user.id)],order="id desc",limit=1).city)
    province = fields.Many2one("res.country.state",required=True, string="发生省份", track_visibility='onchange',default= lambda self:self.search([('create_uid','=',self.env.user.id)],order="id desc",limit=1).city.provinceid)
    actiondesc = fields.Text(string="活动描述")
    customernumber=fields.Integer(string="客户人数")
    peitongnumber = fields.Integer(string="陪同人数")
    @api.constrains("expensedetail","customernumber","peitongnumber")
    def check_id_all_zero(self):
        if self.expensecatelog.name == u"日常业务费" and self.customernumber == 0 and self.peitongnumber == 0:
            raise ValidationError(u"日常业务费客户人数和陪同人数不能同时为0")
        if self.customernumber < 0 or self.peitongnumber < 0:
            raise ValidationError(u"客户人数和陪同人数不能小于0")

    @api.multi
    @api.depends('customernumber', 'invoicevalue','peitongnumber')
    def _compute_everyonecost(self):
        for record in self:
            if (int(record.customernumber)+int(record.peitongnumber)) >0:
                record.everyonecost = record.invoicevalue/(int(record.customernumber)+int(record.peitongnumber))

    everyonecost = fields.Float(digits=(11, 2),string="人均消费(元)",compute=_compute_everyonecost, store=True)
    visible_all = fields.Boolean(default=False,string="是否隐藏客户人数、陪同人数，人均消费")
    attachment_ids = fields.One2many('dtdream.expense.record.attachment', 'record_id', u'附件明细')
    @api.constrains("attachment_ids")
    def attachment_ids_che(self):
        for attachment in self.attachment_ids:
            if not attachment.image:
                self.attachment_ids = [(2,attachment.id)]
    report_ids = fields.Many2many("dtdream.expense.report", "dtdream_exprense_record_report_ref", "report_id",
                                  "record_id", string="报销单ID")
    report_ids_count = fields.Integer(compute=_compute_report_ids_count, store=True)

    @api.multi
    @api.onchange('report_ids', 'koujianamount', 'invoicevalue', 'currentdate','kuanji_koujian')
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
        expense_parentids=[]
        applicant_ids = set()
        for expense in expense_ids:
            applicant_ids.add(expense.applicant.id)
            if len(expense_parentids) == 0:
                expense_parentids.append(expense.expensedetail.parentid.id)
            else:
                if expense.expensedetail.parentid.id not in expense_parentids:
                    raise Warning(u'一张报销单中的费用类别必须相同')
            if len(applicant_ids) > 1:
                raise ValidationError("请保持所有消费明细申请人一致！")
            if expense.create_uid.id != self.env.user.id:
                raise Warning(u'只能对自己的费用明细生成报销单')
            if expense.report_ids:
                raise Warning(u'%s 已经生成了报销单' % (expense.expensedetail.name))

        vals = {
            'applicant': expense_ids[0].applicant.id,
            'record_ids': [(6, 0, active_ids)]
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
            if float(rec.invoicevalue) <= float(0):
                raise exceptions.ValidationError('票据金额不能小于等于0！')
            if rec.invoicevalue >1000000000:
                raise exceptions.ValidationError('亲！您真的有这么多钱要报销吗？')

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

    @api.constrains('invoicevalue','expensecatelog')
    def _check_daily_gt_f_thousand(self):
        if self.invoicevalue>5000 and self.expensecatelog.name == u'日常业务费':
            raise ValidationError('大于5000元的日常业务费,请走专项申请!')

    # 费用类别与费用明细联动
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
        if not self.expensecatelog:
            return{
                'domain':{
                    "expensedetail": [('parentid', '!=', False)]
                }
            }

    @api.onchange("expensedetail")
    def onchange_expensedetail(self):
        if self.expensedetail:
            self.expensecatelog = self.expensedetail.parentid

            if self.expensecatelog.name ==u"日常业务费":
                self.visible_all = False
            else:
                self.visible_all = True

    @api.onchange("province")
    def onchange_province(self):
        if self.province:
            if self.city.provinceid != self.province:
                self.city = ""
            return {
                'domain': {
                    "city": [('provinceid', '=', self.province.id)]
                }
            }
        else:
            return {
                'domain': {
                    "city": [('provinceid', '!=', False)]
                }
            }

    @api.onchange("city")
    def onchange_city(self):
        if self.city:
            self.province = self.city.provinceid

    @api.multi
    def unlink(self):
        for record in self:
            if record.report_ids:
                raise Warning("已报销记录不能删除!")
            if record.create_uid.id != self.env.user.id and record.applicant.user_id.id != self.env.user.id:
                raise Warning(u'只能删除自己的消费记录!')
            res = super(dtdream_expense_record, self).unlink()
            return res

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):

        params = self._context.get('params', None)
        action = params.get("action", 0) if params else 0
        my_action = self.env["ir.actions.act_window"].search([('id', '=', action)])
        res = super(dtdream_expense_record, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=False)
        self.onchange_expensecatelog()
        print res['fields']
        return res
