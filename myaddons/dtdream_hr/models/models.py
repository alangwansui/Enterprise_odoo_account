# -*- coding: utf-8 -*-

from openerp import models, fields, api


class dtdream_hr(models.Model):
    _inherit = 'hr.department'

    code = fields.Char("部门编码")
    assitant_id = fields.Many2many("hr.employee",string="行政助理")

    def search_read(self, cr, uid, domain=None, fields=None, offset=0, limit=None, order=None, context=None):
        if 'child_ids' not in fields:
            domain = [ex for ex in domain if ex != ['parent_id', '=', False]]
        return super(dtdream_hr, self).search_read(cr, uid, domain=domain)


class dtdream_hr_employee(models.Model):
    _inherit = 'hr.employee'

    # 显示花名和工号
    @api.multi
    def name_get(self):
        res = super(dtdream_hr_employee, self).name_get()
        data = []
        for employee in self:
            display_value = ''
            display_value += employee.name or ""
            display_value += '.' + employee.full_name + ' '
            display_value += employee.job_number or ""
            data.append((employee.id, display_value))
        return data

    # 可以根据姓名、花名、工号搜索
    def name_search(self, cr, user, name='', args=None, operator='ilike', context=None, limit=100):
        ids = self.search(cr, user, ['|','|',('name', 'ilike', name),('full_name', 'ilike', name),('job_number', 'ilike', name)] + args, limit=limit)
        return super(dtdream_hr_employee, self).name_search(
            cr, user, '', args=[('id', 'in', list(ids))],
            operator='ilike', context=context, limit=limit)
    @api.depends("name")
    def _compute_nick_name(self):
        for rec in self:
            rec.nick_name= rec.name

    nick_name = fields.Char("花名",compute=_compute_nick_name,store=True)
    full_name = fields.Char(string="姓名", required=True)
    gender = fields.Selection([('male', '男'), ('female', '女')], '性别',required=True)
    job_number = fields.Char("工号", required=True)
    work_email = fields.Char('工作Email', size=240,required=True)
    department_id = fields.Many2one('hr.department', '部门')
    mobile_phone = fields.Char('手机号', readonly=False, required=True)
    home_address = fields.Char("居住地址")
    education = fields.Selection([
        ('education_01', '中专'),
        ('education_02','大专'),
        ('education_03','本科'),
        ('education_04', '硕士'),
        ('education_05', '博士'),
        ('education_06', '其他'),
        ], string='最高学历')

    duties = fields.Char("职务")
    post = fields.Char("岗位")
    Inaugural_state = fields.Selection([('Inaugural_state_01','在职'),('Inaugural_state_02','离职')],"就职状态", required=True)
    entry_day=fields.Date("入职日期")
    user_id = fields.Many2one('res.users','相关用户')

    _sql_constraints = [
        ('employee_nick_name_unique', 'UNIQUE(nick_name)', "花名不能重复！"),
        ('employee_job_number_unique', 'UNIQUE(job_number)', "工号不能重复！"),
        ('employee_work_email_unique', 'UNIQUE(work_email)', "工作Email不能重复！"),
        ('employee_mobile_phone_unique', 'UNIQUE(mobile_phone)', "手机号不能重复！"),
    ]

