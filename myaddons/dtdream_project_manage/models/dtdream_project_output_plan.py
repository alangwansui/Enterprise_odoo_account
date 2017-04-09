# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.exceptions import AccessError


class dtdream_project_output_plan(models.Model):
    _name = "dtdream.project.output.plan"

    name = fields.Many2one('dtdream.project.stage.setting', string='项目阶段')
    project_type = fields.Many2one('dtdream.project.type', string='项目类型')
    plan_manage = fields.One2many('dtdream.project.output.plan.manage', 'project_output_id')

    _sql_constraints = [
        ('project_name', 'UNIQUE(name)', "项目阶段已存在!"),
    ]


class dtdream_project_output_plan_manage(models.Model):
    _name = "dtdream.project.output.plan.manage"
    _order = 'name'

    @api.model
    def create(self, vals):
        cr = self.env['dtdream.project.manage'].search([('id', '=', vals.get('project_manage_id', ''))])
        if cr and cr.state_y != '20':
            raise AccessError('输出物规划只有在策划阶段且是项目经理才可新增项。')
        if vals:
            vals.update({'created': True})
        return super(dtdream_project_output_plan_manage, self).create(vals)

    @api.depends('is_header')
    def compute_project_state(self):
        for rec in self:
            rec.state_y = rec.project_manage_id.state_y

    def compute_is_manage(self):
        for rec in self:
            rec.is_project_manage = rec.project_manage_id.is_project_manage

    def compute_is_header(self):
        for rec in self:
            if rec.env.user == rec.header.user_id:
                rec.is_header = True
            else:
                rec.is_header = False

    def compute_is_assess_man(self):
        for rec in self:
            if rec.env.user == rec.assess_man.user_id:
                rec.is_assess_man = True
            else:
                rec.is_assess_man = False

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.can_delete:
                raise AccessError('此项为必须项不可删除!')
            if rec.state_y != '20':
                raise AccessError('无法删除此项!')
        return super(dtdream_project_output_plan_manage, self).unlink()

    def get_approve_id(self):
        header = []
        for output in self.search([('project_manage_id', '=', self.project_manage_id.id), ('state', 'in', ('0', '3'))]):
            if output.header.id not in header:
                header.append(output.header.id)
        for output_approve in self.search([('project_manage_id', '=', self.project_manage_id.id), ('state', '=', '1')]):
            if output_approve.assess_man.id not in header:
                header.append(output_approve.assess_man.id)

        for deliver in self.env['dtdream.project.output.deliver.manage'].search([(
                'project_manage_id', '=', self.project_manage_id.id), ('state', 'in', ('0', '3'))]):
            if deliver.header.id not in header:
                header.append(deliver.header.id)
        for deliver_approve in self.env['dtdream.project.output.deliver.manage'].search([(
                'project_manage_id', '=', self.project_manage_id.id), ('state', '=', '1')]):
            if deliver_approve.assess_man.id not in header:
                header.append(deliver_approve.assess_man.id)
        return header

    def update_current_approve(self):
        approve = self.get_approve_id()
        self.project_manage_id.current_approve = [(6, 0, approve)]

    @api.multi
    def btn_output_submit(self):
        if not self.assess_man or not self.url:
            raise AccessError('请指定审核人提交相关输出物之后在发起审核!')
        self.write({'submit_time': fields.date.today(), 'state': '1'})
        self.update_current_approve()

    @api.multi
    def btn_output_approve(self):
        self.write({'assess_time': fields.date.today(), 'state': '2', 'assess_times': self.assess_times + 1})
        self.update_current_approve()
        if not self.project_manage_id.current_approve:
            self.project_manage_id.current_approve = [(6, 0, [self.project_manage_id.project_manage.id])]

    @api.multi
    def btn_output_reject(self):
        action = {
                    'name': '驳回',
                    'type': 'ir.actions.act_window',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'dtdream.pmo.approve.wizard',
                    'context': self._context,
                    'target': 'new'
                    }
        return action

    @api.multi
    def btn_lookup_approve_records(self):
        action = {'type': 'ir.actions.act_window',
                  'res_model': 'dtdream.project.approve.record',
                  'name': "审批记录",
                  'view_mode': 'tree',
                  'view_type': 'form',
                  'domain': [],
                  'target': 'new'}
        return action

    name = fields.Many2one('dtdream.project.stage.setting', string='项目阶段')
    output = fields.Char(string='输出物名称', size=20)
    plan_time = fields.Date(string='计划完成时间')
    header = fields.Many2one('hr.employee', string='责任人')
    submit_time = fields.Date(string='提交审核时间')
    assess_time = fields.Date(string='审核时间')
    state = fields.Selection([('0', '未审核'), ('1', '审核中'), ('2', '审核通过'), ('3', '审核不通过')], string='审核状态', default='0')
    assess_times = fields.Integer(string='评审次数')
    assess_man = fields.Many2one('hr.employee', string='审核人')
    url = fields.Char(string='相关链接', size=50)
    project_output_id = fields.Many2one('dtdream.project.output.plan', '输出物规划')
    project_manage_id = fields.Many2one('dtdream.project.manage', string='项目')
    can_delete = fields.Boolean(string='是否必须')
    created = fields.Boolean(string='是否已创建')
    is_header = fields.Boolean(string='是否责任人', compute=compute_is_header)
    is_assess_man = fields.Boolean(string='是否审核人', compute=compute_is_assess_man)
    is_project_manage = fields.Boolean(string='是否项目经理', compute=compute_is_manage)
    state_y = fields.Selection([('0', '草稿'),
                               ('10', '指派项目经理'),
                               ('11', '同步项目订单信息'),
                               ('12', '交付服务经理确认'),
                               ('1', '立项'),
                               ('20', '发起策划'),
                               ('21', 'PMO审核策划'),
                               ('2', '策划'),
                               ('3', '交付'),
                               ('4', '运维'),
                               ('99', '结项')], string='项目状态', compute=compute_project_state)



