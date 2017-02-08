# -*- coding: utf-8 -*-

import openerp
from openerp.addons.web.http import Controller, route, request
from openerp.tools import html_escape
import json
from openerp.addons.web.controllers.main import _serialize_exception
from openerp.exceptions import ValidationError
from werkzeug import exceptions


class ReportController_extend(openerp.addons.report.controllers.main.ReportController):
    @route(['/report/download'], type='http', auth="user")
    def report_download(self, data, token):
        if 'con_dtdream_expense_report_print' in data:
            id = data.split('/report/pdf/')[1].split('?')[0].split('/')[1]
            expense = request.env['dtdream.expense.report'].search([('id','=',int(id))])
            values = request.params.copy()
            if expense.state == 'draft':
                error = {
                'code': 200,
                'message': "打印错误！",
                'data': {
                    'debug':'草稿状态的报销单不能打印！'

                }
            }
                return request.make_response(html_escape(json.dumps(error)))
        return super(ReportController_extend,self).report_download(data, token)