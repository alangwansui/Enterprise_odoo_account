# -*- coding: utf-8 -*-
from openerp import models, fields, api
from openerp.exceptions import ValidationError

class lxWizard(models.TransientModel):
    _name = 'dtdream_prod_appr.wizard'
    reason = fields.Char()

    @api.one
    def btn_confirm(self):
        current_lixiang = self.env['dtdream_prod_appr'].browse(self._context['active_id'])
        if current_lixiang.state=='state_00':
            current_lixiang.signal_workflow('btn_to_lixiang')
        elif current_lixiang.state=='state_01':
            current_lixiang.signal_workflow('btn_to_ztsj')
        elif current_lixiang.state=='state_02':
            current_lixiang.signal_workflow('btn_to_ddkf')
        elif current_lixiang.state=='state_03':
            current_lixiang.signal_workflow('btn_to_yzfb')
        elif current_lixiang.state=='state_04':
            current_lixiang.signal_workflow('btn_to_jieshu')


class lxWizardappr(models.TransientModel):
    _name = 'dtdream_prod_appr.wizardappr'
    reason = fields.Char()

    @api.one
    def btn_confirm(self):
        current_lixiang = self.env['dtdream_prod_appr'].browse(self._context['active_id'])
        current_lixiang.write({'is_appred':True})
        current_lixiang.current_approver_user = [(5,)]
        records = self.env['dtdream_rd_approver'].search([('pro_state','=','state_02'),('level','=','level_01')])           #审批人配置
        rold_ids = []
        for record in records:
            rold_ids +=[record.name.id]
        appro = self.env['dtdream_rd_role'].search([('role_id','=',current_lixiang.id),('cof_id','in',rold_ids),('person','!=',False)]) #产品中角色配置
        for record in appro:
            self.env['dtdream_rd_process'].create({"role":record.cof_id.id, "ztsj_process_id":current_lixiang.id,'pro_state':'state_02','approver':record.person.id,'approver_old':record.person.id,'level':'level_01'})       #审批意见记录创建
            current_lixiang.write({'current_approver_user': [(4, record.person.user_id.id)]})

        processes = self.env['dtdream_rd_process'].search([('ztsj_process_id','=',current_lixiang.id),('pro_state','=','state_02'),('level','=','level_01'),('is_new','=',True)])
        if len(processes)==0:
            ctd = self.env['dtdream_rd_approver'].search([('department','=',current_lixiang.department.id)],limit=1)
            self.env['dtdream_rd_process'].create({"role":ctd.name.id,"ztsj_process_id":current_lixiang.id,'pro_state':current_lixiang.state,'approver':current_lixiang.department.manager_id.id,'approver_old':current_lixiang.department.manager_id.id,'level':'level_02'})       #审批意见记录创建
            current_lixiang.current_approver_user = [(5,)]
            current_lixiang.write({'current_approver_user': [(4, current_lixiang.department.manager_id.user_id.id)]})




class versionWizard(models.TransientModel):
    _name = 'dtdream_rd_version.wizard'
    reason = fields.Char()

    @api.one
    def btn_version_submit(self):
        current_version = self.env['dtdream_rd_version'].browse(self._context['active_id'])
        state = current_version.version_state
        if state=='initialization':
            current_version.signal_workflow('btn_to_kaifa')
        elif state=='Development':
            current_version.signal_workflow('btn_to_dfb')
        elif state=='pending':
            current_version.signal_workflow('btn_to_yfb')


