# -*- coding: utf-8 -*-

from openerp import models, fields, api
from datetime import datetime
from openerp.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
class dtdream_foreign_wizard(models.TransientModel):
    _name = "dtdream.foreign.wizard"
    name= fields.Char()
    reason = fields.Text(string="原因")

    def _check_juemi_shenpi(self, foreign):
        peo = self.env["dtdream.information.people"].sudo().search([])[0]
        if len(peo) < 1:
            raise ValidationError(u"请管理员配置绝密权签人")
        foreign.write({'current_approve': peo.juemi_shenpi.id})



    #同意
    @api.multi
    def btn_agree(self):
        foreign = self.env['dtdream.foreign'].browse(self._context['active_id'])
        foreign.write({'approves': [(4, foreign.current_approve.id)]})
        if foreign.state=='1':
            foreign.write({'current_approve': foreign.manager.id})
            foreign.signal_workflow('xxyjc_to_zgsp')
            foreign.message_poss_foreign_shenpi(statechange=u'信息员检查->主管审批', action=u'同意', next_shenpiren=foreign.current_approve.name,reason=self.reason)
            foreign.send_email_foreign(next_approver=foreign.current_approve)
        elif foreign.state == '2':
            if foreign.manager==foreign.origin_department_01.manager_id:                                                #申请人主管 与信息源主管一致
                if foreign.secret_level=="level_02":                                                                    #绝密
                    self._check_juemi_shenpi(foreign)
                    foreign.signal_workflow('zgsp_to_qqrsp')
                    foreign.message_poss_foreign_shenpi(statechange=u'主管审批->权签人审批', action=u'同意',next_shenpiren=foreign.current_approve.name,reason=self.reason)
                    foreign.send_email_foreign(next_approver=foreign.current_approve)
                else:
                    foreign.write({'current_approve':False})
                    foreign.signal_workflow('zgsp_to_wc')
                    foreign.message_poss_foreign_shenpi(statechange=u'主管审批->完成', action=u'同意',next_shenpiren=foreign.current_approve.name,reason=self.reason)
            else:
                if len(foreign.origin_department_01.manager_id)<1:
                    raise ValidationError(u"信息源部门主管为空")
                foreign.write({'current_approve': foreign.origin_department_01.manager_id.id})
                foreign.signal_workflow('zgsp_to_xxyzgsp')
                foreign.message_poss_foreign_shenpi(statechange=u'主管审批->信息源主管审批', action=u'同意',next_shenpiren=foreign.current_approve.name,reason=self.reason)
                foreign.send_email_foreign(next_approver=foreign.current_approve)
        elif foreign.state == '3':
            if foreign.secret_level == "level_02":
                self._check_juemi_shenpi(foreign)
                foreign.signal_workflow('xxyzgsp_to_qqrsp')
                foreign.message_poss_foreign_shenpi(statechange=u'信息源主管审批->权签人审批', action=u'同意',next_shenpiren=foreign.current_approve.name,reason=self.reason)
                foreign.send_email_foreign(next_approver=foreign.current_approve)
            else:
                foreign.write({'current_approve': False})
                foreign.signal_workflow('xxyzgsp_to_wc')
                foreign.message_poss_foreign_shenpi(statechange=u'信息源主管审批->完成', action=u'同意',next_shenpiren=foreign.current_approve.name,reason=self.reason)
        elif foreign.state == '4':
            foreign.write({'current_approve': False})
            foreign.signal_workflow('qqrsp_to_wc')
            foreign.message_poss_foreign_shenpi(statechange=u'权签人审批->完成', action=u'同意',next_shenpiren=foreign.current_approve.name,reason=self.reason)


    #驳回
    @api.multi
    def btn_reject(self):
        if not self.reason:
            raise ValidationError(u'请填写驳回原因')
        foreign = self.env['dtdream.foreign'].browse(self._context['active_id'])
        foreign.write({'approves': [(4, foreign.current_approve.id)]})
        if foreign.state=='1':
            foreign.write({'current_approve': False})
            foreign.signal_workflow('xxyjc_to_cg')
            foreign.message_poss_foreign_shenpi(statechange=u'信息员检查->草稿', action=u'驳回',next_shenpiren=foreign.current_approve.name,reason=self.reason)
        elif foreign.state == '2':
            foreign.write({'current_approve': False})
            foreign.signal_workflow('zgsp_to_cg')
            foreign.message_poss_foreign_shenpi(statechange=u'主管审批->草稿', action=u'驳回', next_shenpiren=foreign.current_approve.name,reason=self.reason)
        elif foreign.state == '3':
            foreign.write({'current_approve': False})
            foreign.signal_workflow('xxyzgsp_to_cg')
            foreign.message_poss_foreign_shenpi(statechange=u'信息源主管审批->草稿', action=u'驳回',next_shenpiren=foreign.current_approve.name,reason=self.reason)
        elif foreign.state == '4':
            foreign.write({'current_approve': False})
            foreign.signal_workflow('qqrsp_to_cg')
            foreign.message_poss_foreign_shenpi(statechange=u'权签人审批->草稿', action=u'驳回',next_shenpiren=foreign.current_approve.name,reason=self.reason)

    #不同意
    @api.multi
    def btn_disagree(self):
        if not self.reason:
            raise ValidationError(u'请填写不同意原因')
        foreign = self.env['dtdream.foreign'].browse(self._context['active_id'])
        foreign.write({'approves': [(4, foreign.current_approve.id)]})
        if foreign.state == '2':
            foreign.write({'current_approve': False})
            foreign.signal_workflow('zzsp_to_zz')
            foreign.message_poss_foreign_shenpi(statechange=u'主管审批->终止', action=u'不同意',next_shenpiren=foreign.current_approve.name, reason=self.reason)
        elif foreign.state == '3':
            foreign.write({'current_approve': False})
            foreign.signal_workflow('xxyzgsp_to_zz')
            foreign.message_poss_foreign_shenpi(statechange=u'信息源主管->终止', action=u'不同意',next_shenpiren=foreign.current_approve.name, reason=self.reason)
        elif foreign.state == '4':
            foreign.write({'current_approve': False})
            foreign.signal_workflow('qqrsp_to_zz')
            foreign.message_poss_foreign_shenpi(statechange=u'权签人审批->终止', action=u'不同意',next_shenpiren=foreign.current_approve.name, reason=self.reason)