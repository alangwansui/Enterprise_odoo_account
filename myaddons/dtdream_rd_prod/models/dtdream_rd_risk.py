# -*- coding: utf-8 -*-
from openerp import models, fields, api


#风险
class dtdream_rd_risk(models.Model):
    _name = 'dtdream_rd_risk'
    risk_id = fields.Many2one("dtdream_prod_appr",'产品名称')
    risk_ver_id = fields.Many2one("dtdream_rd_version", '版本名称')
    name = fields.Text('风险描述', required=True)
    name_old = fields.Text('风险描述')
    chance_describe = fields.Text('机遇描述', required=True)
    chance_describe_old = fields.Text('机遇描述')
    plan_close_time = fields.Date("计划关闭日期")
    plan_close_time_old = fields.Date("计划关闭日期")
    PDT = fields.Many2one("hr.employee",'责任人', required=True)
    PDT_old = fields.Many2one("hr.employee")
    risk_state = fields.Many2one('dtdream_rd_riskconfig','风险状态', required=True, track_visibility='onchange')
    risk_state_old = fields.Many2one('dtdream_rd_riskconfig')
    risk_sort_state = fields.Many2one('dtdream_rd_risksortconfig', '风险类别')
    risk_sort_state_old = fields.Many2one('dtdream_rd_risksortconfig')

    # 判断风险任意字段是否变更
    def is_risk_change(self):
        name_ins = self.name != self.name_old
        chance_describe_ins = self.chance_describe != self.chance_describe_old
        plan_close_time_ins = self.plan_close_time != self.plan_close_time_old
        PDT_ins = self.PDT != self.PDT_old
        risk_state_ins = self.risk_state != self.risk_state_old
        risk_sort_state_ins = self.risk_sort_state != self.risk_sort_state_old
        return name_ins or chance_describe_ins or plan_close_time_ins or plan_close_time_ins or PDT_ins or risk_state_ins or risk_sort_state_ins

    # 判断风险类别是否变更
    def risk_sort_state_change(self):
        old = self.risk_sort_state_old
        new = self.risk_sort_state
        risk_sort_state_ins = ''
        if new != old:
            risk_sort_state_ins = u"<p>风险类别：%s --> %s</p>" % (old.name, new.name)
        return risk_sort_state_ins

    # 判断风险状态是否变更
    def risk_state_change(self):
        old = self.risk_state_old
        new = self.risk_state
        risk_state_ins = ''
        if new != old:
            risk_state_ins = u"<p>风险状态：%s --> %s</p>" % (old.name, new.name)
        return risk_state_ins

    # 判断风险责任人是否变更
    def risk_PDT_change(self):
        old = self.PDT_old
        new = self.PDT
        PDT_ins = ''
        if new != old:
            PDT_ins = u"<p>风险责任人：%s --> %s</p>" % (old.name_related, new.name_related)
        return PDT_ins

    # 判断风险计划关闭日期是否变更
    def risk_plan_close_time_change(self):
        old = self.plan_close_time_old
        new = self.plan_close_time
        plan_close_time_ins = ''
        if new != old:
            plan_close_time_ins = u"<p>风险计划关闭日期：%s --> %s</p>" % (old, new)
        return plan_close_time_ins

    # 判断机遇描述是否变更
    def risk_chance_describe_change(self):
        old = self.chance_describe_old
        new = self.chance_describe
        chance_describe_ins = ''
        if new != old:
            chance_describe_ins = u"<p>机遇描述：%s --> %s</p>" % (old, new)
        return chance_describe_ins

    # 判断风险描述是否变更
    def risk_name_change(self):
        old = self.name_old
        new = self.name
        name_ins = ''
        if new != old:
            name_ins = u"<p>风险描述：%s --> %s</p>" % (old, new)
        return name_ins

    # 更新信息至old字段
    def update_old_ins(self):
        self.write({'risk_state_old': self.risk_state.id})
        self.write({'name_old': self.name})
        self.write({'chance_describe_old': self.chance_describe})
        self.write({'plan_close_time_old': self.plan_close_time})
        self.write({'PDT_old': self.PDT.id})
        self.write({'risk_sort_state_old': self.risk_sort_state.id})