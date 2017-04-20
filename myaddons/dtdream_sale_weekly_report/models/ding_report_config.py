# -*- coding: utf-8 -*-
from openerp import models, fields, api

# 钉钉周报配置
class ding_report_config(models.Model):
    _name = "ding.report.config"

    name = fields.Char(default="钉钉应用配置")
    agentid = fields.Char(string="钉钉应用id")