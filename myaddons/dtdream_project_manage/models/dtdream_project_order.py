# -*- coding: utf-8 -*-

from openerp import models, fields, api


class dtdream_project_order(models.Model):
    _name = 'dtdream.project.order'

    code = fields.Char(string='订单编号', size=16)
    order_type = fields.Char(string='订单类型', size=8)
    bom = fields.Char(string='BOM', size=8)
    version = fields.Char(string='型号', size=16)
    product_type = fields.Char(string='产品类别', size=8)
    product_des = fields.Text(string="产品描述")
    company = fields.Char(string='单位', size=16)
    vender = fields.Char(string='生产厂家', size=16)
    num = fields.Integer(string='数量')
    actual_price = fields.Float(string='实收金额')
    need_price = fields.Float(string='应收金额')
    project_manage_id = fields.Many2one('dtdream.project.manage')


class dtdream_project_order_view(models.Model):
    _name = 'dtdream.project.order.view'

    @api.multi
    def write(self, vals):
        employee = vals.get('employee', '')
        users = [self.env['hr.employee'].search([('id', '=', rec)]).user_id.id for rec in employee[0][2] if employee]
        self.env.ref("dtdream_project_manage.group_project_order_view").sudo().write({'users': [(6, 0, users)]})
        return super(dtdream_project_order_view, self).write(vals)

    employee = fields.Many2many('hr.employee', string='查看订单金额人员')
    name = fields.Char(default=lambda self: u'查看订单人员配置')
