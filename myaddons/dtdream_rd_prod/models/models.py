# -*- coding: utf-8 -*-

from openerp import models, fields, api

class dtdream_rd_prod(models.Model):
    _name = 'dtdream_rd_prod.dtdream_rd_prod'
    name = fields.Char("项目名称")
    code = fields.Char("项目编码")


# class dtdream_rd_version(models.Model):
#     _name = 'dtdream_rd_prod.dtdream_rd_version'
#     version_numb = fields.Char("版本号")
#     plan_dev_time = fields.Date("计划开发时间")
#     plan_pub_time = fields.Date("计划发布时间")
#     actual_dev_time = fields.Date("实际开发时间")
#     actual_pub_time = fields.Date("实际发布时间")