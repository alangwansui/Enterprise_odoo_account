# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.exceptions import ValidationError, AccessError
from lxml import etree


class dtdream_project_manage(models.Model):
    _name = 'dtdream.project.manage'
    _inherit = ['mail.thread']
    _description = u'项目管理'

    def compute_is_create(self):
        for rec in self:
            if rec.env.user == rec.create_uid:
                rec.is_create = True
            else:
                rec.is_create = False

    def compute_role_manage(self):
        for rec in self.role:
            if rec.name == self.env.ref('dtdream_project_manage.dtdream_project_role_PMOO').name and \
                            rec.leader.user_id == self.env.user:
                self.is_PMOO = True

    def compute_is_admin(self):
        if self.env.ref('dtdream_project_manage.group_project_mange_admin') in self.env.user.groups_id:
            self.is_manage = True
        else:
            self.is_manage = False

    def compute_is_manage(self):
        for rec in self:
            if rec.env.user == rec.project_manage.user_id:
                rec.is_project_manage = True
            else:
                rec.is_project_manage = False

    def compute_is_deliver_manage(self):
        for rec in self.role:
            if rec.name == self.env.ref('dtdream_project_manage.dtdream_project_role_PT').name and \
                            rec.leader.user_id == self.env.user:
                self.is_deliver_manage = True

    def compute_is_current(self):
        if self.env.user in [rec.user_id for rec in self.current_approve]:
            self.is_current = True
        else:
            self.is_current = False

    def update_project_stage_plan_time(self):
        for rec in self.stage:
            record = self.env['dtdream.project.plan.detail'].search([('project_manage_id', '=', self.id),
                                                                     ('name.name', '=', rec.name)])
            if record:
                start_time = [cr.start_time for cr in record]
                end_time = [cr.end_time for cr in record]
                rec.write({'plan_start_time': min(start_time), 'plan_end_time': max(end_time)})

    def check_need_fields(self):
        if self.is_project_manage:
            for plan in self.plan:
                if not plan.start_time or not plan.end_time or not plan.header:
                    raise ValidationError('项目规划中(开始时间,结束时间,责任人)为必填，请填写后提交。')
            for output in self.output_plan:
                if not output.plan_time or not output.header:
                    raise ValidationError('输出物规划中(计划完成时间,责任人)为必填，请填写后提交。')
        else:
            for deliver in self.output_deliver:
                if not deliver.plan_time or not deliver.header:
                    raise ValidationError('交付输出物规划中(计划完成时间,责任人)为必填，请填写后提交。')

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
        elif self.state_y == '20':
            approve = []
            self.check_need_fields()
            if self.is_project_manage:
                self.update_project_stage_plan_time()
                approve = [rec.leader.id for rec in self.role if rec.name == self.env.ref(
                    'dtdream_project_manage.dtdream_project_role_PT').name]
            self.write({'current_approve': [(6, 0, approve)]})
            if not self.current_approve:
                self.signal_workflow('btn_submit')
            else:
                self.record_action_message(state=u'发起策划', action=u'提交', approve=','.join(
                    [rec.name for rec in self.current_approve]))
        else:
            self.signal_workflow('btn_submit')

    @api.multi
    def btn_reject_click(self):
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

    def update_current_approve(self):
        current_approve = [rec.leader.id for rec in self.role if not rec.approved and 'PMO' not in rec.name.upper()]
        if any([True for rec in self.role if rec.approved and rec.result]) and \
                        self.project_manage.id not in current_approve:
            current_approve.append(self.project_manage.id)
        elif self.project_manage.id in current_approve:
            current_approve.remove(self.project_manage.id)
        self.write({'current_approve': [(6, 0, current_approve)]})

    def get_approve_list(self, result=False, suggestion=u''):
        approve_list = []
        for rec in self.role:
            if rec.leader.user_id == self.env.user:
                rec.approved = True
                rec.result = result
                rec.suggestion = suggestion
                continue
            if not rec.approved and 'PMO' not in rec.name.upper():
                approve_list.append(rec.leader.id)
        if any([rec.result for rec in self.role]):
            approve_list = [self.project_manage.id]
        return approve_list

    @api.multi
    def multi_manage_approve(self):
        approve_list = self.get_approve_list(suggestion=u'同意')
        self.write({'current_approve': [(6, 0, approve_list)]})
        if not self.current_approve:
            self.signal_workflow('approve_pass')
            self.env['dtdream.project.initial.plan'].create({'project_manage_id': self.id})
        self.record_action_message(state=u'交付服务经理确认', action=u'同意', approve=','.join(
                        [rec.name for rec in self.current_approve]))

    @api.multi
    def multi_manage_reject(self):
        action = {
                    'name': '不同意',
                    'type': 'ir.actions.act_window',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'dtdream.pmo.approve.wizard',
                    'context': self._context,
                    'target': 'new'
                    }
        return action

    def get_project_plan_setting(self):
        """读取项目规划配置并创建项目规划记录并关联项目"""
        plans = []
        for cr in self.env['dtdream.project.plan.config'].search([('project_type', '=', self.project_type.id)]):
            if cr.plan:
                for crr in cr.plan:
                    plans.append({'name': cr.name.id, 'work_item': crr.work_item, 'leader': crr.leader, 'work_details':
                        crr.work_details, 'can_delete': crr.can_delete, 'created': True})
            else:
                plans.append({'name': cr.name.id, 'created': True})
        for rec in self.plan:
            rec.write({'can_delete': False})
        self.plan = plans

    def get_output_plan_setting(self):
        """读取输出物规划配置并创建输出物规划记录并关联项目"""
        output = []
        for cr in self.env['dtdream.project.output.plan'].search([('project_type', '=', self.project_type.id)]):
            if cr.plan_manage:
                for crr in cr.plan_manage:
                    output.append({'name': cr.name.id, 'output': crr.output, 'can_delete': crr.can_delete,
                                   'created': True, 'state': '0'})
            else:
                output.append({'name': cr.name.id, 'created': True, 'state': '0'})
        for rec in self.output_plan:
            rec.write({'can_delete': False})
        self.output_plan = output

    def get_output_deliver_setting(self):
        """读取交付输出物规划配置并创建交付输出物规划记录并关联项目"""
        deliver = []
        for cr in self.env['dtdream.project.output.deliver'].search([('project_type', '=', self.project_type.id)]):
            if cr.deliver_manage:
                for crr in cr.deliver_manage:
                    deliver.append({'name': cr.name.id, 'deliver': crr.deliver, 'can_delete': crr.can_delete,
                                    'created': True, 'state': '0'})
            else:
                deliver.append({'name': cr.name.id, 'created': True, 'state': '0'})
        for rec in self.output_deliver:
            rec.write({'can_delete': False})
        self.output_deliver = deliver

    @api.onchange('project_type')
    def get_output_deliver_settings(self):
        self.get_project_plan_setting()
        self.get_output_plan_setting()
        self.get_output_deliver_setting()

    def get_output_approve_states(self):
        states = []
        for output in self.output_plan:
            if output.state not in states:
                states.append(output.state)
        for deliver in self.output_deliver:
            if deliver.state not in states:
                states.append(deliver.state)
        return states

    @api.multi
    def step_to_next_stage(self):
        if self.state_y == '3':
            states = self.get_output_approve_states()
            if states != ['2']:
                raise AccessError('存在未审核通过输出物,无法进入下一阶段!')
        self.signal_workflow('next_stage')

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
    def check_yunwei(self):
        return (True, False)[self.yunwei == '0']

    @api.multi
    def btn_import_order(self):
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
                    'role': [(6, 0, [])] + [(0, 0, {'name': role.name, 'required': role.required,'state': ''}) for role in roles]})
        return rec

    @api.multi
    def record_action_message(self, state, action, approve=''):
        self.message_post(body=u"""<table border="1" style="border-collapse: collapse;table-layout: fixed">
                                               <tr><td style="padding:10px">状态</td><td style="padding:10px">%s</td></tr>
                                               <tr><td style="padding:10px">操作</td><td style="padding:10px">%s</td></tr>
                                               <tr><td style="padding:10px;">当前处理人</td><td style="padding:10px;
                                               white-space:nowrap;text-overflow:ellipsis;-o-text-overflow:ellipsis;
                                               -moz-text-overflow: ellipsis;-webkit-text-overflow: ellipsis;
                                               overflow:hidden;">%s</td></tr>
                                               </table>""" % (state, action, approve))

    code = fields.Char(string='项目编码', size=16)
    name = fields.Char(string='项目名称(服务)', size=32)
    name_contract = fields.Char(string='项目名称(合同)', size=32)
    customer = fields.Char(string='客户名称', size=16)
    pay_way = fields.Char(string='付款方式', size=8)
    customer_manage = fields.Many2one('hr.employee', string='客户经理')
    product_manage = fields.Many2one('hr.employee', string='产品经理')
    office = fields.Char(string='办事处', size=8)
    sys_department = fields.Char(string='系统部', size=8)
    project_manage = fields.Many2one('hr.employee', string='项目经理')
    project_leval = fields.Many2one('dtdream.project.level', string='项目等级')
    contract = fields.Selection([('0', '未签'), ('1', '已签')], string='合同签订')
    yunwei = fields.Selection([('0', '否'), ('1', '是')], string='是否需要转运维')
    project_des = fields.Text(string='项目描述')
    project_range = fields.Text(string='项目范围')
    evaluate = fields.Text(string='评价标准')
    condition = fields.Text(string='项目假定与约束条件')
    project_type = fields.Many2one('dtdream.project.type', string='项目类型')
    initial_plan = fields.One2many('dtdream.project.initial.plan', 'project_manage_id', string='初始计划')
    project_struction = fields.One2many('dtdream.project.construction', 'project_manage_id', string='项目组织结构')
    order = fields.One2many('dtdream.project.order', 'project_manage_id', string='订单信息')
    stage = fields.One2many('dtdream.project.stage', 'project_manage_id', string='项目阶段')
    role = fields.One2many('dtdream.project.role', 'project_manage_id', string='负责人')
    plan = fields.One2many('dtdream.project.plan.detail', 'project_manage_id', string='项目规划')
    output_plan = fields.One2many('dtdream.project.output.plan.manage', 'project_manage_id', string='输出物规划')
    output_deliver = fields.One2many('dtdream.project.output.deliver.manage', 'project_manage_id', string='交付输出物规划')
    is_PMOO = fields.Boolean(string='是否PMO主管', compute=compute_role_manage)
    is_manage = fields.Boolean(string='是否管理员', compute=compute_is_admin)
    is_create = fields.Boolean(string='是否创建者', compute=compute_is_create)
    is_project_manage = fields.Boolean(string='是否项目经理', compute=compute_is_manage)
    is_deliver_manage = fields.Boolean(string='是否交付经理', compute=compute_is_deliver_manage)
    current_approve = fields.Many2many('hr.employee', string='当前审批人')
    is_current = fields.Boolean(string='是否当前审批人', compute=compute_is_current)
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
                               ('99', '结项')], string='项目状态', default='0')
    state_n = fields.Selection([('0', '草稿'),
                               ('10', '指派项目经理'),
                               ('11', '同步项目订单信息'),
                               ('12', '交付服务经理确认'),
                               ('1', '立项'),
                               ('20', '发起策划'),
                               ('21', 'PMO审核策划'),
                               ('2', '策划'),
                               ('3', '交付'),
                               ('99', '结项')], string='项目状态', default='0')

    _sql_constraints = [
        ('project_name_uniquee', 'UNIQUE(name)', "项目名称(服务)已存在!"),
    ]

    def wkf_PMO(self):
        for rec in self.role:
            if rec.name == self.env.ref('dtdream_project_manage.dtdream_project_role_PMOO').name:
                pmo = rec.leader.id
                leader = rec.leader
        self.write({'state_y': '10', 'state_n': '10', 'current_approve': [(6, 0, [pmo])]})
        self.record_action_message(state=u'草稿-->指派项目经理', action=u'提交', approve=leader.name)

    def wkf_sync(self):
        self.write({'state_y': '11', 'state_n': '11', 'current_approve': [(6, 0, [self.project_manage.id])]})
        self.record_action_message(state=u'指派项目经理-->同步项目订单信息', action=u'提交', approve=self.project_manage.name)

    def wkf_manage_approve(self):
        approve = []
        for rec in self.role:
            if not rec.leader:
                raise AccessError("存在项目相关负责人未填写,请先指定相关负责人")
            if rec.leader.id and 'PMO' not in rec.name.upper():
                approve.append(rec.leader.id)
        self.write({'state_y': '12', 'state_n': '12', 'current_approve': [(6, 0, approve)]})
        self.record_action_message(state=u'同步项目订单信息-->交付服务经理确认', action=u'同步项目信息',
                                   approve=','.join([rec.name for rec in self.current_approve]))

    def wkf_create_project(self):
        self.write({'state_y': '1', 'state_n': '1', 'current_approve': [(6, 0, [self.project_manage.id])]})
        self.record_action_message(state=u'交付服务经理确认-->立项', action=u'确认', approve=self.project_manage.name)

    def wkf_plan(self):
        approve = [self.project_manage.id]
        if self.state_y == '21':
            self.write({'state_y': '20', 'state_n': '20', 'current_approve': [(6, 0, approve)]})
            self.record_action_message(state=u'PMO审核策划-->发起策划', action=u'驳回',
                                       approve=','.join([rec.name for rec in self.current_approve]))
        else:
            self.write({'state_y': '20', 'state_n': '20', 'current_approve': [(6, 0, approve)]})
            self.record_action_message(state=u'立项-->发起策划', action=u'进入下一阶段',
                                       approve=','.join([rec.name for rec in self.current_approve]))

    def wkf_plan_approve(self):
        self.write({'state_y': '21', 'state_n': '21', 'current_approve': [
            (6, 0, [rec.leader.id for rec in self.role if rec.name == self.env.ref('dtdream_project_manage.dtdream_project_role_PMO').name])]})
        self.record_action_message(state=u'发起策划-->PMO审核策划', action=u'提交',
                                   approve=','.join([rec.name for rec in self.current_approve]))

    def wkf_plan_done(self):
        self.write({'state_y': '2', 'state_n': '2', 'current_approve': [(6, 0, [self.project_manage.id])]})
        self.record_action_message(state=u'PMO审核策划-->策划', action=u'同意', approve=self.project_manage.name)

    def get_deliver_stage_approve(self):
        approve = []
        for rec in self.output_plan:
            if rec.header.id not in approve:
                approve.append(rec.header.id)
        for rec in self.output_deliver:
            if rec.header.id not in approve:
                approve.append(rec.header.id)
        return approve

    def wkf_deliver(self):
        approve = self.get_deliver_stage_approve()
        self.write({'state_y': '3', 'state_n': '3', 'current_approve': [(6, 0, approve)]})
        self.record_action_message(state=u'策划-->交付', action=u'进入下一阶段',
                                   approve=','.join([rec.name for rec in self.current_approve]))

    def wkf_yunwei(self):
        self.write({'state_y': '4'})

    def wkf_project_done(self):
        if self.state_y == '3':
            self.record_action_message(state=u'交付-->结项', action=u'进入下一阶段', approve='')
        else:
            self.record_action_message(state=u'运维-->结项', action=u'进入下一阶段', approve='')
        self.write({'state_y': '99', 'state_n': '99', 'current_approve': [(6, 0, [])]})




