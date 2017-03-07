# -*- coding: utf-8 -*-
from openerp import http, fields
from openerp.http import request
import logging
import requests
import openerp
# import odoo.Enterprise.web.controllers.utils.code as DTCode
# import odoo.Enterprise.web.controllers.dtphone as DTPhone
_logger = logging.getLogger(__name__)

class DtdreamWage(openerp.http.Controller):

    @http.route('/dtdream_wage/getValidateCode', type='http', auth="none", methods=['GET'], csrf=False)
    def get_validate_code(self, **kw):
        print 111111111111111111
        try:
            login = kw['login']
        except Exception,e:
            return {'code':1}
        # try:
        #     timeout = openerp.tools.config['timeout']
        # except Exception, e:
        #     timeout = 180
        # phone = "18768122019"
        # verification_code = DTCode.generate_verification_code()
        # registry = openerp.modules.registry.Registry("0829")
        # with registry.cursor() as cr:
        #     cr.execute(
        #         "INSERT INTO dtdream_verification_code (login,key,time) VALUES (%s, %s, (now() at time zone 'UTC'))", \
        #         (login, verification_code))
        # d={}
        # d['phone'] = phone
        # d['code'] = verification_code
        # # retval = DTPhone.send_sms_aliyun(**d)
        # retval=0
        # if retval == DTPhone.ERROR_NUM_SUCCESS:
        #     if save_verifycode_and_date(login, d['code']):
        #         result = DTError.get_error_msg(DTError.DT_ERROR_NUM_SUCCESS)
        #         result['timeout'] = timeout
        #         return result
        #     else:
        #         return DTError.get_error_msg(DTError.DT_ERROR_NUM_ERROR)
        # elif retval == DTPhone.ERROR_NUM_HTTPS_ERROR:
        #     return DTError.get_error_msg(DTError.DT_ERROR_NUM_HTTPS_FAILED)
        # elif retval == DTPhone.ERROR_NUM_SENDSMS_ERROR:
        #     return DTError.get_error_msg(DTError.DT_ERROR_NUM_SEND_SMS_FAILED)

    @http.route('/dtdream_wage/saveValidateCode', type='json', auth="none", methods=['POST'], csrf=True)
    def save_validate_code(self, **kw):
        # try:
        #     login = request.jsonrequest['login']
        #     sn = request.jsonrequest['sn']
        # except Exception, e:
        #     return {"code": 1, "error": u"错误"}

        # checkresult = check_validate_code(login,sn)
        # if checkresult:
        #     return {"code": 0, "message": u"验证正确"}
        return {"code": 0, "error": u"错误"}

