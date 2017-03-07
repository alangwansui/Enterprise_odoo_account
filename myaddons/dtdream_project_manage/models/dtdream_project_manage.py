# -*- coding: utf-8 -*-

from openerp import models, fields, api
from lxml import etree


class dtdream_project_manage(models.Model):
    _name = 'dtdream.project.manage'

    @api.onchange('yunwei')
    def _onchange_compute_hr_pbc(self):
        if self.yunwei == '1':
            records = self.env["dtdream.project.role.setting"].search([])
            roles = [(0, 0, {'name': rec.name, 'required': rec.required, 'state': ''}) for rec in records]
            self.role = [(6, 0, [])]
            self.role = roles
        else:
            roles = [(0, 0, {'name': rec.name, 'required': rec.required, 'state': ''}) for rec in self.role if rec.name != u'运维服务经理']
            self.role = [(6, 0, [])]
            self.role = roles

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        params = self._context.get('params', None)
        action = params.get("action", 0) if params else 0
        my_action = self.env["ir.actions.act_window"].search([('id', '=', action)])
        res = super(dtdream_project_manage, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=False)
        doc = etree.XML(res['arch'])
        if my_action.name != u"我的申请":
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
                    'role': [(6, 0, [])] + [(0, 0, {'name': role.name, 'required': role.required,'state': ''}) for role in roles]})
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
    state_y = fields.Selection([('0', '草稿'),
                               ('10', 'PMO主管'),
                               ('11', '项目经理'),
                               ('12', '交付服务经理'),
                               ('13', '发布章程'),
                               ('1', '已立项'),
                               ('20', '发起策划'),
                               ('21', 'PMO审核策划'),
                               ('2', '已策划'),
                               ('3', '已交付'),
                               ('4', '已运维'),
                               ('99', '结项')], string='项目状态', default='0')
    state_n = fields.Selection([('0', '草稿'),
                               ('10', 'PMO主管'),
                               ('11', '项目经理'),
                               ('12', '交付服务经理'),
                               ('13', '发布章程'),
                               ('1', '已立项'),
                               ('20', '发起策划'),
                               ('21', 'PMO审核策划'),
                               ('2', '已策划'),
                               ('3', '已交付'),
                               ('99', '结项')], string='项目状态', default='0')

    _sql_constraints = [
        ('project_code_uniquee', 'UNIQUE(code)', "项目编码已存在!"),
    ]








