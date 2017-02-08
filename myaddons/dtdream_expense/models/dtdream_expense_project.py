# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.exceptions import ValidationError


class dtdream_expense_project(models.Model):
    _name = "dtdream.expense.project"
    _description = u"报销分摊项目"

    name = fields.Many2one('crm.lead',string='项目名称')
    share_percent = fields.Float(string='分摊比例(%)')
    report_id = fields.Many2one('dtdream.expense.report',string='报销单号')

    @api.constrains('share_percent')
    def check_share_percent(self):
        if self.share_percent<=0 or self.share_percent>100:
            raise ValidationError("分摊比例不能小于等于0或大于100%")


class crm_lead_expense_extend(models.Model):
    _inherit = "crm.lead"

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        args = args or []
        domain = []
        if name:
            domain = [("name", operator, name)]
        if self._module == 'dtdream_expense':
            pos = self.sudo().search(domain + args, limit=limit)
        else:
            pos = self.search(domain + args, limit=limit)
        return pos.name_get()
    
    @api.multi
    def name_get(self):
        if self._module == 'dtdream_expense':
            data = []
            for rec in self:
                data.append((rec.id,rec.sudo().name))
            return data
        return super(crm_lead_expense_extend, self).name_get()