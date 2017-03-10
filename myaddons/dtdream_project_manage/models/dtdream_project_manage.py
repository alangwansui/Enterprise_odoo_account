# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.exceptions import ValidationError
from lxml import etree


class dtdream_project_manage(models.Model):
    _name = 'dtdream.project.manage'

    def compute_is_create(self):
        for rec in self:
            if rec.env.user == rec.create_uid:
                rec.is_create = True
            else:
                rec.is_create = False

    def compute_role_manage(self):
        for rec in self.role:
            if rec.name == u'PMO主管' and rec.leader.user_id == self.env.user:
                self.is_PMOO = True

    def compute_is_manage(self):
        for rec in self:
            if rec.env.user == rec.project_manage.user_id:
                rec.is_project_manage = True
            else:
                rec.is_project_manage = False

    def compute_is_current(self):
        if self.env.user in [rec.user_id for rec in self.current_approve]:
            self.is_current = True
        else:
            self.is_current = False

    @api.multi
    def btn_submit_click(self):
        if not len(self.order) and self.state_y == '0':
            raise ValidationError('订单信息为必填，请添加后提交!')
        if self.state_y == '0':
            action = {
                        'name': '确认PMO主管',
                        'type': 'ir.actions.act_window',
                        'view_type': 'form',
                        'view_mode': 'form',
                        'res_model': 'dtdream.pmoo.wizard',
                        'context': self._context,
                        'target': 'new'
                        }
            return action
        else:
            self.signal_workflow('btn_submit')

    @api.multi
    def multi_manage_approve(self):
        approve_list = []
        for rec in self.role:
            if rec.leader.user_id == self.env.user:
                rec.approved = True
                continue
            if not rec.approved:
                approve_list.append(rec.leader.id)
        self.write({'current_approve': [(6, 0, approve_list)]})
        if not self.current_approve:
            self.signal_workflow('approve_pass')

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        params = self._context.get('params', None)
        action = params.get("action", 0) if params else 0
        my_action = self.env["ir.actions.act_window"].search([('id', '=', action)])
        res = super(dtdream_project_manage, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=False)
        doc = etree.XML(res['arch'])
        if my_action.name != u"与我相关":
            if res['type'] == "form":
                doc.xpath("//form")[0].set("create", "false")
            if res['type'] == "tree":
                doc.xpath("//tree")[0].set("create", "false")
            if res['type'] == "kanban":
                doc.xpath("//kanban")[0].set("create", "false")
        res['arch'] = etree.tostring(doc)
        return res

    @api.multi
    def import_order_records(self):
        action = {'type': 'ir.actions.act_window',
                  'res_model': 'dtimport.project.manage',
                  'name': "导入",
                  'view_mode': 'form',
                  'view_type': 'form',
                  'views': [[False, 'form']],
                  'target': 'new'}
        return action

    @api.model
    def default_get(self, fields):
        rec = super(dtdream_project_manage, self).default_get(fields)
        stages = self.env['dtdream.project.stage.setting'].search([], order='order asc')
        roles = self.env['dtdream.project.role.setting'].search([])
        rec.update({'stage': [(6, 0, [])] + [(0, 0, {'name': stage.name}) for stage in stages],
                    'role': [(6, 0, [])] + [(0, 0, {'name': role.name, 'required': role.required,'state': '', 'approved': True if 'PMO' in role.name else False}) for role in roles]})
        return rec

    code = fields.Char(string='项目编码', size=16)
    name = fields.Char(string='项目名称', size=16)
    customer = fields.Char(string='客户名称', size=16)
    pay_way = fields.Char(string='付款方式', size=8)
    customer_manage = fields.Char(string='客户经理', size=8)
    product_manage = fields.Many2one('hr.employee', string='产品经理')
    office = fields.Char(string='办事处', size=8)
    sys_department = fields.Char(string='系统部', size=8)
    project_manage = fields.Many2one('hr.employee', string='项目经理')
    project_leval = fields.Selection([('SS', '重大级'), ('S', '公司级'), ('V', '部门级')], string='项目等级')
    contract = fields.Selection([('0', '未签'), ('1', '已签')], string='合同签订')
    yunwei = fields.Selection([('0', '否'), ('1', '是')], string='是否需要转运维')
    order = fields.One2many('dtdream.project.order', 'project_manage_id', string='订单信息')
    stage = fields.One2many('dtdream.project.stage', 'project_manage_id', string='项目阶段')
    role = fields.One2many('dtdream.project.role', 'project_manage_id', string='负责人')
    plan = fields.One2many('dtdream.project.plan.detail', 'project_manage_id', string='项目规划')
    is_PMOO = fields.Boolean(string='是否PMO主管', compute=compute_role_manage)
    is_create = fields.Boolean(string='是否创建者', compute=compute_is_create)
    is_project_manage = fields.Boolean(string='是否项目经理', compute=compute_is_manage)
    current_approve = fields.Many2many('hr.employee', string='当前审批人')
    is_current = fields.Boolean(string='是否当前审批人', compute=compute_is_current)
    state_y = fields.Selection([('0', '草稿'),
                               ('10', '指派项目经理'),
                               ('11', '同步项目订单信息'),
                               ('12', '交付服务经理审批'),
                               ('1', '立项'),
                               ('20', '发起策划'),
                               ('21', 'PMO审核策划'),
                               ('2', '策划'),
                               ('3', '交付'),
                               ('4', '运维'),
                               ('99', '结项')], string='项目状态', default='0')
    state_n = fields.Selection([('0', '草稿'),
                               ('10', '指派项目经理'),
                               ('11', '同步项目订单信息'),
                               ('12', '交付服务经理审批'),
                               ('1', '立项'),
                               ('20', '发起策划'),
                               ('21', 'PMO审核策划'),
                               ('2', '策划'),
                               ('3', '交付'),
                               ('99', '结项')], string='项目状态', default='0')

    _sql_constraints = [
        ('project_code_uniquee', 'UNIQUE(code)', "项目编码已存在!"),
    ]

    def wkf_PMO(self):
        for rec in self.role:
            if rec.name == u'PMO主管':
                pmo = rec.leader.id
        self.write({'state_y': '10', 'state_n': '10', 'current_approve': [(6, 0, [pmo])]})

    def wkf_sync(self):
        self.write({'state_y': '11', 'state_n': '11', 'current_approve': [(6, 0, [self.project_manage.id])]})

    def wkf_manage_approve(self):
        self.write({'state_y': '12', 'state_n': '12', 'current_approve': [(6, 0, [rec.leader.id for rec in self.role if not rec.approved])]})

    def wkf_create_project(self):
        self.write({'state_y': '1', 'state_n': '1', 'current_approve': [(6, 0, [self.project_manage.id])]})

    def wkf_plan(self):
        pass

    def wkf_plan_approve(self):
        pass

    def wkf_plan_done(self):
        pass



