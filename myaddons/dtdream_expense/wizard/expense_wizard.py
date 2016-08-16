# -*- coding: utf-8 -*-

from openerp import models, fields, api,exceptions
from datetime import datetime
from openerp .exceptions import ValidationError,Warning
import time

class ExpenseWizard(models.TransientModel):
    _name = 'dtdream.expense.wizard'

    def _get_states_now(self):

        # print '---------', self._context
        #
        # cur_state = self.env['dtdream.expense.report'].browse(self._context['active_id']).state
        # print  '----------', cur_state
        #
        # if cur_state == 'xingzheng':
        #     re = [('draft', '申请人')]
        # elif cur_state == 'zhuguan':
        #     re = [('draft', '申请人'), ('xingzheng', '行政助理')]
        # elif cur_state == 'quanqianren':
        #     re = [('draft', '申请人'), ('xingzheng', '行政助理'), ('zhuguan', '主管')]
        # elif cur_state == 'jiekoukuaiji':
        re = [('draft', '申请人'), ('xingzheng', '行政助理'), ('zhuguan', '主管'), ('quanqianren', '权签人')]
        return re

    state = fields.Selection(selection='_get_states_now', string="节点")

    liyou = fields.Text("驳回原因", required=True)

#发送邮件公共方法
    def get_base_url(self, cr, uid):
        base_url = self.pool.get('ir.config_parameter').get_param(cr, uid, 'web.base.url')
        return base_url

    def get_mail_server_name(self):
        return self.env['ir.mail_server'].search([], limit=1).smtp_user

    def send_mail(self, subject, content, email_to, email_cc="", wait=False):
        base_url = self.get_base_url()
        link = '/web#id=%s&view_type=form&model=dtdream.expense.report' % self.env['dtdream.expense.report'].browse(self._context['active_id']).id
        url = base_url + link
        email_to = email_to
        email_cc = "" if email_cc == email_to else email_cc
        subject = subject
        if wait:
            appellation = u'{0},您好：'.format(self.name.user_id.name)
        else:
            # appellation = u'{0},您好：'.format(self.currentauditperson.user_id.name)
            appellation = u'您好：'
        content = content
        self.env['mail.mail'].create({
            'body_html': u'''<p>%s</p>
                                <p>%s</p>
                                <a href="%s">点击链接进入查看</a></p>
                                <p>dodo</p>
                                <p>万千业务，简单有do</p>
                                <p>%s</p>''' % (appellation, content, url, self.env['dtdream.expense.report'].browse(self._context['active_id']).write_date[:10]),
            'subject': '%s' % subject,
            'email_from': self.get_mail_server_name(),
            'email_to': '%s' % email_to,
            'auto_delete': False,
        }).send()

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

    @api.one
    def btn_confirm(self):

        current_expense_model = self.env['dtdream.expense.report'].browse(self._context['active_id'])

        zongcai_hr_employee_id = self.get_company_president()  # 总裁在hr.employee中的id
        zhuguan_id_hr_employee = self.get_zhuguan(current_expense_model.create_uid.id)  # 主管hr.employee中id
        no_one_auditor_hr_employee = self.get_no_one_auditor(current_expense_model.create_uid.id)  # 第一审批人在hr.employee中id
        no_one_auditor_amount = self.get_no_one_auditor_amount(current_expense_model.create_uid.id)  # 第一审批人上限金额
        no_two_auditor_hr_employee = self.get_no_two_auditor(current_expense_model.create_uid.id)  # 第二审批人在hr.employee中id
        no_two_auditor_amount = self.get_no_two_auditor_amount(current_expense_model.create_uid.id)  # 第二审批人上限金额
        jiekoukuaiji = self.get_jiekoukuaiji(current_expense_model.create_uid.id)  # 接口会计
        zhuguan_login = self.get_employee_login(zhuguan_id_hr_employee)
        parentdepartmentid = self.get_employee_parentdepartmentid(zhuguan_login)  # 上级部门是否为空，为空则为一级，否则为二级
        create_hr_id = self.get_employee_id(current_expense_model.create_uid.id)  # 本单创建人hr.employee中id

        re_currentauditperson = ''



        if self.state=="draft" and current_expense_model.state=="xingzheng":
            #日志
            message = u"驳回，状态：行政助理审批---->草稿"
            current_expense_model.message_post(body=message + u"，审批意见:" + self.liyou)

            shenqinren = self.get_employee_id(current_expense_model.create_uid.id)
            emailto = self.env['hr.employee'].search([('id', '=', shenqinren)]).work_email
            self.send_mail(u"【提醒】{0}于{1}提交的费用报销单被行政助理驳回!".format(current_expense_model.create_uid.name, current_expense_model.create_date[:10]),
                           u"%s提交的费用报销单被行政助理驳回。" % current_expense_model.create_uid.name,
                           email_to=emailto)

            current_expense_model.signal_workflow('btn_refuse_xingzheng_to_draft')


        elif self.state=="draft" and current_expense_model.state=="zhuguan":
            message = u"驳回，状态：主管审批---->草稿"
            current_expense_model.message_post(body=message + u"，审批意见:" + self.liyou)

            shenqinren = self.get_employee_id(current_expense_model.create_uid.id)
            emailto = self.env['hr.employee'].search([('id', '=', shenqinren)]).work_email
            self.send_mail(u"【提醒】{0}于{1}提交的费用报销单被主管驳回!".format(current_expense_model.create_uid.name,
                                                                 current_expense_model.create_date[:10]),
                           u"%s提交的费用报销单被主管驳回。" % current_expense_model.create_uid.name,
                           email_to=emailto)

            current_expense_model.signal_workflow('btn_refuse_zhuguan_to_draft')

        elif self.state=="xingzheng" and current_expense_model.state=="zhuguan":
            message = u"驳回，状态：主管审批---->行政助理审批。"
            current_expense_model.message_post(body=message + u"，审批意见:" + self.liyou)
            xingzhengzhuli= self.get_xingzheng(current_expense_model.create_uid.id)
            emailto = self.env['hr.employee'].search([('id', '=', xingzhengzhuli)]).work_email
            self.send_mail(u"【提醒】{0}于{1}提交的费用报销单已被主管驳回，现在等待您的审批!".format(current_expense_model.create_uid.name,current_expense_model.create_date[:10]),u"%s提交的费用报销单已被主管驳回，现在等待您的审批。" % current_expense_model.create_uid.name,email_to=emailto)
            current_expense_model.signal_workflow('btn_refuse_zhuguan_to_xingzheng')

        elif self.state=="draft" and current_expense_model.state=="quanqianren":
            message = u"驳回，状态：权签人审批---->草稿"
            current_expense_model.message_post(body=message + u"，审批意见:" + self.liyou)

            shenqinren = self.get_employee_id(current_expense_model.create_uid.id)
            emailto = self.env['hr.employee'].search([('id', '=', shenqinren)]).work_email
            self.send_mail(u"【提醒】{0}于{1}提交的费用报销单被权签人驳回!".format(current_expense_model.create_uid.name,
                                                               current_expense_model.create_date[:10]),
                           u"%s提交的费用报销单被权签人驳回。" % current_expense_model.create_uid.name,
                           email_to=emailto)

            current_expense_model.signal_workflow('btn_refuse_quanqianren_to_draft')

        elif self.state=="xingzheng" and current_expense_model.state=="quanqianren":
            message = u"驳回，状态：权签人审批---->行政助理审批。"
            current_expense_model.message_post(body=message + u"，审批意见:" + self.liyou)
            xingzhengzhuli = self.get_xingzheng(current_expense_model.create_uid.id)
            emailto = self.env['hr.employee'].search([('id', '=', xingzhengzhuli)]).work_email
            self.send_mail(u"【提醒】{0}于{1}提交的费用报销单已被权签人驳回，现在等待您的审批!".format(current_expense_model.create_uid.name,
                                                                         current_expense_model.create_date[:10]),
                           u"%s提交的费用报销单已被主管驳回，现在等待您的审批。" % current_expense_model.create_uid.name, email_to=emailto)

            current_expense_model.signal_workflow('btn_refuse_quanqianren_to_xingzheng')

        elif self.state=="zhuguan" and current_expense_model.state=="quanqianren":
            message = u"驳回，状态：权签人审批---->主管审批"
            current_expense_model.message_post(body=message + u"，审批意见:" + self.liyou)


            if create_hr_id == zhuguan_id_hr_employee:
                if parentdepartmentid != False:  # 二级主管提交到一级主管
                    re_currentauditperson = self.get_zhuguanfromdepid(parentdepartmentid)
                else:  # 一级主管提交到总裁
                    re_currentauditperson = self.env['dtdream.expense.president'].search(
                        [('type', '=', 'zongcai')]).name.id
            else:  # 员工提交到二级主管
                re_currentauditperson = zhuguan_id_hr_employee

            emailto = self.env['hr.employee'].search([('id', '=', re_currentauditperson)]).work_email
            self.send_mail(u"【提醒】{0}于{1}提交的费用报销单已被权签人驳回，现在等待您的审批!".format(current_expense_model.create_uid.name,
                                                                          current_expense_model.create_date[:10]),
                           u"%s提交的费用报销单已被权签人驳回，现在等待您的审批。" % current_expense_model.create_uid.name,
                           email_to=emailto)

            current_expense_model.signal_workflow('btn_refuse_quanqianren_to_zhuguan')

        elif self.state=="draft" and current_expense_model.state=="jiekoukuaiji":
            message = u"驳回，状态：接口会计审批---->草稿"
            current_expense_model.message_post(body=message + u"，审批意见:" + self.liyou)

            shenqinren = self.get_employee_id(current_expense_model.create_uid.id)
            emailto = self.env['hr.employee'].search([('id', '=', shenqinren)]).work_email
            self.send_mail(u"【提醒】{0}于{1}提交的费用报销单被接口会计驳回!".format(current_expense_model.create_uid.name,
                                                                current_expense_model.create_date[:10]),
                           u"%s提交的费用报销单被接口会计驳回。" % current_expense_model.create_uid.name,
                           email_to=emailto)

            current_expense_model.signal_workflow('btn_refuse_jiekoukuaiji_to_draft')

        elif self.state=="xingzheng" and current_expense_model.state=="jiekoukuaiji":
            message = u"驳回，状态：接口会计审批---->行政助理审批。"
            current_expense_model.message_post(body=message + u"，审批意见:" + self.liyou)
            xingzhengzhuli = self.get_xingzheng(current_expense_model.create_uid.id)
            emailto = self.env['hr.employee'].search([('id', '=', xingzhengzhuli)]).work_email
            self.send_mail(u"【提醒】{0}于{1}提交的费用报销单已被接口会计驳回，现在等待您的审批!".format(current_expense_model.create_uid.name,
                                                                          current_expense_model.create_date[:10]),
                           u"%s提交的费用报销单已被主管驳回，现在等待您的审批。" % current_expense_model.create_uid.name, email_to=emailto)

            current_expense_model.signal_workflow('btn_refuse_jiekoukuaiji_to_xingzheng')

        elif self.state=="zhuguan" and current_expense_model.state=="jiekoukuaiji":
            message = u"驳回，状态：接口会计审批---->主管审批"
            current_expense_model.message_post(body=message + u"，审批意见:" + self.liyou)

            if create_hr_id == zhuguan_id_hr_employee:
                if parentdepartmentid != False:  # 二级主管提交到一级主管
                    re_currentauditperson = self.get_zhuguanfromdepid(parentdepartmentid)
                else:  # 一级主管提交到总裁
                    re_currentauditperson = self.env['dtdream.expense.president'].search(
                        [('type', '=', 'zongcai')]).name.id
            else:  # 员工提交到二级主管
                re_currentauditperson = zhuguan_id_hr_employee

            emailto = self.env['hr.employee'].search([('id', '=', re_currentauditperson)]).work_email

            self.send_mail(u"【提醒】{0}于{1}提交的费用报销单已被接口会计驳回，现在等待您的审批!".format(current_expense_model.create_uid.name,
                                                                          current_expense_model.create_date[:10]),
                           u"%s提交的费用报销单已被接口会计驳回，现在等待您的审批。" % current_expense_model.create_uid.name,
                           email_to=emailto)

            current_expense_model.signal_workflow('btn_refuse_jiekoukuaiji_to_zhuguan')

        elif self.state == "quanqianren" and current_expense_model.state == "jiekoukuaiji":
            message = u"驳回，状态：接口会计审批---->权签人审批"
            current_expense_model.message_post(body=message + u"，审批意见:" + self.liyou)

            # 判断该单审批主管
            if create_hr_id == zhuguan_id_hr_employee:
                if parentdepartmentid != False:  # 二级主管提交到一级主管


                    zhuguanauditperson = self.get_zhuguanfromdepid(parentdepartmentid)


                else:  # 一级主管提交到总裁

                    zhuguanauditperson = self.env['dtdream.expense.president'].search(
                        [('type', '=', 'zongcai')]).name.id


            else:  # 员工提交到二级主管

                zhuguanauditperson = zhuguan_id_hr_employee




            if zhuguanauditperson == zongcai_hr_employee_id:  # 主管审批环节，如果处理人是总裁的话则直接到接口会计


                re_currentauditperson = jiekoukuaiji

            elif zhuguanauditperson == no_two_auditor_hr_employee:  # 如果是一级主管到接口会计

                re_currentauditperson = jiekoukuaiji

            elif zhuguanauditperson == no_one_auditor_hr_employee:

                re_currentauditperson = no_two_auditor_hr_employee

            else:

                re_currentauditperson = no_one_auditor_hr_employee

            emailto = self.env['hr.employee'].search([('id', '=', re_currentauditperson)]).work_email
            self.send_mail(u"【提醒】{0}于{1}提交的费用报销单已被接口会计驳回，现在等待您的审批!".format(current_expense_model.create_uid.name,
                                                                           current_expense_model.create_date[:10]),
                           u"%s提交的费用报销单已被接口会计驳回，现在等待您的审批。" % current_expense_model.create_uid.name,
                           email_to=emailto)
            current_expense_model.signal_workflow('btn_refuse_jiekoukuaiji_to_quanqianren')






