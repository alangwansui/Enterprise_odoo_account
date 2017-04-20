# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.exceptions import AccessError


class dtdream_project_deliver_config(models.Model):
    _name = "dtdream.project.deliver.config"
    _order = 'order'

    name = fields.Char(string='交付大类', size=16)
    order = fields.Integer(string='序号')

    _sql_constraints = [
        ('deliver_name', 'UNIQUE(name)', "该交付类别已存在!"),
    ]


class dtdream_project_output_deliver(models.Model):
    _name = "dtdream.project.output.deliver"

    name = fields.Many2one('dtdream.project.deliver.config', string='交付类别')
    project_type = fields.Many2one('dtdream.project.type', string='项目类别')
    deliver_manage = fields.One2many('dtdream.project.output.deliver.manage', 'project_deliver_id')

    _sql_constraints = [
        ('project_name_type_unique', 'UNIQUE(name,project_type)', "交付类别已存在!"),
    ]


class dtdream_project_output_deliver_manage(models.Model):
    _name = "dtdream.project.output.deliver.manage"
    _order = 'name'

    @api.model
    def create(self, vals):
        project_id = vals.get('project_manage_id', '')
        if project_id:
            cr = self.env['dtdream.project.manage'].search([('id', '=', project_id)])
            if cr and (cr.state_y != '20'or (not cr.is_deliver_manage and not vals.get('created', False))) and not cr.is_manage:
                raise AccessError('交付输出物只有在策划阶段且是交付经理才可新增项。')
            if vals:
                vals.update({'created': True})
        return super(dtdream_project_output_deliver_manage, self).create(vals)

    @api.depends('is_header')
    def compute_project_state(self):
        for rec in self:
            rec.state_y = rec.project_manage_id.state_y

    @api.depends('is_header')
    def compute_is_deliver_manage(self):
        for rec in self:
            rec.is_deliver_manage = rec.project_manage_id.is_deliver_manage

    def compute_is_admin(self):
        for rec in self:
            rec.is_manage = rec.project_manage_id.is_manage

    def compute_is_header(self):
        for rec in self:
            if rec.env.user == rec.header.user_id:
                rec.is_header = True
            else:
                rec.is_header = False

    def compute_is_assess_man(self):
        for rec in self:
            if (rec.env.user == rec.assess_man.user_id and rec.state_y == '3') or \
                    (rec.env.user == rec.assess_man_deliver.user_id and rec.state_y == '30'):
                rec.is_assess_man = True
            else:
                rec.is_assess_man = False

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.can_delete and not rec.is_manage:
                raise AccessError('此项为必须项不可删除!')
            if rec.state_y != '20' and not rec.is_manage:
                raise AccessError('无法删除此项!')
        return super(dtdream_project_output_deliver_manage, self).unlink()

    def get_approve_id(self):
        header = []
        for deliver in self.search([('project_manage_id', '=', self.project_manage_id.id), ('state', 'in', ('0', '3'))]):
            if deliver.header.id not in header:
                header.append(deliver.header.id)
        if self.project_manage_id.state_y == '30':
            for deliver_approve in self.project_manage_id.output_deliver:
                if deliver_approve.assess_man_deliver.id not in header:
                    header.append(self.assess_man_deliver.id)
        else:
            for deliver_approve in self.search([('project_manage_id', '=', self.project_manage_id.id), ('state', '=', '1')]):
                if deliver_approve.assess_man.id not in header:
                    header.append(deliver_approve.assess_man.id)

        for output in self.env['dtdream.project.output.plan.manage'].search([(
                'project_manage_id', '=', self.project_manage_id.id), ('state', 'in', ('0', '3'))]):
            if output.header.id not in header:
                header.append(output.header.id)
        for output_approve in self.env['dtdream.project.output.plan.manage'].search([(
                'project_manage_id', '=', self.project_manage_id.id), ('state', '=', '1')]):
            if output_approve.assess_man.id not in header:
                header.append(output_approve.assess_man.id)
        return header

    def update_current_approve(self):
        approve = self.get_approve_id()
        self.project_manage_id.current_approve = [(6, 0, approve)]

    @api.multi
    def btn_deliver_submit(self):
        if not self.assess_man or not self.url:
            raise AccessError('请指定审核人提交相关输出物之后在发起审核!')
        self.write({'submit_time': fields.date.today(), 'state': '1'})
        self.project_manage_id.send_mail(subject=u'请您审核%s' % (self.deliver or self.name.name), content=u'''%s发起了%s的审核，
        请您审核。''' % (self.header.name, self.deliver or self.name.name), name=[
            self.assess_man, self.assess_man_deliver][self.state_y == '30'])
        self.update_current_approve()

    def create_approve_log(self, result=u''):
        name = self.env.user.employee_ids
        self.env['dtdream.project.approve.record'].create({'output': self.deliver, 'result': result,
                                                           'approve': '.'.join([name.name, name.full_name, name.job_number]),
                                                           'approve_time': fields.Datetime.now(),
                                                           'project_manage_id': self.project_manage_id.id,
                                                           'output_deliver_id': self.id})

    @api.multi
    def btn_deliver_approve(self):
        if self.project_manage_id.state_y == '30':
            self.write({'assess_time': fields.date.today(), 'state': '2', 'assess_times': self.assess_times + 1,
                        'deliver_approve': True})
        else:
            self.write({'assess_time': fields.date.today(), 'state': '2', 'assess_times': self.assess_times + 1})
        self.create_approve_log(result=u'同意')
        self.update_current_approve()
        if not self.project_manage_id.current_approve:
            self.project_manage_id.current_approve = [(6, 0, [self.project_manage_id.project_manage.id])]
            self.project_manage_id.send_mail(subject=u'项目交付已经完成,请将项目进入下一阶段', content=u'''项目(%s)交付已经完成，
            请将项目进入下一阶段。''' % self.project_manage_id.name, name=self.project_manage_id.project_manage)

    @api.multi
    def btn_deliver_reject(self):
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
                  'domain': [('output_deliver_id', '=', self.id), ('project_manage_id', '=', self.project_manage_id.id)]}
        return action

    name = fields.Many2one('dtdream.project.deliver.config', string='交付大类')
    deliver = fields.Char(string='交付资料', size=20)
    plan_time = fields.Date(string='计划完成时间')
    header = fields.Many2one('hr.employee', string='责任人')
    submit_time = fields.Date(string='提交审核时间')
    assess_time = fields.Date(string='审核时间')
    state = fields.Selection([('0', '未审核'), ('1', '审核中'), ('2', '审核通过'), ('3', '审核不通过')], string='审核状态', default='0')
    assess_times = fields.Integer(string='评审次数')
    assess_man = fields.Many2one('hr.employee', string='审核人(交付)')
    assess_man_deliver = fields.Many2one('hr.employee', string='审核人(运维)')
    deliver_approve = fields.Boolean(string='运维管控是否同意')
    url = fields.Char(string='相关链接', size=50)
    project_deliver_id = fields.Many2one('dtdream.project.output.deliver', '交付输出物规划')
    project_manage_id = fields.Many2one('dtdream.project.manage', string='项目')
    can_delete = fields.Boolean(string='是否必须')
    created = fields.Boolean(string='是否已创建')
    is_header = fields.Boolean(string='是否责任人', compute=compute_is_header)
    is_assess_man = fields.Boolean(string='是否审核人', compute=compute_is_assess_man)
    is_deliver_manage = fields.Boolean(string='是否交付经理', compute=compute_is_deliver_manage)
    is_manage = fields.Boolean(string='是否管理员', compute=compute_is_admin)
    state_y = fields.Selection([('0', '草稿'),
                               ('10', '指派项目经理'),
                               ('11', '同步项目订单信息'),
                               ('12', '交付服务经理确认'),
                               ('1', '立项'),
                               ('20', '发起策划'),
                               ('21', 'PMO审核策划'),
                               ('2', '策划'),
                               ('3', '交付'),
                               ('30', '运维管控测试'),
                               ('31', '交付运维测试'),
                               ('32', '运维服务经理审核'),
                               ('33', '指定VIP经理'),
                               ('34', 'VIP经理确认'),
                               ('4', '运维'),
                               ('99', '结项')], string='项目状态', compute=compute_project_state)