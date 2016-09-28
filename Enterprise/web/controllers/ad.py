# -*- coding: utf-8 -*-
import datetime
import tempfile
import os
from utils.dtldap import DTLDAP
from utils.dtldap import DTLDAPPError
import utils.dtmail as DTMail
import utils.code as DTCode
import utils.dtphone as DTPhone

from common.dterror import DTError
import openerp


class DTAD(object):
    TYPE_PHONE = "phone"
    TYPE_MAIL = "mail"

    def resetPasswd(self, **kw):

        """
        reset password

        :param kw:
        :return:

        kw = {
        'login':''
        'sn':''
        'passwd':''
        'passwd2':''
        'db_name':''
        'uid':''
        }
        """

        if kw['passwd'] != kw['passwd2'] :
            return DTError.get_error_msg(DTError.DT_ERROR_NUM_INVALID_RESET_PARAM_PASS)

        if self._check_passwd(kw['passwd']):
            return DTError.get_error_msg(DTError.DT_ERROR_NUM_INVALID_RESET_PARAM_PASS_REG)

        if self._is_verifycode_invalid(kw['login'], kw['sn']):
            return DTError.get_error_msg(DTError.DT_ERROR_NUM_RESET_CODE_INVALID)

        if self._is_verifycode_expiration(kw['login']):
            return DTError.get_error_msg(DTError.DT_ERROR_NUM_RESET_CODE_EXPIRATION)

        try:
            ldap_domain = openerp.tools.config['ldap_domain']
            ldap_cert_file = openerp.tools.config['ldap_cert_file']
            ldap_ssl = True
        except Exception,e:
            ldap_ssl = False

        try:
            dt_ldap = DTLDAP(kw['db_name'], kw['login'], ldap_ssl, ldap_domain, ldap_cert_file)
            dt_ldap.reset_password(**kw)
            result = DTError.get_error_msg(DTError.DT_ERROR_NUM_SUCCESS)
        except DTLDAPPError, e:
            if e.value == DTLDAPPError.ERROR_NUM_LDAP_ERROR:
                return DTError.get_error_msg(DTError.DT_ERROR_NUM_LDAP_ERROR)
            elif e.value == DTLDAPPError.ERROR_NUM_LDAP_BIND_FAILED:
                return DTError.get_error_msg(DTError.DT_ERROR_NUM_LDAP_BIND_FAILED)
            elif e.value == DTLDAPPError.ERROR_NUM_LDAP_USER_IS_NOT_EXIST:
                return DTError.get_error_msg(DTError.DT_ERROR_NUM_LDAP_USER_IS_NOT_EXIST)
            elif e.value == DTLDAPPError.ERROR_NUM_LDAP_MODIFY_PASSWORD_FAILED:
                return DTError.get_error_msg(DTError.DT_ERROR_NUM_LDAP_MODIFY_PASSWORD_FAILED)
        finally:
            if vars().has_key('dt_ldap') and dt_ldap:
                dt_ldap.unbind()

        return result

    def send_msg(self, t=None, **kw):

        login = kw['login']
        db = kw['db_name']
        try:
            ldap_util = DTLDAP(db, login)
            user = ldap_util.query_user(login)
        except DTLDAPPError, e:
            if e.value == DTLDAPPError.ERROR_NUM_LDAP_ERROR:
                return DTError.get_error_msg(DTError.DT_ERROR_NUM_LDAP_ERROR)
            elif e.value == DTLDAPPError.ERROR_NUM_LDAP_BIND_FAILED:
                return DTError.get_error_msg(DTError.DT_ERROR_NUM_LDAP_BIND_FAILED)
            elif e.value == DTLDAPPError.ERROR_NUM_LDAP_USER_IS_NOT_EXIST:
                return DTError.get_error_msg(DTError.DT_ERROR_NUM_LDAP_USER_IS_NOT_EXIST)
        finally:
            if vars().has_key('ldap_util') and ldap_util:
                ldap_util.unbind()

        if user is None:
            return DTError.get_error_msg(DTError.DT_ERROR_NUM_LDAP_USER_IS_NOT_EXIST)

        try:
            timeout = openerp.tools.config['timeout']
        except Exception, e:
            timeout = 180

        if t == self.TYPE_MAIL:
            email = kw['mail']
            flag = False
            if user:
                for m in user[0][1]['mail']:
                    if m == email:
                        kw['display_name'] = user[0][1]['displayName'][0]
                        flag = True
                        break
            if flag:
                d = self._build_mail_msg(**kw)
                if d:
                    retval = DTMail.send_mail(**d)
                    if retval == DTMail.ERROR_NUM_SUCCESS:
                        if self._save_verifycode_and_date(login, d['code']):
                            result = DTError.get_error_msg(DTError.DT_ERROR_NUM_SUCCESS)
                            result['timeout'] = timeout
                            return result
                        else:
                            return DTError.get_error_msg(DTError.DT_ERROR_NUM_ERROR)

                    elif retval == DTMail.ERROR_NUM_REGISTRY_ERROR:
                        return DTError.get_error_msg(DTError.DT_ERROR_NUM_REGISTRY_MAIL_FAILED)

                    elif retval == DTMail.ERROR_NUM_SENDMAIL_ERROR:
                        return DTError.get_error_msg(DTError.DT_ERROR_NUM_SEND_MAIL_FAILED)
                else:
                    return DTError.get_error_msg(DTError.DT_ERROR_NUM_ERROR)
            else:
                return DTError.get_error_msg(DTError.DT_ERROR_NUM_INVALID_MAIL_PARM)

        elif t == self.TYPE_PHONE:
            phone = kw['phone']
            flag = False
            if user:
                for p in user[0][1]['telephoneNumber']:
                    if p == phone:
                        kw['display_name'] = user[0][1]['displayName'][0]
                        flag = True
                        break
                if flag:
                    d = self._build_phone_msg(**kw)
                    if d:
                        retval = DTPhone.send_ms(**d)
                        if retval == DTPhone.ERROR_NUM_SUCCESS:
                            if self._save_verifycode_and_date(login, d['code']):
                                result = DTError.get_error_msg(DTError.DT_ERROR_NUM_SUCCESS)
                                result['timeout'] = timeout
                                return result
                            else:
                                return DTError.get_error_msg(DTError.DT_ERROR_NUM_ERROR)

                        elif retval == DTPhone.ERROR_NUM_HTTPS_ERROR:
                            return DTError.get_error_msg(DTError.DT_ERROR_NUM_HTTPS_FAILED)

                        elif retval == DTPhone.ERROR_NUM_SENDSMS_ERROR:
                            return DTError.get_error_msg(DTError.DT_ERROR_NUM_SEND_SMS_FAILED)
                    else:
                        return DTError.get_error_msg(DTError.DT_ERROR_NUM_ERROR)

                else:
                    return DTError.get_error_msg(DTError.DT_ERROR_NUM_INVALID_PHONE_PARM)

        return DTError.get_error_msg(DTError.DT_ERROR_NUM_ERROR)

        # return result
    def _build_phone_msg(self, **kw):

        try:
            d = {}
            d['phone'] = kw['phone']
            d['display_name'] = kw['display_name']
            d['url'] = openerp.tools.config['dayu_url']
            d['key'] = openerp.tools.config['dayu_key']
            d['secret'] = openerp.tools.config['dayu_secret']
            d['code'] = DTCode.generate_verification_code()
        except Exception,e:
            d = {}
        return d

    def _build_mail_msg(self, **kw):

        try:
            d = {}
            d['uid'] = kw['uid']
            d['login'] = kw['login']
            d['display_name'] = kw['display_name']
            d['db_name'] = kw['db_name']
            d['mail_to'] = kw['mail']
            d['mail_from'] = openerp.tools.config['email_from']
            d['code'] = DTCode.generate_verification_code()
        except Exception, e:
            d = {}

        return d

    def _save_verifycode_and_date(self, login, code):

        import datetime
        import tempfile
        import os

        try:
            date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            tmp = tempfile.gettempdir()
            datefile = os.path.join(tmp, login+'.date')
            with open(datefile, 'w') as f:
                f.write(date)

            codefile = os.path.join(tmp, login + '.code')
            with open(codefile, 'w') as f:
                f.write(code)
        except Exception, e:
            return False

        return True

    def _is_verifycode_expiration(self, login, timeout=180):
        tmp = tempfile.gettempdir()
        datefile = os.path.join(tmp, login + '.date')
        try:
            with open(datefile, 'r') as f:
                sss = f.readline()
                timeStart = datetime.datetime.strptime(sss, '%Y-%m-%d %H:%M:%S')
                timeEnd = datetime.datetime.now()
                if timeEnd.__sub__(timeStart).seconds > timeout :
                    return True
        except Exception, e:
            return True

        return False

    def _is_verifycode_invalid(self,login, code):
        tmp = tempfile.gettempdir()
        codefile = os.path.join(tmp, login + '.code')
        try:
            with open(codefile, 'r') as f:
                verify = f.readline()
                if code == verify:
                    return False
        except Exception, e:
            return True

        return False

    def _check_passwd(self, passwd):
        import re
        result = re.match(
            r'^(?![0-9_]+$)(?![a-z_]+$)(?![A-Z_]+$)(?![\W_]+$)(?![0-9a-z]+$)(?![A-Za-z]+$)(?![\Wa-z]+$)(?![0-9A-Z]+$)(?![\WA-Z]+$)(?![0-9\W]+$)[\w\W]{8,}$',
            passwd)
        if result:
            return False
        return True

