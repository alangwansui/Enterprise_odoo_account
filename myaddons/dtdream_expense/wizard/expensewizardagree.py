# -*- coding: utf-8 -*-

from openerp import models, fields, api,exceptions
from datetime import datetime
from openerp .exceptions import ValidationError,Warning
import time



class ExpenseWizard(models.TransientModel):
    _name = 'dtdream.expense.agree.wizard'

    advice = fields.Text(string="审批意见")

    # 发送邮件公共方法
    def get_base_url(self, cr, uid):
        base_url = self.pool.get('ir.config_parameter').get_param(cr, uid, 'web.base.url')
        return base_url

    def get_mail_server_name(self):
        return self.env['ir.mail_server'].search([], limit=1).smtp_user

    def send_dingding_msg(self, report, employee_id, content=None, model="receipts", action="view"):
        from openerp.dtdream.dingding.message import send as ding

        # if content == None:
        #     content = u"%s提交了费用报销单,等待您的审批!" % report.create_uid.name

        user_id = self.env['hr.employee'].search([('id', '=', employee_id)]).user_id

        import redis
        import openerp

        token = ""
        try:
            redis_host = openerp.tools.config['redis_host']
            redis_port = openerp.tools.config['redis_port']
            redis_pass = openerp.tools.config['redis_pass']
            r = redis.Redis(host=redis_host, password=redis_pass, port=redis_port, db=0)
            if r.get("dtdream.dingtalk.token"):
                token = r.get("dtdream.dingtalk.token")
        except Exception, e:
            print "get token from redis failed"
            pass

        agentid = self.env['ir.config_parameter'].get_param('dtdream.expense.agentId', default="")
        url = self.env['ir.config_parameter'].get_param('dtdream.expense.agentUrl', default="")
        url = "%s?model=%s&action=%s&id=%d" % (url, model, action, report.id)

        text = u"数梦报销"
        oa = {
            "message_url": url,
            "head": {
                "bgcolor": "51bcec",
                "text": text
            },
            "body": {
                "form": [
                    {"key": u"具体信息如下:", "value": ""},
                    {"key": u"单据号:", "value": report.name},
                    {"key": u"报销人:", "value": report.create_uid.name},
                    {"key": u"创建时间:", "value": report.create_date[:10]},
                    {"key": u"报销金额:", "value": report.total_shibaoamount}
                ],
                "content": content
            }
        }

        dd_id = self.env['res.users'].search([('id', '=', user_id.id)]).dd_userid
        try:
            print "Begin to send dingding message to %s" % (dd_id)
            ding(token, dd_id, '', 'oa', oa, agentid)
            print "End to send dingding message to %s" % (dd_id)
        except Exception,e:
            print "Only support operate in ding ding"
            pass

    def send_mail(self, subject, content, email_to, email_cc="", wait=False):
        base_url = self.get_base_url()
        action = self.env['ir.model.data'].search([('name','=','action_dtdream_expense_pending_jiekoukuaiji')]).res_id
        menu_id = self.env['ir.ui.menu'].search([('name','=','费用报销')]).id
        link = '/web#id=%s&view_type=form&model=dtdream.expense.report&action=%s&menu_id=%s' % (self.env['dtdream.expense.report'].browse(
            self._context['active_id']).id,action,menu_id)
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

    @api.one
    def btn_confirm(self):
        current_expense_model = self.env['dtdream.expense.report'].browse(self._context['active_id'])

        create_hr_id = self.get_employee_id(current_expense_model.create_uid.id)
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
                if parentdepartmentid != False:
                    if create_hr_id == no_two_auditor_hr_employee and current_expense_model.total_invoicevalue > no_two_auditor_amount:
                        re_currentauditperson = zongcai_hr_employee_id
                        current_expense_model.xingzheng2who = "2"
                        message = u"同意，状态：行政助理审批---->总裁审批"

                    elif create_hr_id == no_one_auditor_hr_employee and current_expense_model.total_invoicevalue > no_one_auditor_amount:
                        # 第一审批人重复，且超出第一审批人金额，进入第二权签人审批
                        re_currentauditperson = no_two_auditor_hr_employee
                        current_expense_model.xingzheng2who = "2"
                        message = u"同意，状态：行政助理审批---->第二权签人审批"
                    elif (create_hr_id == no_two_auditor_hr_employee and current_expense_model.total_invoicevalue <= no_two_auditor_amount) or \
                            (create_hr_id == no_one_auditor_hr_employee and current_expense_model.total_invoicevalue <= no_one_auditor_amount):
                        re_currentauditperson = jiekoukuaiji
                        current_expense_model.xingzheng2who = "3"
                        message = u"同意，状态：行政助理审批---->接口会计审批"
                    else:
                        # 未重复的到第一权签人审批
                        re_currentauditperson = no_one_auditor_hr_employee
                        current_expense_model.xingzheng2who = "2"
                        message = u"同意，状态：行政助理审批---->第一权签人审批"

                    emailto = self.env['hr.employee'].search([('id', '=', re_currentauditperson)]).work_email

                else:  # 一级主管提交到总裁
                    current_expense_model.xingzheng2who = "1"
                    re_currentauditperson = self.env['dtdream.expense.president'].search([('type', '=', 'zongcai')]).name.id

                    emailto = self.env['hr.employee'].search([('id', '=', re_currentauditperson)]).work_email

            else:  # 员工提交到二级主管
                current_expense_model.xingzheng2who = "1"
                re_currentauditperson = zhuguan_id_hr_employee
                emailto = self.env['hr.employee'].search([('id', '=', re_currentauditperson)]).work_email


            self.send_mail(u"【提醒】{0}于{1}提交的费用报销单已通过行政助理审批，现在等待您的审批!".format(current_expense_model.create_uid.name,
                                                                           current_expense_model.create_date[:10]),
                           u"%s提交的费用报销单已通过行政助理审批，现在等待您的审批。" % current_expense_model.create_uid.name,
                           email_to=emailto)

            content=u"【提醒】{0}于{1}提交的费用报销单已通过行政助理审批!".format(current_expense_model.create_uid.name,
                                                                           current_expense_model.create_date[:10])
            employee_id = create_hr_id

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


            if currentauditperson == zongcai_hr_employee_id:   #主管审批环节，如果处理人是总裁的话则直接到接口会计
                message = u"同意，状态：主管审批---->接口会计审批"
                zhuguan_quanqian_jiekou = "2"
                re_currentauditperson = jiekoukuaiji
            elif currentauditperson == no_two_auditor_hr_employee and current_expense_model.total_invoicevalue<=no_two_auditor_amount:
                message = u"同意，状态：主管审批---->接口会计审批"
                zhuguan_quanqian_jiekou = "2"
                re_currentauditperson = jiekoukuaiji
            elif currentauditperson == no_two_auditor_hr_employee and current_expense_model.total_invoicevalue > no_two_auditor_amount:
                message = u"同意，状态：主管审批---->总裁审批"
                zhuguan_quanqian_jiekou = "1"
                re_currentauditperson = zongcai_hr_employee_id
            elif currentauditperson == no_one_auditor_hr_employee and current_expense_model.total_invoicevalue<=no_one_auditor_amount:
                message = u"同意，状态：主管审批---->接口会计审批"
                zhuguan_quanqian_jiekou = "2"
                re_currentauditperson = jiekoukuaiji
            elif currentauditperson == no_one_auditor_hr_employee and current_expense_model.total_invoicevalue > no_one_auditor_amount:
                message = u"同意，状态：主管审批---->第二权签人审批"
                zhuguan_quanqian_jiekou = "1"
                re_currentauditperson = no_two_auditor_hr_employee
            else:
                message = u"同意，状态：主管审批---->第一权签人审批"
                zhuguan_quanqian_jiekou = "1"
                re_currentauditperson = no_one_auditor_hr_employee

            emailto = self.env['hr.employee'].search([('id', '=', re_currentauditperson)]).work_email
            self.send_mail(u"【提醒】{0}于{1}提交的费用报销单已通过主管审批，现在等待您的审批!".format(current_expense_model.create_uid.name,
                                                                               current_expense_model.create_date[:10]),
                               u"%s提交的费用报销单已通过主管审批，现在等待您的审批。" % current_expense_model.create_uid.name,
                               email_to=emailto)
            current_expense_model.write({'zhuguan_quanqian_jiekoukuaiji': zhuguan_quanqian_jiekou})

            content = u"【提醒】{0}于{1}提交的费用报销单已通过主管审批!".format(current_expense_model.create_uid.name,
                                                                               current_expense_model.create_date[:10])
            employee_id = create_hr_id

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

            content = u"【提醒】{0}于{1}提交的费用报销单已通过权签人审批!".format(current_expense_model.create_uid.name,
                                                                          current_expense_model.create_date[:10])
            employee_id=create_hr_id

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

            content = u"【提醒】{0}于{1}提交的费用报销单已通过接口会计审批!".format(current_expense_model.create_uid.name,
                                                                           current_expense_model.create_date[:10])
            if current_expense_model.total_koujianamount > 0:
                if self.advice and self.advice.strip() != "":
                    content = u"【提醒】{0}于{1}提交的费用报销单已通过接口会计审批，发生{2}元的扣款!审批意见:{3}".format(
                              current_expense_model.create_uid.name,
                              current_expense_model.create_date[:10],
                              current_expense_model.total_koujianamount,
                              self.advice.strip())
                else:
                    content = u"【提醒】{0}于{1}提交的费用报销单已通过接口会计审批，发生{2}元的扣款!".format(
                              current_expense_model.create_uid.name,
                              current_expense_model.create_date[:10],
                              current_expense_model.total_koujianamount)

            employee_id=create_hr_id


        self.send_dingding_msg(current_expense_model, employee_id, content=content)

        # print '-------->',self.advice
        auditadvice=''
        if self.advice == False:
            auditadvice = ''
        else:
            auditadvice  =self.advice
        current_expense_model.message_post(body=message + u"，审批意见:" + auditadvice)

        current_expense_model.signal_workflow('btn_agree')
