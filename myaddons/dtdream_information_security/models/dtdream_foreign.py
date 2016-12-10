# -*- coding: utf-8 -*-
from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp import models, fields, api
from openerp.osv import expression
from lxml import etree
import time
from openerp.exceptions import ValidationError

class dtdream_foreign(models.Model):
    _name = "dtdream.foreign"
    _description = u'对外披露'
    _inherit = ['mail.thread']
    @api.depends('applicant')
    def _compute_department_belong(self):
        for rec in self:
            rec.department = rec.applicant.department_id
    def _comepute_job_number(self):
        for rec in self:
            rec.workid = rec.applicant.job_number

    @api.depends('applicant')
    def _compute_employee(self):
        for rec in self:
            rec.manager = rec.applicant.department_id.manager_id
            if rec.applicant.department_id.parent_id:
                rec.department_02 = rec.applicant.department_id
                rec.sq_department_code = rec.applicant.department_id.code
                rec.department_01 = rec.applicant.department_id.parent_id
            else:
                rec.department_01 = rec.applicant.department_id
                rec.sq_department_code = rec.applicant.department_id.code

    @api.onchange('sfxqbmxy')
    def _onchange_sfxqbmxy(self):
        if self.sfxqbmxy == True:
            return {'warning':{
                'title': u'提示',
                'message': u'请咨询法务意见',
            }}

    applicant = fields.Many2one('hr.employee', string='申请人',default=lambda self: self.env["hr.employee"].search([("user_id", "=", self.env.user.id)]))
    name=fields.Char(default=lambda self:"对外披露")
    department = fields.Many2one('hr.department', string='所属部门', compute=_compute_department_belong)
    department_01 = fields.Many2one("hr.department", compute=_compute_employee, string="申请一级部门", store=True)
    department_02 = fields.Many2one("hr.department", compute=_compute_employee, string="申请二级部门", store=True)
    sq_department_code = fields.Char(compute=_compute_employee, string="申请部门编码", store=True)
    yuan_department_code = fields.Char(string="源部门编码", readonly=True)
    origin_department_01 = fields.Many2one("hr.department", string="信息源一级部门", store=True, required=True)
    origin_department_02 = fields.Many2one("hr.department", string="信息源二级部门", store=True)
    manager = fields.Many2one("hr.employee", string="直接主管", compute=_compute_employee, store=True)
    workid=fields.Char(string='工号',compute=_comepute_job_number)
    target=fields.Char(string='披露对象',required='true')
    attachment = fields.Binary(string="附件(限制25M以下)", store=True,required='true')
    attachment_name = fields.Char(string='附件名',required='true')
    reason=fields.Char(string='披露原因',required='true')
    secret_level = fields.Selection([('level_01', '机密'), ('level_02', '绝密'),('level_03', '内部公开 ')], string="最高密级", required=True)
    sfxqbmxy=fields.Boolean(string='是否需签保密协议')
    sfxytm=fields.Boolean(string='是否需要脱敏')
    tminstructions=fields.Text(string="脱敏说明")
    approves = fields.Many2many('hr.employee', string='已审批的人')

    current_approve = fields.Many2one('hr.employee', string='当前处理人')
    state = fields.Selection([('0', '草稿'),
                              ('1', '直接主管审批'),
                              ('2', '权签人审批'),
                              ('99', '完成'),
                              ], string='状态', default='0')

    @api.multi
    def wkf_draft(self):
        approve = self.current_approve
        self.write({"state": '0', 'approves':[(4, approve.id)]})
    @api.multi
    def wkf_department_approve(self):
        current_approve = self.applicant.department_id.manager_id
        self.write({"state": '1', 'current_approve': current_approve.id})
    @api.multi
    def wkf_demand_approve(self):
        approve = self.current_approve
        if self.secret_level == "level_02":
            cr = self.env["dtdream.information.people"].search()
            current_approve = cr.juemi_shenpi
            # current_approve = self.applicant.department_id.parent_id.manager_id or self.applicant.department_id.manager_id
        else:
            current_approve = self.applicant.department_id.parent_id.manager_id or self.applicant.department_id.manager_id
        self.write({"state": '2', 'current_approve': current_approve.id, 'approves':[(4, approve.id)]})
    @api.multi
    def wkf_done(self):
        approve = self.current_approve
        self.write({"state": '99', 'current_approve': '', 'approves': [(4, approve.id)]})

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        params = self._context.get('params', {})
        action = params.get('action', None)
        if action:
            menu = self.env["ir.actions.act_window"].search([('id', '=', action)]).name
        if menu == u"与我相关":
            uid = self._context.get('uid', '')
            domain = expression.AND([['|', '|', '|', ('applicant.user_id', '=', uid), ('create_uid', '=', uid),
                                          ('current_approve.user_id', '=', uid), ('approves.user_id', '=', uid)],
                                         domain])
        return super(dtdream_foreign, self).search_read(domain=domain, fields=fields, offset=offset,limit=limit, order=order)

    @api.multi
    def _compute_is_shenpiren(self):
        for rec in self:
            if self.env.user == rec.current_approve.user_id:
                rec.is_shenpiren = True
            else:
                rec.is_shenpiren = False

    is_shenpiren = fields.Boolean(string="是否审批人", compute=_compute_is_shenpiren, readonly=True)





