# -*- coding: utf-8 -*-
from openerp import http
from openerp.http import request
import logging,openerp

from openerp.dtdream.ldap.dtldap import DTLdap
from openerp.addons.web.controllers.utils import dtphone as DTPhone
from openerp.addons.web.controllers.common.dterror import DTError as DTError
from openerp.addons.web.controllers.utils import code as DTCode
from openerp.exceptions import ValidationError

path_log_file = '/tmp/dtdream_pay.log'
logger = logging.getLogger(__name__)
file_handler = logging.FileHandler(path_log_file)
formatter = logging.Formatter('%(asctime)s:%(name)s-->%(levelname)s %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


_logger = logging.getLogger(__name__)

class DtdreamPay(http.Controller):

    @http.route('/dtdream_pay/getValidateCode', type='json', auth="user", methods=['POST'], csrf=False)
    def get_validate_code(self, **kw):
        login = request.session.login
        _logger.info("get_validate_code login: "+login)
        user = request.env["res.users"].search([('id', '=', request.session.uid)])
        if user.is_locked_pay:
            return {'code': 11005, 'message': u'您已连续5次输入错误，账号已被锁定，请明日再查询'}

        from openerp.dtdream import openerplib
        try:
            hostname = openerp.tools.config['wage_hostname']
            database = openerp.tools.config['wage_database']
            wage_login = openerp.tools.config['wage_login']
            password = openerp.tools.config['wage_password']
        except Exception, e:
            return {"code": 20000, "message": u"工资查询系统参数未配置"}

        connection = openerplib.get_connection(hostname=hostname, database=database,login=wage_login, password=password)
        remodel = connection.get_model("dtdream.verification.code")
        # request.session.uid=1
        ldapconfig = request.env['res.company.ldap'].sudo().search([])[0]
        host = ldapconfig.ldap_domain
        port = ldapconfig.ldap_port
        dn = ldapconfig.ldap_binddn
        passwd = ldapconfig.ldap_password
        base = ldapconfig.ldap_base
        cacertfile = ldapconfig.ldap_cert_file
        try:
            dtldap = DTLdap(host=host, port=port, dn=dn, passwd=passwd, base=base, cacertfile=cacertfile)
        except Exception, e:
            raise ValidationError(u'ldap连接错误,请联系管理员检查公司LDAP数据配置')
        entry = dtldap.search(login)
        if len(entry)>0:
            phone = entry[0][1]['telephoneNumber'][0]
            _logger.info("phone" + phone)
        else:
            return {'code':22000,'message':u"用户不存在域中"}
        verification_code = DTCode.generate_verification_code_num()
        d={}
        d['phone'] = phone
        d['code'] = verification_code
        d['templateCode'] = "SMS_27380183"                                      #短信模板
        print verification_code
        retval = DTPhone.send_sms_aliyun(**d)
        # retval=0
        if retval == DTPhone.ERROR_NUM_SUCCESS:
            import hashlib
            code = hashlib.sha1(d['code'].encode('utf-8')).hexdigest()
            if remodel.save_verification_code(login = login, sn =code):
                result = DTError.get_error_msg(DTError.DT_ERROR_NUM_SUCCESS)        #u"操作成功"
                result['telephone']=d['phone']
                return result
            else:
                return DTError.get_error_msg(DTError.DT_ERROR_NUM_ERROR)            #u"10007服务器内部错误"
        elif retval == DTPhone.ERROR_NUM_HTTPS_ERROR:
            return DTError.get_error_msg(DTError.DT_ERROR_NUM_HTTPS_FAILED)         #u"10005服务器内部错误，手机发送验证码http请求异常"
        elif retval == DTPhone.ERROR_NUM_SENDSMS_ERROR:
            return DTError.get_error_msg(DTError.DT_ERROR_NUM_SEND_SMS_FAILED)          # u"10006服务器内部错误，手机发送验证码失败"



    @http.route('/dtdream_pay/saveValidateCode', type='json', auth="user", methods=['POST'], csrf=False)
    def save_validate_code(self, **kw):
        login = request.session.login               #帐号
        _logger.info("save_validate_code login: " + login)
        _logger.info("save_validate_code host: " + request.httprequest.host_url)
        try:
            sn = request.jsonrequest["sn"]
            _logger.info("save_validate_code sn: " + sn)
        except Exception, e:
            sn=""
        from openerp.dtdream import openerplib
        try:
            hostname = openerp.tools.config['wage_hostname']
            database = openerp.tools.config['wage_database']
            wage_login = openerp.tools.config['wage_login']
            password = openerp.tools.config['wage_password']
        except Exception, e:
            return {"code": 20000, "message": u"工资查询系统参数未配置"}

        user = request.env["res.users"].search([('id', '=', request.session.uid)])
        if user.is_locked_pay:
            return {'code': 11005, 'message': u'您已连续5次输入错误，账号已被锁定，请明日再查询'}
        else:
            connection = openerplib.get_connection(hostname=hostname, database=database, login=wage_login, password=password)
            remodel = connection.get_model("dtdream.verification.code")
            import hashlib
            code = hashlib.sha1(sn.encode('utf-8')).hexdigest()
            result = remodel.check_verification_code(login=login,sn=code)
            em = request.env["hr.employee"].search([('user_id', '=', request.session.uid)])
            if len(em)>0:
                if em.account ==login:
                    if result['code']==10000:
                        user.sudo().write({'pay_fail_times':0})
                        result['vaCode'] = code
                        result['waterline'] = em.name+'.'+em.job_number
                    elif result['code']==10002:
                        user.sudo().write({'pay_fail_times': user.pay_fail_times+1})
                    return  result
                else:
                    return {'code': 11105, 'message': u'该用户与关联员工帐号对应不上，请联系系统管理员调整'}
            else:
                return {'code': 11105, 'message': u'该用户尚未关联员工，请联系系统管理员添加'}
