# -*- coding: utf-8 -*-

from openerp import models, fields, api

# class dtdream_partner(models.Model):
#     _name = 'dtdream_partner.dtdream_partner'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100

# 继承客户模型，修改字段
class dtdream_partner(models.Model):
    _inherit = ["res.partner"]

    # partner_no = fields.Char(string="客户编号",compute='')
    partner_no = fields.Char(string='客户编号')
    industry_id = fields.Many2one('dtdream.industry',string='行业',required=True)
    partner_important = fields.Selection([
        ('ss', 'SS'),
        ('s', 'S'),
        ('a','A'),
        ('b','B'),
        ('c','C'),
        ('d','D'),
    ], string='客户重要级', required=True)
    partner_owner = fields.Many2one('res.users', string='营销责任人',required=True)


# # 新增行业类别
# class dtdream_industry(models.Model):
#     _name = 'dtdream.industry'

#     name = fields.Char(string='行业名称',required=True)
#     parent_no = fields.Char(string='行业编码',required=True)
#     parent_id = fields.Many2one('dtdream.industry', string='上级行业')
#     children_ids = fields.One2many('dtdream.industry','parent_id',string='下级行业')
