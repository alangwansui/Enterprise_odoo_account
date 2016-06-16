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

    @api.depends('name')
    def _compute_employee_info(self):
        for rec in self:
            rec.workid = rec.name.job_number
            rec.department = rec.name.department_id
            rec.onwork = rec.name.Inaugural_state

    @api.model
    def create(self, vals):
        pbc = vals.get('pbc', '')
        for val in pbc:
            val[0] = 4
        vals['pbc'] = pbc
        return super(dtdream_hr_performance, self).create(vals)

    name = fields.Many2one('hr.employee', string='花名', required=True)
    department = fields.Many2one('hr.department', string='部门', compute=_compute_employee_info)
    workid = fields.Char(string='工号', compute=_compute_employee_info)
    quarter = fields.Selection([('1', '第一季度'),
                                ('2', '第二季度'),
                                ('3', '第三季度'),
                                ('4', '第四季度'),
                                ], string='考核季度', required=True)
    officer = fields.Many2one('hr.employee', string='主管')
    result = fields.Char(string='考核结果')
    onwork = fields.Selection([('Inaugural_state_01', '在职'), ('Inaugural_state_02', '离职')],
                              string="在职状态", compute=_compute_employee_info)
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
    pbc_employee = fields.One2many('dtdream.hr.pbc.employee', 'perform', string='个人PBC')

    _sql_constraints = [
        ('name_quarter_uniq', 'unique (name,quarter)', '每个员工每个季度只能有一条员工PBC !')
    ]

    @api.multi
    def wkf_wait_write(self):
        self.write({'state': '1'})

    @api.multi
    def wkf_confirm(self):
        self.write({'state': '2'})

    @api.multi
    def wkf_evaluate(self):
        self.write({'state': '3'})

    @api.multi
    def wkf_conclud(self):
        self.write({'state': '4'})

    @api.multi
    def wkf_rate(self):
        self.write({'state': '5'})

    @api.multi
    def wkf_final(self):
        self.write({'state': '6'})

    @api.multi
    def wkf_done(self):
        self.write({'state': '99'})


class dtdream_hr_pbc_employee(models.Model):
    _name = "dtdream.hr.pbc.employee"

    perform = fields.Many2one('dtdream.hr.performance')
    work = fields.Char(string='工作事项')
    detail = fields.Text(string='工作目标描述')
    result = fields.Text(string='工作目标(结果)与关键事件(过程)')
    evaluate = fields.Text(string='主管评价')


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


class dtdream_hr_pbc_start(models.TransientModel):
    _name = "dtdream.hr.pbc.start"

    @api.one
    def start_hr_pbc(self):
        context = dict(self._context or {})
        pbc = context.get('active_ids', []) or []
        performance = self.env['dtdream.hr.performance'].browse(pbc)
        for per in performance:
            if per.state == '0':
                per.signal_workflow('btn_start')
        return {'type': 'ir.actions.act_window_close'}

    @api.one
    def start_hr_pbc_evaluate(self):
        context = dict(self._context or {})
        pbc = context.get('active_ids', []) or []
        performance = self.env['dtdream.hr.performance'].browse(pbc)
        for per in performance:
            if per.state == '3':
                per.signal_workflow('btn_start2')
        return {'type': 'ir.actions.act_window_close'}


