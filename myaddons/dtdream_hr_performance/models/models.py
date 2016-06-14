# -*- coding: utf-8 -*-

from openerp import models, fields, api


class dtdream_hr_pbc(models.Model):
    _name = "dtdream.hr.pbc"
    _inherit = ['mail.thread']

    name = fields.Char(default=lambda self: '部门PBC')
    department = fields.Many2one('hr.department', string='部门')
    quarter = fields.Selection([('1', '第一季度'),
                                ('2', '第二季度'),
                                ('3', '第三季度'),
                                ('4', '第四季度'),
                                ], string='考核季度')
    target = fields.One2many('dtdream.pbc.target', 'target', string='目标')


class dtdream_hr_performance(models.Model):
    _name = "dtdream.hr.performance"
    _inherit = ['mail.thread']


    @api.onchange('department', 'quarter')
    def _onchange_compute_hr_pbc(self):
        if self.department and self.quarter:
            cr = self.env['dtdream.hr.pbc'].search([('quarter', '=', self.quarter), '|', ('department', '=', self.department.parent_id.id), ('department', '=', self.department.id)])
            for crr in cr:
                self.env['dtdream.hr.per.pbc'].create({'name': crr.department.id, 'target': crr.target, 'perform': self.id})

    department = fields.Many2one('hr.department', string='部门')
    name = fields.Many2one('hr.employee', string='花名')
    workid = fields.Char(string='工号')
    quarter = fields.Selection([('1', '第一季度'),
                                ('2', '第二季度'),
                                ('3', '第三季度'),
                                ('4', '第四季度'),
                                ], string='考核季度')
    officer = fields.Many2one('hr.employee', string='主管')
    result = fields.Char(string='考核结果')
    onwork = fields.Selection([('Inaugural_state_01', '在职'), ('Inaugural_state_02','离职')], "在职状态")
    state = fields.Selection([('0', '待启动'),
                              ('1', '待填写PBC'),
                              ('2', '待主管确认'),
                              ('3', '待考评启动'),
                              ('4', '待总结'),
                              ('5', '待主管评价'),
                              ('6', '待最终考评'),
                              ('99', '考评完成')
                              ], string='状态', default='0')
    hr_pbc = fields.One2many('dtdream.hr.per.pbc', 'perform', string="部门PBC")


class dtdream_hr_per_pbc(models.Model):
    _name = "dtdream.hr.per.pbc"

    name = fields.Many2one('hr.department', string='部门名称')
    perform = fields.Many2one('dtdream.hr.performance')
    target = fields.One2many('dtdream.pbc.target', 'per_target', string='工作内容')


class dtdream_pbc_target(models.Model):
    _name = "dtdream.pbc.target"

    target = fields.Many2one('dtdream.hr.pbc', string='部门PBC')
    per_target = fields.Many2one('dtdream.hr.per.pbc')
    num = fields.Integer(string='序号')
    works = fields.Text(string='工作内容')
