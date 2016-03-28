# -*- coding: utf-8 -*-

from openerp import models, fields, api
from datetime import datetime
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from dateutil.relativedelta import relativedelta
from openerp.exceptions import ValidationError
class dtdream_hr_holidays_extend(models.Model):
    _inherit = "hr.holidays"
    shenqingren=fields.Char( string="申请人",default=lambda self:self.env['hr.employee'].search([('login','=',self.env.user.login)]).name,readonly=1)
    gonghao=fields.Char(string="工号",default=lambda self:self.env['hr.employee'].search([('login','=',self.env.user.login)]).job_number,readonly=1)
    bumen=fields.Char(string="部门",default=lambda self:self.env['hr.employee'].search([('login','=',self.env.user.login)]).department_id.name,readonly=1)
    create_time= fields.Datetime(string='申请时间',default=datetime.today()- relativedelta(hours=8),readonly=1)

    @api.one
    def _compute_is_shenpiren(self):
        if self.shenpiren.user_id==self.env.user:
            self.is_shenpiren=True
        else:
            self.is_shenpiren=False

    @api.constrains("shenqingren")
    def _compute_has_shenpiren(self):
        print len(self.env['dtdream.hr.holidays.extend.new.menu'].search([('create_uid','=',self.env.user.id)]))
        if len(self.env['dtdream.hr.holidays.extend.new.menu'].search([('create_uid','=',self.env.user.id)])) == 0:
            raise ValidationError('请先配置审批人！')

    is_shenpiren=fields.Boolean(compute=_compute_is_shenpiren,string="是否是审批人")
    has_shenpiren=fields.Boolean(compute=_compute_has_shenpiren,string="是否有审批人")



class dtdream_hr_holidays_extend_new_menu(models.Model):
    _name="dtdream.hr.holidays.extend.new.menu"
    related_user=fields.Many2one("res.users")
    shenpiren1=fields.Many2one('hr.employee',string="第一审批人",required=True)
    shenpiren2=fields.Many2one('hr.employee',string="第二审批人")
    shenpiren3=fields.Many2one('hr.employee',string="第三审批人")
    shenpiren4=fields.Many2one('hr.employee',string="第四审批人")
    shenpiren5=fields.Many2one('hr.employee',string="第五审批人")
    number=fields.Integer(default=lambda self:len(self.search([('create_uid','=',self.env.user.id)])))

    @api.multi
    @api.constrains("number")
    def chuangjian_number(self):
        print self.number
        if self.number > 0:
            raise ValidationError('您已经有审批人配置，请编辑原有记录。')


