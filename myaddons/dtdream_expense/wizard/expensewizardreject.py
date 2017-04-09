# -*- coding: utf-8 -*-

from openerp import models, fields, api,exceptions,tools
from datetime import datetime
from openerp .exceptions import ValidationError,Warning
import time

import logging

_logger = logging.getLogger(__name__)


class ExpenseWizard(models.TransientModel):
    _name = 'dtdream.expense.wizard'

    def _get_states_now(self):

        context = dict(self._context or {})
        _logger.info("context:" + str(context))
        active_model = context.get('active_model', "")
        if active_model:
            active_id = context.get("active_id")
            cur_rec = self.env['dtdream.expense.report'].browse(active_id)
            zongcai = self.env['dtdream.expense.president'].search([('type', '=', 'zongcai')]).name

            if cur_rec.state == 'xingzheng':
                re = [('draft', '申请人')]
            elif cur_rec.state == 'zhuguan':
                re = [('draft', '申请人'), ('xingzheng', '行政助理')]
            elif cur_rec.state == 'quanqianren':
                re = [('draft', '申请人'), ('xingzheng', '行政助理'), ('zhuguan', '主管')]
                if cur_rec.xingzheng2who == "2":
                    re = [('draft', '申请人'), ('xingzheng', '行政助理')]
            elif cur_rec.state == 'jiekoukuaiji':
                re = [('draft', '申请人'), ('xingzheng', '行政助理'), ('zhuguan', '主管'), ('quanqianren', '权签人')]
                if cur_rec.applicant == zongcai:
                    re = [('draft', '申请人')]
                else:
                    if cur_rec.xingzheng2who == "1":
                        if cur_rec.zhuguan_quanqian_jiekoukuaiji == '2':
                            re = [('draft', '申请人'), ('xingzheng', '行政助理'), ('zhuguan', '主管')]
                    elif cur_rec.xingzheng2who == "2":
                        re = [('draft', '申请人'), ('xingzheng', '行政助理'), ('quanqianren', '权签人')]
                    elif cur_rec.xingzheng2who == "3":
                        re = [('draft', '申请人'), ('xingzheng', '行政助理')]
            elif cur_rec.state == 'daifukuan':
                re = [('draft', '申请人'), ('xingzheng', '行政助理'), ('zhuguan', '主管'), ('quanqianren', '权签人'), ('jiekoukuaiji','接口会计')]
                if cur_rec.applicant == zongcai:
                    re = [('draft', '申请人'), ('jiekoukuaiji', '接口会计')]
                else:
                    if cur_rec.xingzheng2who == "1":
                        if cur_rec.zhuguan_quanqian_jiekoukuaiji == '2':
                            re = [('draft', '申请人'), ('xingzheng', '行政助理'), ('zhuguan', '主管'), ('jiekoukuaiji','接口会计')]
                    elif cur_rec.xingzheng2who == "2":
                        re = [('draft', '申请人'), ('xingzheng', '行政助理'), ('quanqianren', '权签人'), ('jiekoukuaiji','接口会计')]
                    elif cur_rec.xingzheng2who == "3":
                        re = [('draft', '申请人'), ('xingzheng', '行政助理'), ('jiekoukuaiji', '接口会计')]
            return re

    state = fields.Selection(selection=_get_states_now, string="节点", required=True)

    liyou = fields.Text("驳回原因", required=True)

    @api.one
    def btn_confirm(self):
        current_expense_model = self.env['dtdream.expense.report'].browse(self._context['active_id'])
        current_login_employee = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)])
        current_expense_model.write({'hasauditor': [(4, current_login_employee.id)]})
        if len(current_expense_model.current_handler) > 1:
            for people in current_expense_model.current_handler:
                if people != current_login_employee:
                    current_expense_model.send_mail(
                            u"%s于%s提交的费用报销单,已被%s驳回!"%(
                                current_expense_model.applicant.name,
                                current_expense_model.create_date[:10],
                                current_login_employee.nick_name
                            ),
                            u"%s提交的费用报销单,等待您的审批!" % current_expense_model.applicant.name,
                            email_to=people.work_email
                    )

        if self.state == "draft" and current_expense_model.state == "xingzheng":
            message = u"驳回，状态：行政助理审批---->草稿"
            current_expense_model.message_post(body=message + u"，审批意见:" + self.liyou)
            current_expense_model.signal_workflow('btn_refuse_xingzheng_to_draft')

        elif self.state == "draft" and current_expense_model.state == "zhuguan":
            message = u"驳回，状态：主管审批---->草稿"
            current_expense_model.message_post(body=message + u"，审批意见:" + self.liyou)
            current_expense_model.signal_workflow('btn_refuse_zhuguan_to_draft')

        elif self.state == "xingzheng" and current_expense_model.state == "zhuguan":
            message = u"驳回，状态：主管审批---->行政助理审批"
            current_expense_model.message_post(body=message + u"，审批意见:" + self.liyou)
            current_expense_model.signal_workflow('btn_refuse_zhuguan_to_xingzheng')

        elif self.state == "draft" and current_expense_model.state == "quanqianren":
            message = u"驳回，状态：权签人审批---->草稿"
            current_expense_model.message_post(body=message + u"，审批意见:" + self.liyou)
            current_expense_model.signal_workflow('btn_refuse_quanqianren_to_draft')

        elif self.state == "xingzheng" and current_expense_model.state == "quanqianren":
            message = u"驳回，状态：权签人审批---->行政助理审批。"
            current_expense_model.message_post(body=message + u"，审批意见:" + self.liyou)
            current_expense_model.signal_workflow('btn_refuse_quanqianren_to_xingzheng')

        elif self.state == "zhuguan" and current_expense_model.state == "quanqianren":
            message = u"驳回，状态：权签人审批---->主管审批"
            current_expense_model.message_post(body=message + u"，审批意见:" + self.liyou)
            current_expense_model.signal_workflow('btn_refuse_quanqianren_to_zhuguan')

        elif self.state == "draft" and current_expense_model.state == "jiekoukuaiji":
            message = u"驳回，状态：接口会计审批---->草稿"
            current_expense_model.message_post(body=message + u"，审批意见:" + self.liyou)
            current_expense_model.signal_workflow('btn_refuse_jiekoukuaiji_to_draft')

        elif self.state == "xingzheng" and current_expense_model.state == "jiekoukuaiji":
            message = u"驳回，状态：接口会计审批---->行政助理审批"
            current_expense_model.message_post(body=message + u"，审批意见:" + self.liyou)
            current_expense_model.signal_workflow('btn_refuse_jiekoukuaiji_to_xingzheng')

        elif self.state == "zhuguan" and current_expense_model.state == "jiekoukuaiji":
            message = u"驳回，状态：接口会计审批---->主管审批"
            current_expense_model.message_post(body=message + u"，审批意见:" + self.liyou)
            current_expense_model.signal_workflow('btn_refuse_jiekoukuaiji_to_zhuguan')

        elif self.state == "quanqianren" and current_expense_model.state == "jiekoukuaiji":
            message = u"驳回，状态：接口会计审批---->权签人审批"
            current_expense_model.message_post(body=message + u"，审批意见:" + self.liyou)
            current_expense_model.signal_workflow('btn_refuse_jiekoukuaiji_to_quanqianren')

        elif self.state == "draft" and current_expense_model.state == "daifukuan":
            message = u"驳回，状态：待付款---->草稿"
            current_expense_model.message_post(body=message + u"，审批意见:" + self.liyou)
            current_expense_model.signal_workflow('btn_refuse_daifukuan_to_draft')

        elif self.state == "xingzheng" and current_expense_model.state == "daifukuan":
            message = u"驳回，状态：待付款---->行政助理审批"
            current_expense_model.message_post(body=message + u"，审批意见:" + self.liyou)
            current_expense_model.signal_workflow('btn_refuse_daifukuan_to_xingzheng')

        elif self.state == "zhuguan" and current_expense_model.state == "daifukuan":
            message = u"驳回，状态：待付款---->主管审批"
            current_expense_model.message_post(body=message + u"，审批意见:" + self.liyou)
            current_expense_model.signal_workflow('btn_refuse_daifukuan_to_zhuguan')

        elif self.state == "quanqianren" and current_expense_model.state == "daifukuan":
            message = u"驳回，状态：待付款---->权签人审批"
            current_expense_model.message_post(body=message + u"，审批意见:" + self.liyou)
            current_expense_model.signal_workflow('btn_refuse_daifukuan_to_quanqianren')

        elif self.state == "jiekoukuaiji" and current_expense_model.state == "daifukuan":
            message = u"驳回，状态：待付款---->接口会计审批"
            current_expense_model.message_post(body=message + u"，审批意见:" + self.liyou)
            current_expense_model.signal_workflow('btn_refuse_daifukuan_to_jiekoukuaiji')