class ExpenseWizard(models.TransientModel):
    _name = 'dtdream.expense.agree.wizard'

    advice = fields.Text(string="审批意见",required=True)

    # 发送邮件公共方法
    def get_base_url(self, cr, uid):
        base_url = self.pool.get('ir.config_parameter').get_param(cr, uid, 'web.base.url')
        return base_url

    def get_mail_server_name(self):
        return self.env['ir.mail_server'].search([], limit=1).smtp_user

    def send_mail(self, subject, content, email_to, email_cc="", wait=False):
        base_url = self.get_base_url()
        link = '/web#id=%s&view_type=form&model=dtdream.expense.report' % self.env['dtdream.expense.report'].browse(
            self._context['active_id']).id
        url = base_url + link
        email_to = email_to
        email_cc = "" if email_cc == email_to else email_cc
        subject = subject
        if wait:
            appellation = u'{0},您好：'.format(self.name.user_id.name)
        else:
            # appellation = u'{0},您好：'.format(self.currentauditperson.user_id.name)
            appellation = u'您好：'
        content = content
        self.env['mail.mail'].create({
            'body_html': u'''<p>%s</p>
                                    <p>%s</p>
                                    <a href="%s">点击链接进入查看</a></p>
                                    <p>dodo</p>
                                    <p>万千业务，简单有do</p>
                                    <p>%s</p>''' % (appellation, content, url,
                                                    self.env['dtdream.expense.report'].browse(
                                                        self._context['active_id']).write_date[:10]),
            'subject': '%s' % subject,
            'email_from': self.get_mail_server_name(),
            'email_to': '%s' % email_to,
            'auto_delete': False,
        }).send()

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
    @api.one
    def btn_confirm(self):
        current_expense_model = self.env['dtdream.expense.report'].browse(self._context['active_id'])

        if current_expense_model.state=="xingzheng":
            if current_expense_model.showcuiqian != '1':
                raise exceptions.ValidationError('请先确认签收纸件！')
            try:
                zongcai_hr_employee_id = self.get_company_president()  # 总裁在hr.employee中的id
                zhuguan_id_hr_employee = self.get_zhuguan(current_expense_model.create_uid.id)  # 主管hr.employee中id
                no_one_auditor_hr_employee = self.get_no_one_auditor(current_expense_model.create_uid.id)  # 第一审批人在hr.employee中id
                no_one_auditor_amount = self.get_no_one_auditor_amount(current_expense_model.create_uid.id)  # 第一审批人上限金额
                no_two_auditor_hr_employee = self.get_no_two_auditor(current_expense_model.create_uid.id)  # 第二审批人在hr.employee中id
                no_two_auditor_amount = self.get_no_two_auditor_amount(current_expense_model.create_uid.id)  # 第二审批人上限金额
                jiekoukuaiji = self.get_jiekoukuaiji(current_expense_model.create_uid.id)  # 接口会计
                # currentauditperson = self.currentauditperson.id  # 本单当前处理人
                zhuguan_login = self.get_employee_login(zhuguan_id_hr_employee)
                parentdepartmentid = self.get_employee_parentdepartmentid(zhuguan_login)  # 上级部门是否为空，为空则为一级，否则为二级
                create_hr_id = self.get_employee_id(current_expense_model.create_uid.id)  # 本单创建人hr.employee中id
            except Exception:

                raise exceptions.ValidationError("参数配置不全，请联系管理员！")

            re_currentauditperson = ''
            message = u"同意，状态：行政助理审批---->主管审批"
            emailto =''


            if create_hr_id == zhuguan_id_hr_employee:
                if parentdepartmentid != False:  # 二级主管提交到一级主管
                    re_currentauditperson = self.get_zhuguanfromdepid(parentdepartmentid)
                    emailto = self.env['hr.employee'].search([('id', '=', re_currentauditperson)]).work_email

                else:  # 一级主管提交到总裁
                    re_currentauditperson = self.env['dtdream.expense.president'].search([('type', '=', 'zongcai')]).name.id

                    emailto = self.env['hr.employee'].search([('id', '=', re_currentauditperson)]).work_email

            else:  # 员工提交到二级主管
                re_currentauditperson = zhuguan_id_hr_employee
                emailto = self.env['hr.employee'].search([('id', '=', re_currentauditperson)]).work_email


            self.send_mail(u"【提醒】{0}于{1}提交的费用报销单已通过行政助理审批，现在等待您的审批!".format(current_expense_model.create_uid.name,
                                                                           current_expense_model.create_date[:10]),
                           u"%s提交的费用报销单已通过行政助理审批，现在等待您的审批。" % current_expense_model.create_uid.name,
                           email_to=emailto)



        elif current_expense_model.state=="zhuguan":

            try:
                zongcai_hr_employee_id = self.get_company_president()  # 总裁在hr.employee中的id
                zhuguan_id_hr_employee = self.get_zhuguan(current_expense_model.create_uid.id)  # 主管hr.employee中id
                no_one_auditor_hr_employee = self.get_no_one_auditor(current_expense_model.create_uid.id)  # 第一审批人在hr.employee中id
                no_one_auditor_amount = self.get_no_one_auditor_amount(current_expense_model.create_uid.id)  # 第一审批人上限金额
                no_two_auditor_hr_employee = self.get_no_two_auditor(current_expense_model.create_uid.id)  # 第二审批人在hr.employee中id
                no_two_auditor_amount = self.get_no_two_auditor_amount(current_expense_model.create_uid.id)  # 第二审批人上限金额
                jiekoukuaiji = self.get_jiekoukuaiji(current_expense_model.create_uid.id)  # 接口会计
                currentauditperson = current_expense_model.currentauditperson.id  # 本单当前处理人
                currentauditperson_login = self.get_employee_login(currentauditperson)
                parentdepartmentid = self.get_employee_parentdepartmentid(currentauditperson_login)  # 上级部门是否为空，为空则为一级，否则为二级
            except Exception:
                raise exceptions.ValidationError("参数配置不全，请联系管理员！")

            re_currentauditperson = ''
            message =''
            emailto = ''

            if currentauditperson == zongcai_hr_employee_id:  # 主管审批环节，如果处理人是总裁的话则直接到接口会计
                re_currentauditperson = jiekoukuaiji
                emailto = self.env['hr.employee'].search([('id', '=', re_currentauditperson)]).work_email
                message = u"同意，状态：主管审批---->接口会计审批。"
            elif parentdepartmentid != False:  # 如果是二级主管则到第二审批人
                re_currentauditperson = no_two_auditor_hr_employee
                emailto = self.env['hr.employee'].search([('id', '=', re_currentauditperson)]).work_email
                message = u"同意，状态：主管审批---->权签人审批。"
            elif parentdepartmentid == False:  # 如果是一级主管到接口会计
                re_currentauditperson = jiekoukuaiji
                emailto = self.env['hr.employee'].search([('id', '=', re_currentauditperson)]).work_email
                message = u"同意，状态：主管审批---->接口会计审批。"


            self.send_mail(u"【提醒】{0}于{1}提交的费用报销单已通过主管审批，现在等待您的审批!".format(current_expense_model.create_uid.name,
                                                                               current_expense_model.create_date[:10]),
                               u"%s提交的费用报销单已通过主管审批，现在等待您的审批。" % current_expense_model.create_uid.name,
                               email_to=emailto)

        elif current_expense_model.state == "quanqianren":



            zongcai_hr_employee_id = self.get_company_president()  # 总裁在hr.employee中的id
            zhuguan_id_hr_employee = self.get_zhuguan(current_expense_model.create_uid.id)  # 主管hr.employee中id
            no_one_auditor_hr_employee = self.get_no_one_auditor(current_expense_model.create_uid.id)  # 第一审批人在hr.employee中id
            no_one_auditor_amount = self.get_no_one_auditor_amount(current_expense_model.create_uid.id)  # 第一审批人上限金额
            no_two_auditor_hr_employee = self.get_no_two_auditor(current_expense_model.create_uid.id)  # 第二审批人在hr.employee中id
            no_two_auditor_amount = self.get_no_two_auditor_amount(current_expense_model.create_uid.id)  # 第二审批人上限金额
            jiekoukuaiji = self.get_jiekoukuaiji(current_expense_model.create_uid.id)  # 接口会计
            zhuguan_login = self.get_employee_login(zhuguan_id_hr_employee)
            parentdepartmentid = self.get_employee_parentdepartmentid(zhuguan_login)  # 上级部门是否为空，为空则为一级，否则为二级
            create_hr_id = self.get_employee_id(current_expense_model.create_uid.id)  # 本单创建人hr.employee中id



            if current_expense_model.currentauditperson.id == zongcai_hr_employee_id and current_expense_model.state == 'quanqianren':
                re_state = 'jiekoukuaiji'
                re_currentauditperson = jiekoukuaiji
                re_currentauditperson_userid = self.get_user_id(jiekoukuaiji)

                message = u"同意，状态：总裁审批---->接口会计审批"
                pass_jiekoukuaiji = "1"


            elif current_expense_model.currentauditperson.id == no_two_auditor_hr_employee and current_expense_model.state == 'quanqianren' and current_expense_model.total_invoicevalue <= no_two_auditor_amount :  # 如果是一级主管到接口会计

                re_state = 'jiekoukuaiji'
                re_currentauditperson = jiekoukuaiji
                re_currentauditperson_userid = self.get_user_id(jiekoukuaiji)

                message = u"同意，状态：第二权签人审批---->接口会计审批"
                pass_jiekoukuaiji="1"

            elif current_expense_model.currentauditperson.id == no_two_auditor_hr_employee and current_expense_model.state == 'quanqianren' and current_expense_model.total_invoicevalue > no_two_auditor_amount :
                re_state = 'quanqianren'
                re_currentauditperson = zongcai_hr_employee_id
                re_currentauditperson_userid = self.get_user_id(zongcai_hr_employee_id)


                message = u"同意，状态：第二权签人审批---->总裁审批"
                pass_jiekoukuaiji = "0"

            elif current_expense_model.currentauditperson.id == no_one_auditor_hr_employee and current_expense_model.state == 'quanqianren' and current_expense_model.total_invoicevalue <= no_one_auditor_amount:

                re_state = 'jiekoukuaiji'
                re_currentauditperson = jiekoukuaiji
                re_currentauditperson_userid = self.get_user_id(jiekoukuaiji)

                message = u"同意，状态：第一权签人审批---->接口会计审批"
                pass_jiekoukuaiji = "1"

            elif current_expense_model.currentauditperson.id == no_one_auditor_hr_employee and current_expense_model.state == 'quanqianren' and current_expense_model.total_invoicevalue > no_one_auditor_amount:

                re_state = 'quanqianren'
                re_currentauditperson = no_two_auditor_hr_employee
                re_currentauditperson_userid = self.get_user_id(no_two_auditor_hr_employee)

                message = u"同意，状态：第一权签人审批---->第二权签人审批"
                pass_jiekoukuaiji = "0"


            else:

                re_state = 'quanqianren'
                re_currentauditperson = no_two_auditor_hr_employee
                re_currentauditperson_userid = self.get_user_id(no_two_auditor_hr_employee)

                message = u"同意，状态：第一权签人审批---->第二权签人审批"
                pass_jiekoukuaiji = "0"



                # 更新报销单
            current_expense_model.write({"hasauditor": [(4, current_expense_model.currentauditperson.id)]})
            current_expense_model.write({'state': re_state, 'currentauditperson': re_currentauditperson,
                        'currentauditperson_userid': re_currentauditperson_userid,'can_pass_jiekoukuaiji':pass_jiekoukuaiji})




            emailto = self.env['hr.employee'].search([('id', '=', re_currentauditperson)]).work_email


            self.send_mail(u"【提醒】{0}于{1}提交的费用报销单已通过权签人审批，现在等待您的审批!".format(current_expense_model.create_uid.name,
                                                                          current_expense_model.create_date[:10]),
                           u"%s提交的费用报销单已通过权签人审批，现在等待您的审批。" % current_expense_model.create_uid.name,
                           email_to=emailto)



        elif current_expense_model.state == "jiekoukuaiji":
            if current_expense_model.showcuiqian != '2':
                raise Warning(u'请先确认签收纸件！')

            message = u"同意，状态：接口会计审批---->待付款"
            # 给出纳会计发送邮件
            hr_employee_login = self.env['res.users'].search([('id', '=', current_expense_model.create_uid.id)]).login
            depid = self.env['hr.employee'].search([('login', '=', hr_employee_login)]).department_id[0].id
            assistant_ids = self.env['hr.department'].search([('id', '=', depid)]).chunakuaiji[0].work_email
            self.send_mail(u"【提醒】{0}于{1}提交的费用报销单已通过接口会计审批，现在等待您的审批!".format(current_expense_model.create_uid.name,
                                                                           current_expense_model.create_date[:10]),
                           u"%s提交的费用报销单已通过接口会计审批，现在等待您的审批。" % current_expense_model.create_uid.name,
                           email_to=assistant_ids)


        current_expense_model.message_post(body=message + u"，审批意见:" + self.advice)

        current_expense_model.signal_workflow('btn_agree')

