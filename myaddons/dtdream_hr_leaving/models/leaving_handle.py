# -*- coding: utf-8 -*-

from openerp import models, fields, api
# 离职办理
class leaving_handle(models.Model):
    _name = 'leaving.handle'

    @api.depends('name')
    def _compute_employee(self):
        for rec in self:
            rec.job_number=rec.name.job_number
            rec.full_name=rec.name.full_name
            rec.post=rec.name.post
            rec.entry_day=rec.name.entry_day
            rec.department=rec.name.department_id.complete_name

    name = fields.Many2one("hr.employee",string="花名",required=True)
    full_name = fields.Char(compute=_compute_employee,string="姓名")
    job_number = fields.Char(compute=_compute_employee,string="工号")
    post = fields.Char(compute=_compute_employee,string="岗位")
    entry_day = fields.Date(compute=_compute_employee,string="入职日期")
    department = fields.Char(compute=_compute_employee,string="部门")
    leave_date = fields.Date("计划离职日期")
    state = fields.Selection([('0','办理申请'),('1','离职办理确认'),('2','工作交接确认'),('3','员工离岗确认'),
                              ('4','离职手续办理完毕确认'),('5','启动离职结算'),('9','通过')], default="0")


#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100