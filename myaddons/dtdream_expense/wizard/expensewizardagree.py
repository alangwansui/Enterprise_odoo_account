# -*- coding: utf-8 -*-

from openerp import models, fields, api,exceptions
from datetime import datetime
from openerp .exceptions import ValidationError,Warning
import time



class ExpenseWizard(models.TransientModel):
    _name = 'dtdream.expense.agree.wizard'
    advice = fields.Text(string="审批意见")

    @api.multi
    def btn_confirm(self):
        current_expense_models = self.env['dtdream.expense.report'].browse(self._context['active_ids'])
        current_login_employee = self.env['hr.employee'].search([('user_id','=',self.env.user.id)])
        for current_expense_model in current_expense_models:
            if current_login_employee not in current_expense_model.current_handler and self.env.user.id != 1:
                raise ValidationError("您不是当前审批人！")
            else:
                old_state = current_expense_model.state
                parentdepartmentid = current_expense_model.department_id.parent_id  # 上级部门是否为空，为空则为一级，否则为二级
                no_one_auditor = current_expense_model.department_id.no_one_auditor  # 第一审批人在hr.employee中
                no_one_auditor_amount = current_expense_model.department_id.no_one_auditor_amount  # 第一审批人上限金额
                no_two_auditor = current_expense_model.department_id.no_two_auditor  # 第二审批人在hr.employee中
                no_two_auditor_amount = current_expense_model.department_id.no_two_auditor_amount  # 第二审批人上限金额
                zongcai_hr_employee = self.env['dtdream.expense.president'].search([('type', '=', 'zongcai')]).name  # 总裁在hr.employee中的
                old_which_quanqianren = ''
                current_handlers = current_expense_model.current_handler
                current_expense_model.write({'current_handler': [(3, current_login_employee.id)]})
                current_expense_model.write({'hasauditor': [(4, current_login_employee.id)]})
                if current_expense_model.state == "xingzheng":

                    if current_expense_model.showcuiqian == '0':
                        raise exceptions.ValidationError('请先确认签收纸件！')

                    if current_expense_model.applicant == current_expense_model.department_id.manager_id:
                        if parentdepartmentid:
                            # 二级部门主管
                            if len(current_expense_model.benefitdep_ids) > 1:
                                # 受益部门多于一个
                                current_expense_model.xingzheng2who = "1"
                            else:
                                if (current_expense_model.applicant == no_two_auditor and current_expense_model.total_invoicevalue <= no_two_auditor_amount) or \
                                        (current_expense_model.applicant == no_one_auditor and current_expense_model.total_invoicevalue <= no_one_auditor_amount):
                                    # 和权签人之一重复且没有超过金额，到主管审批(由上级部门主管审批)
                                    current_expense_model.xingzheng2who = "1"
                                else:
                                    # 其他到权签人审批
                                    current_expense_model.xingzheng2who = "2"
                        else:
                            # 一级主管提交到主管审批（总裁）
                            current_expense_model.xingzheng2who = "1"
                    else:  # 员工提交到主管
                        current_expense_model.xingzheng2who = "1"

                elif current_expense_model.state == "zhuguan":
                    if len(current_expense_model.benefitdep_ids) > 1:
                        if current_expense_model.department_id.manager_id == current_expense_model.applicant and \
                                not current_expense_model.department_id.parent_id:
                            # 一级部门主管单据，主管审批（总裁）后直接到直接到接口会计
                            current_expense_model.zhuguan_quanqian_jiekoukuaiji = "2"
                        else:
                            if not current_expense_model.no_one_quanqian and not current_expense_model.no_two_quanqian \
                                    and not current_expense_model.if_by_zongcai:
                                current_expense_model.zhuguan_quanqian_jiekoukuaiji = "2"
                            else:
                                current_expense_model.zhuguan_quanqian_jiekoukuaiji = "1"

                    else:
                        if current_expense_model.department_id.manager_id == current_expense_model.applicant:
                            # 主管审批环节，如果是部门主管的单据，总裁或者上级部门主管审批后直接到直接到接口会计
                            current_expense_model.zhuguan_quanqian_jiekoukuaiji = "2"

                        elif current_handlers[0] == no_two_auditor and current_expense_model.total_invoicevalue <= no_two_auditor_amount or \
                                current_handlers[0] == no_one_auditor and current_expense_model.total_invoicevalue <= no_one_auditor_amount:
                            # 和权签人重复且没有超过金额
                            current_expense_model.zhuguan_quanqian_jiekoukuaiji = "2"

                        else:
                            current_expense_model.zhuguan_quanqian_jiekoukuaiji = "1"

                elif current_expense_model.state == "quanqianren":
                    old_which_quanqianren = current_expense_model.which_quanqianren
                    if len(current_expense_model.benefitdep_ids) > 1:
                        if len(current_expense_model.current_handler) == 0:
                            if current_expense_model.no_two_quanqian and old_which_quanqianren == '1':
                                pass_jiekoukuaiji = "0"
                                current_expense_model.which_quanqianren = '2'
                                current_expense_model.current_handler = current_expense_model.no_two_quanqian
                            elif not current_expense_model.no_two_quanqian and old_which_quanqianren == '1' and current_expense_model.if_by_zongcai:
                                pass_jiekoukuaiji = "0"
                                current_expense_model.which_quanqianren = '3'
                                current_expense_model.current_handler = zongcai_hr_employee
                            elif current_expense_model.if_by_zongcai and old_which_quanqianren == '2':
                                pass_jiekoukuaiji = "0"
                                current_expense_model.which_quanqianren = '3'
                                current_expense_model.current_handler = zongcai_hr_employee
                            else:
                                pass_jiekoukuaiji = "1"
                        else:
                            pass_jiekoukuaiji = "0"

                    else:
                        if current_handlers[0] == zongcai_hr_employee:
                            # 总裁审批之后到接口会计
                            pass_jiekoukuaiji = "1"
                        elif current_handlers[0] == no_two_auditor and current_expense_model.total_invoicevalue <= no_two_auditor_amount or \
                                current_handlers[0] == no_one_auditor and current_expense_model.total_invoicevalue <= no_one_auditor_amount:
                            # 没有超出权签人金额，到接口会计
                            pass_jiekoukuaiji="1"

                        elif current_handlers[0] == no_two_auditor and current_expense_model.total_invoicevalue > no_two_auditor_amount:
                            # 超出第二权签人金额，到总裁审批
                            re_currentauditperson = zongcai_hr_employee
                            current_expense_model.which_quanqianren = '3'
                            pass_jiekoukuaiji = "0"
                            current_expense_model.write({"hasauditor": [(4, current_handlers[0].id)]})
                            current_expense_model.current_handler = re_currentauditperson
                            # current_expense_model.write({'current_handler': [(6, re_currentauditperson.id)]})
                            current_expense_model.send_mail(u"【提醒】{0}于{1}提交的费用报销单,请您审批!".format(current_expense_model.applicant.name, current_expense_model.create_date[:10]),
                               u"%s提交的费用报销单,等待您的审批!" % current_expense_model.applicant.name,
                               email_to=re_currentauditperson.work_email)
                            current_expense_model.send_dingding_msg(current_expense_model, re_currentauditperson.user_id.id)

                        elif current_handlers[0] == no_one_auditor and current_expense_model.total_invoicevalue > no_one_auditor_amount:
                            # 超出第一权签人金额，到第二权签人审批
                            re_currentauditperson = no_two_auditor
                            current_expense_model.which_quanqianren = '2'
                            pass_jiekoukuaiji = "0"
                            current_expense_model.write({"hasauditor": [(4, current_handlers[0].id)]})
                            current_expense_model.current_handler = re_currentauditperson
                            # current_expense_model.write({'current_handler': [(6, re_currentauditperson.id)]})
                            current_expense_model.send_mail(u"【提醒】{0}于{1}提交的费用报销单,请您审批!".format(current_expense_model.applicant.name, current_expense_model.create_date[:10]),
                               u"%s提交的费用报销单,等待您的审批!" % current_expense_model.applicant.name,
                               email_to=re_currentauditperson.work_email)
                            current_expense_model.send_dingding_msg(current_expense_model, re_currentauditperson.user_id.id)

                        else:
                            raise ValidationError("相关信息已经发生变更，请联系管理员进行更改！")
                    current_expense_model.write({'can_pass_jiekoukuaiji':pass_jiekoukuaiji})

                elif current_expense_model.state == "jiekoukuaiji":
                    if current_expense_model.showcuiqian != '2':
                        raise Warning(u'请先确认签收纸件！')

                if not current_expense_model.current_handler:
                        current_expense_model.signal_workflow('btn_agree')
                if not self.advice:
                    auditadvice = ''
                else:
                    auditadvice = self.advice

                new_state = current_expense_model.state
                new_which_quanqianren = current_expense_model.which_quanqianren
                mess_state1 = dict(current_expense_model._columns['state'].selection)[old_state]
                mess_state2 = dict(current_expense_model._columns['state'].selection)[new_state]
                if old_state == "quanqianren":
                    if old_which_quanqianren == "1":
                        mess_state1 = u"第一权签人审批"
                    elif old_which_quanqianren == "2":
                        mess_state1 = u"第二权签人审批"
                    elif old_which_quanqianren == "3":
                        mess_state1 = u"总裁审批"
                if new_state == "quanqianren":
                    if new_which_quanqianren == "1":
                        mess_state2 = u"第一权签人审批"
                    elif new_which_quanqianren == "2":
                        mess_state2 = u"第二权签人审批"
                    elif new_which_quanqianren == "3":
                        mess_state2 = u"总裁审批"
                message = u"同意，"+mess_state1+"---->"+mess_state2
                current_expense_model.message_post(body=message + u"，审批意见:" + auditadvice)


