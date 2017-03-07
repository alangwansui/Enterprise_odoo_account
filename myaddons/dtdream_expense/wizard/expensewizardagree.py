# -*- coding: utf-8 -*-

from openerp import models, fields, api,exceptions
from datetime import datetime
from openerp .exceptions import ValidationError,Warning
import time



class ExpenseWizard(models.TransientModel):
    _name = 'dtdream.expense.agree.wizard'

    advice = fields.Text(string="审批意见")

    ###################公用函数定义区##################################################
    # 获取公司总裁在hr.employee中的id,模型名称:dtdream.expense.president
    def get_company_president(self):
        re = self.env['dtdream.expense.president'].search([('type', '=', 'zongcai')])
        return re.name.id

    # 根据uid（res.users中的id）获取登录账号
    def get_users_login(self, uuid):
        re = self.env['res.users'].search([('id', '=', uuid)])
        return re.login

    # 根据id(hr.employee)获取登录账号
    def get_employee_login(self, hrid):
        re = self.env['hr.employee'].search([('id', '=', hrid)])
        return re.login

    # 根据登录账号获取员工所在部门id
    def get_employee_departmentid(self, loginid):
        re = self.env['hr.employee'].search([('login', '=', loginid)])
        return re.department_id[0].id

    # 根据登录账号获取员工所在部门的上级部门id
    def get_employee_parentdepartmentid(self, loginid):
        re = self.env['hr.employee'].search([('login', '=', loginid)])
        return re.department_id[0].parent_id.id

    # 根据uid(res.users)获取hr.employee 的id
    def get_employee_id(self, uuid):
        res = self.env['res.users'].search([('id', '=', uuid)])
        re = self.env['hr.employee'].search([('login', '=', res.login)])
        return re.id

    # 根据hr.employee 的id获取uid(res.users)
    def get_user_id(self, hrid):

        re = self.env['hr.employee'].search([('id', '=', hrid)])

        res = self.env['res.users'].search([('login', '=', re.login)])

        return res.id

    # 根据uid（res.users中的id）获取直接主管
    def get_zhuguan(self, uuid):
        hr_employee_login = self.get_users_login(uuid)
        depid = self.get_employee_departmentid(hr_employee_login)
        re = self.env['hr.department'].search([('id', '=', depid)])
        return re.manager_id[0].id

    # 根据departmentid 获取直接主管
    def get_zhuguanfromdepid(self, depid):

        re = self.env['hr.department'].search([('id', '=', depid)])
        return re.manager_id[0].id

    # 根据uid（res.users中的id）获取第一审批人
    def get_no_one_auditor(self, uuid):
        hr_employee_login = self.get_users_login(uuid)
        depid = self.get_employee_departmentid(hr_employee_login)
        re = self.env['hr.department'].search([('id', '=', depid)])
        return re.no_one_auditor[0].id

    # 根据uid（res.users中的id）获取第一审批人上限金额
    def get_no_one_auditor_amount(self, uuid):
        hr_employee_login = self.get_users_login(uuid)
        depid = self.get_employee_departmentid(hr_employee_login)
        re = self.env['hr.department'].search([('id', '=', depid)])
        return re.no_one_auditor_amount

    # 根据uid（res.users中的id）获取第二审批人
    def get_no_two_auditor(self, uuid):
        hr_employee_login = self.get_users_login(uuid)
        depid = self.get_employee_departmentid(hr_employee_login)
        re = self.env['hr.department'].search([('id', '=', depid)])
        return re.no_two_auditor[0].id

    # 根据uid（res.users中的id）获取接口会计
    def get_jiekoukuaiji(self, uuid):
        hr_employee_login = self.get_users_login(uuid)
        depid = self.get_employee_departmentid(hr_employee_login)
        re = self.env['hr.department'].search([('id', '=', depid)])
        return re.jiekoukuaiji[0].id

    # 根据uid（res.users中的id）获取出纳会计
    def get_chuna(self, uuid):
        hr_employee_login = self.get_users_login(uuid)
        depid = self.get_employee_departmentid(hr_employee_login)
        re = self.env['hr.department'].search([('id', '=', depid)])
        return re.chunakuaiji[0].id

    # 根据uid（res.users中的id）获取行政助理
    def get_xingzheng(self, uuid):
        hr_employee_login = self.get_users_login(uuid)
        depid = self.get_employee_departmentid(hr_employee_login)
        re = self.env['hr.department'].search([('id', '=', depid)])
        return re.assitant_id[0].id

    # 根据uid（res.users中的id）获取第二审批人上限金额
    def get_no_two_auditor_amount(self, uuid):
        hr_employee_login = self.get_users_login(uuid)
        depid = self.get_employee_departmentid(hr_employee_login)
        re = self.env['hr.department'].search([('id', '=', depid)])
        return re.no_two_auditor_amount

    ##################################################################################

    @api.multi
    def btn_confirm(self):
        current_expense_models = self.env['dtdream.expense.report'].browse(self._context['active_ids'])
        current_login_employee = self.env['hr.employee'].search([('user_id','=',self.env.user.id)])
        for current_expense_model in current_expense_models:
            if current_login_employee not in current_expense_model.current_handler and self.env.user.id != 1:
                raise ValidationError("您不是当前审批人！")
            else:
                old_state = current_expense_model.state
                create_hr_id = self.get_employee_id(current_expense_model.create_uid.id)
                zhuguan_id_hr_employee = self.get_zhuguan(current_expense_model.create_uid.id)  # 主管hr.employee中id
                zhuguan_login = self.get_employee_login(zhuguan_id_hr_employee)
                parentdepartmentid = self.get_employee_parentdepartmentid(zhuguan_login)  # 上级部门是否为空，为空则为一级，否则为二级
                no_one_auditor = self.env['hr.department'].search([('id', '=', current_expense_model.department_id.id)]).no_one_auditor  # 第一审批人在hr.employee中
                no_one_auditor_amount = self.get_no_one_auditor_amount(current_expense_model.create_uid.id)  # 第一审批人上限金额
                no_two_auditor = self.env['hr.department'].search([('id', '=', current_expense_model.department_id.id)]).no_two_auditor  # 第二审批人在hr.employee中
                no_two_auditor_amount = self.get_no_two_auditor_amount(current_expense_model.create_uid.id)  # 第二审批人上限金额
                zongcai_hr_employee = self.env['dtdream.expense.president'].search([('type', '=', 'zongcai')]).name  # 总裁在hr.employee中的
                old_which_quanqianren = ''
                current_handlers = current_expense_model.current_handler
                current_expense_model.write({'current_handler': [(3, current_login_employee.id)]})
                current_expense_model.write({'hasauditor': [(4, current_login_employee.id)]})
                if current_expense_model.state == "xingzheng":

                    if current_expense_model.showcuiqian == '0':
                        raise exceptions.ValidationError('请先确认签收纸件！')

                    if create_hr_id == zhuguan_id_hr_employee:
                        if parentdepartmentid:
                            # 二级部门主管
                            if len(current_expense_model.benefitdep_ids) > 1:
                                # 受益部门多于一个
                                current_expense_model.xingzheng2who = "1"
                            else:
                                if (create_hr_id == no_two_auditor.id and current_expense_model.total_invoicevalue <= no_two_auditor_amount) or \
                                        (create_hr_id == no_one_auditor.id and current_expense_model.total_invoicevalue <= no_one_auditor_amount):
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
                        if current_expense_model.department_id.manager_id.user_id == current_expense_model.create_uid and \
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
                        if current_expense_model.department_id.manager_id.user_id == current_expense_model.create_uid:
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
                            current_expense_model.send_mail(u"【提醒】{0}于{1}提交的费用报销单,请您审批!".format(current_expense_model.create_uid.name, current_expense_model.create_date[:10]),
                               u"%s提交的费用报销单,等待您的审批!" % current_expense_model.create_uid.name,
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
                            current_expense_model.send_mail(u"【提醒】{0}于{1}提交的费用报销单,请您审批!".format(current_expense_model.create_uid.name, current_expense_model.create_date[:10]),
                               u"%s提交的费用报销单,等待您的审批!" % current_expense_model.create_uid.name,
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


