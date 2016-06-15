# -*- coding: utf-8 -*-

from openerp import models, fields, api


class dtdream_hr_performance(models.Model):
    _name = "dtdream.hr.performance"
    _inherit = ['mail.thread']

    @api.onchange('department', 'quarter')
    def _onchange_compute_hr_pbc(self):
        if self.department and self.quarter:
            cr = self.env['dtdream.hr.pbc'].search([('quarter', '=', self.quarter), '|', ('name', '=', self.department.parent_id.id), ('name', '=', self.department.id)])
            self.pbc = cr

    @api.model
    def create(self, vals):
        pbc = vals.get('pbc', '')
        for val in pbc:
            val[0] = 4
        vals['pbc'] = pbc
        return super(dtdream_hr_performance, self).create(vals)

    department = fields.Many2one('hr.department', string='部门')
    name = fields.Many2one('hr.employee', string='花名', required=True)
    workid = fields.Char(string='工号')
    quarter = fields.Selection([('1', '第一季度'),
                                ('2', '第二季度'),
                                ('3', '第三季度'),
                                ('4', '第四季度'),
                                ], string='考核季度', required=True)
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
    pbc = fields.Many2many('dtdream.hr.pbc', string="部门PBC")


class dtdream_hr_pbc(models.Model):
    _name = "dtdream.hr.pbc"
    _inherit = ['mail.thread']

    name = fields.Many2one('hr.department', string='部门', required=True)
    quarter = fields.Selection([('1', '第一季度'),
                                ('2', '第二季度'),
                                ('3', '第三季度'),
                                ('4', '第四季度'),
                                ], string='考核季度', required=True)
    target = fields.One2many('dtdream.pbc.target', 'target', string='工作内容')

    _sql_constraints = [
        ('name_quarter_uniq', 'unique (name,quarter)', '每个季度只能有一条PBC !')
    ]


class dtdream_pbc_target(models.Model):
    _name = "dtdream.pbc.target"

    target = fields.Many2one('dtdream.hr.pbc', string='部门PBC')
    num = fields.Integer(string='序号')
    works = fields.Text(string='工作内容', required=True)
