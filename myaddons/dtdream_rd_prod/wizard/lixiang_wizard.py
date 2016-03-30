# -*- coding: utf-8 -*-
from openerp import models, fields, api
from openerp.exceptions import ValidationError

class lxWizard(models.TransientModel):
    _name = 'dtdream_rd_prod.dtdream_prod_appr.wizard'
    reason = fields.Char()

    @api.one
    def btn_confirm(self):
        current_lixiang = self.env['dtdream_rd_prod.dtdream_prod_appr'].browse(self._context['active_id'])
        if current_lixiang.state=='state_00':
            lg = len(current_lixiang.version_ids)
            if lg <=0:
                raise ValidationError("提交项目时至少要有一个版本")
            # current_lixiang.write({'state': 'state_01'})
            current_lixiang.signal_workflow('btn_to_lixiang')
        elif current_lixiang.state=='state_01':
            # current_lixiang.write({'state': 'state_02'})
            current_lixiang.signal_workflow('btn_to_ztsj')
        elif current_lixiang.state=='state_02':
            # current_lixiang.write({'state': 'state_03'})
            current_lixiang.signal_workflow('btn_to_ddkf')
        elif current_lixiang.state=='state_03':
            # current_lixiang.write({'state': 'state_04'})
            current_lixiang.signal_workflow('btn_to_yzfb')
        elif current_lixiang.state=='state_04':
            current_lixiang.signal_workflow('btn_to_jieshu')


class versionWizard(models.TransientModel):
    _name = 'dtdream_rd_prod.dtdream_rd_version.wizard'
    reason = fields.Char()

    @api.one
    def btn_version_submit(self):
        current_version = self.env['dtdream_rd_prod.dtdream_rd_version'].browse(self._context['active_id'])
        state = current_version.version_state
        if state=='initialization':
            current_version.signal_workflow('btn_to_kaifa')
        elif state=='Development':
            current_version.signal_workflow('btn_to_dfb')
        elif state=='pending':
            current_version.signal_workflow('btn_to_yfb')


