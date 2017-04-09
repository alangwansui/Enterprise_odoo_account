# -*- coding: utf-8 -*-
from openerp import models, fields, api

class dtdream_authorization_attachment(models.Model):
    _name = "dtdream.authorization.attachment"
    _description = u"合同评审附件"

    contract_id = fields.Many2one("dtdream.project.bid.authorize.apply.attachment_ids", string="项目授权函")
    attachment = fields.Binary(string="附件", store=True, required=1,track_visibility='onchange')
    attachment_name = fields.Char(string="附件名", invisible=1)
    attachment_remark = fields.Char(string="说明")
    attachment_upper = fields.Many2one('hr.employee', string='上传者', default = lambda self:self.env['hr.employee'].search([('user_id', '=', self.env.user.id)]))