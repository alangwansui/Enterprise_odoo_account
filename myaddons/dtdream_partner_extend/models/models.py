# -*- coding: utf-8 -*-

from openerp import models, fields, api

# class dtdream_partner_extend(models.Model):
#     _name = 'dtdream_partner_extend.dtdream_partner_extend'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100