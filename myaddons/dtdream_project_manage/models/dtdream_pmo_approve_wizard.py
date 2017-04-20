# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.exceptions import AccessError


class dtdream_pmo_approve_wizard(models.TransientModel):
    _name = 'dtdream.pmo.approve.wizard'

    reason = fields.Text(string="理由", required=True, size=30)

    @api.multi
    def record_action_message(self, project, state, action, reason=''):
        project.message_post(body=u"""<table border="1" style="border-collapse: collapse;table-layout: fixed">
                                               <tr><td style="padding:10px">状态</td><td style="padding:10px">%s</td></tr>
                                               <tr><td style="padding:10px">操作</td><td style="padding:10px">%s</td></tr>
                                               <tr><td style="padding:10px;">原因</td><td style="padding:10px">%s</td></tr>
                                               </table>""" % (state, action, reason))

    @api.one
    def btn_confirm(self):
        model_name = self._context.get('active_model')
        if model_name in['dtdream.project.output.plan.manage', 'dtdream.project.output.deliver.manage']:
            record = self.env[model_name].browse(self._context['active_id'])
            record.write({'assess_time': fields.date.today(), 'state': '3', 'assess_times': record.assess_times + 1})
            if 'deliver' in model_name:
                record.project_manage_id.send_mail(subject=u'%s输出物的审核被驳回，请您重新提交后再发起审核' % (record.deliver or record.name.name),
                                                   content=u'%s输出物的审核被驳回，请您重新提交后再发起审核。' % (record.deliver or record.name.name),
                                                   name=record.header)
            else:
                record.project_manage_id.send_mail(subject=u'%s输出物的审核被驳回，请您重新提交后再发起审核' % (record.output or record.name.name),
                                                   content=u'%s输出物的审核被驳回，请您重新提交后再发起审核。' % (record.output or record.name.name),
                                                   name=record.header)
            record.create_approve_log(result=u'驳回,%s' % self.reason)
            record.update_current_approve()
        else:
            project = self.env['dtdream.project.manage'].browse(self._context['active_id'])
            if project.state_y == '12':
                approve_list = project.get_approve_list(result=True, suggestion=u'不同意, %s' % self.reason)
                project.write({'current_approve': [(6, 0, approve_list)]})
                self.record_action_message(project, state=u'交付服务经理确认', action=u'不同意', reason=self.reason)
                project.send_mail(subject=u'交付服务经理驳回', content=u'''您同步的项目信息及订单信息被%s驳回，
                请调整相关负责人。''' % self.env.user.employee_ids.name, name=project.project_manage)
            elif project.state_y == '21':
                self.record_action_message(project, state=u'PMO审核策划-->发起策划', action=u'驳回', reason=self.reason)
                project.signal_workflow('approve_reject')
            elif project.state_y == '32':
                self.record_action_message(project, state=u'运维服务经理审核-->交付运维测试', action=u'驳回', reason=self.reason)
                project.signal_workflow('approve_reject')


class dtdream_yunwei_confirm_wizard(models.TransientModel):
    _name = 'dtdream.yunwei.confirm.wizard'

    yunwei = fields.Selection([('0', '否'), ('1', '是')], string='是否转运维')

    def judge_role_yunwei_setted(self, project):
        yunwei, deliver = False, False
        for rec in project.project_struction_inner:
            if rec.role.name == self.env.ref('dtdream_project_manage.dtdream_project_role_YWF').name:
                yunwei = True
            if rec.role.name == self.env.ref('dtdream_project_manage.dtdream_project_role_JFF').name:
                deliver = True
        return yunwei, deliver

    @api.one
    def btn_confirm(self):
        project = self.env['dtdream.project.manage'].browse(self._context['active_id'])
        if self.yunwei == '1':
            if not all(self.judge_role_yunwei_setted(project)):
                raise AccessError("项目章程公司内部人员中未设置'运维管控负责人'和'交付负责人'。")
            if not any([True for rec in project.role if rec.name ==
                    self.env.ref('dtdream_project_manage.dtdream_project_role_YW').name]):
                raise AccessError("运维服务经理未设置，请在项目负责人中进行设置。")
        project.yunwei = self.yunwei
        project.signal_workflow('next_stage')
