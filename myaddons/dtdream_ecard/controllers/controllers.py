# -*- coding: utf-8 -*-
import openerp
from openerp import http, exceptions

class DtdreamEcard(http.Controller):

    @http.route('/dtdream_ecard/employee', type='json', auth="none", methods=['POST'], csrf=False)
    def index(self, **kw):

        if http.request.jsonrequest['key'] != "wAiZidtXG7iZJoOY8":
            raise exceptions.ValidationError("ERROR AUTH")

        ecard_url = openerp.tools.config['ecard_url']
        if http.request.httprequest.remote_addr not in ecard_url:
            return exceptions.ValidationError("ERROR Client")

        http.request.uid = openerp.SUPERUSER_ID
        sn = http.request.jsonrequest['sn']
        index = "0"
        if len(http.request.jsonrequest['sn']) > len("0335"):
            sn = http.request.jsonrequest['sn'][:len("0335")]
            index = http.request.jsonrequest['sn'][len("0335")+1:]

        emp = http.request.env['dtdream_ecard.dtdream_ecard'].search([('emp_no','=',sn),('ecard_index','=',index)])
        data={
                "content":"操作成功",
                "detail":{
                    # "cmpy":"数梦工场",
                    "mobile_phone":emp.emp_phone,
                    "empno":emp.emp_no,
                    # "idx":"601",
                    # "address":"杭州滨江白金海岸",
                    "email": emp.emp_email,
                    "name": emp.emp_name,
                    "org": emp.emp_duty,
                    # "face_idx":"-1",
                    "full_name": emp.emp_alias_name
                },
                "title":"操作结果",
                "type":"1"
        }

        return data