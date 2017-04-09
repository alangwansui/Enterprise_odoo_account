# # -*- coding: utf-8 -*-
# from openerp import models, fields, api
#
# class dtdream_industry(models.Model):
#     _name = 'dtdream.industry'
#
#     name = fields.Char(string='系统部/行业名称',required=True)
#     code = fields.Char(string='系统部/行业编码',required=True)
#     parent_id = fields.Many2one('dtdream.industry', string='上级系统部/行业')
#
#     children_ids = fields.One2many('dtdream.industry','parent_id',string='下级系统部/行业')