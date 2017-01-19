# -*- coding: utf-8 -*-
from openerp import models, fields, api


#风险
class dtdream_rd_risk(models.Model):
    _name = 'dtdream_rd_risk'
    risk_id = fields.Many2one("dtdream_prod_appr",'产品名称')
    risk_ver_id = fields.Many2one("dtdream_rd_version", '版本名称')
    name = fields.Text('风险描述', required=True)
    chance_describe = fields.Text('机遇描述', required=True)
    plan_close_time = fields.Date("计划关闭日期")
    PDT = fields.Many2one("hr.employee",'责任人')
    risk_state = fields.Many2one('dtdream_rd_riskconfig','风险状态', required=True, track_visibility='onchange')
    risk_state_old = fields.Many2one('dtdream_rd_riskconfig')

