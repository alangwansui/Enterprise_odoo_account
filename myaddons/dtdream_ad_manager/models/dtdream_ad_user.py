# -*- coding: utf-8 -*-
from openerp import models, fields, api
from datetime import datetime
import ldap
from ldap.controls import SimplePagedResultsControl


# 域用户信息
class dtdream_ad_user(models.Model):
    _name = 'dtdream.ad.user'
    _description = u'域用户信息'

    user_name = fields.Char(string=u'用户名称')
    work = fields.Boolean(string=u'是否有效用户')
    display_name = fields.Char(string=u'显示名称')
    email = fields.Char(string=u'邮箱')
    phone = fields.Char(string=u'手机')
    expire_time = fields.Datetime(string=u'超期时间')

    @api.model
    def timing_ad_user(self):
        try:
            ldapconfig = self.env['res.company.ldap'].sudo().search([])[0]
            host = ldapconfig.ldap_domain
            port = ldapconfig.ldap_port
            dn = ldapconfig.ldap_binddn
            passwd = ldapconfig.ldap_password
            base = ldapconfig.ldap_base
            cacertfile = ldapconfig.ldap_cert_file
            ldap.set_option(ldap.OPT_PROTOCOL_VERSION, ldap.VERSION3)
            ldap.set_option(ldap.OPT_X_TLS_CACERTFILE, cacertfile)
            ldap.set_option(ldap.OPT_X_TLS, ldap.OPT_X_TLS_DEMAND)
            ldap.set_option(ldap.OPT_X_TLS_DEMAND, True)
            l = ldap.initialize('ldaps://%s:%d' % (host, port))
            l.simple_bind(dn, passwd)
        except Exception, e:
            print e
            return False
        req_ctrl = SimplePagedResultsControl(True, size=10, cookie='')
        searchreq_attrlist = ['sAMAccountName', 'displayName', 'accountExpires', 'mail', 'telephoneNumber', 'userAccountControl']
        msgid = l.search_ext(
            base,
            ldap.SCOPE_SUBTREE,
            "(&(objectCategory=person)(objectClass=user))",
            searchreq_attrlist,
            serverctrls=[] + [req_ctrl])
        while True:
            rtype, rdata, rmsgid, rctrls = l.result3(msgid)
            for r in rdata:
                user_name = r[1]['sAMAccountName'][0] if r[1].has_key('sAMAccountName') else None
                work = True if r[1].has_key('userAccountControl') and r[1]['userAccountControl'][0] == '512' else False
                display_name = r[1]['displayName'][0].decode("utf8") if r[1].has_key('displayName') else None
                email = r[1]['mail'][0] if r[1].has_key('mail') else None
                phone = r[1]['telephoneNumber'][0] if r[1].has_key('telephoneNumber') else None
                expire_time = r[1]['accountExpires'][0] if r[1].has_key('accountExpires') else None
                if expire_time:
                    expire_time = int(expire_time) / 10000000 - 11644560000
                    try:
                        expire_time = datetime.utcfromtimestamp(expire_time)
                    except Exception:
                        expire_time = None
                result = self.search([('user_name', '=', user_name)])
                if result:
                    result.write({
                        'user_name': user_name,
                        'work': work,
                        'display_name': display_name,
                        'email': email,
                        'phone': phone,
                        'expire_time': expire_time
                    })
                else:
                    self.create({
                        'user_name': user_name,
                        'work': work,
                        'display_name': display_name,
                        'email': email,
                        'phone': phone,
                        'expire_time': expire_time
                    })
            if rctrls[0].cookie:
                req_ctrl.cookie = rctrls[0].cookie
                msgid = l.search_ext(
                    base,
                    ldap.SCOPE_SUBTREE,
                    "(&(objectCategory=person)(objectClass=user))",
                    attrlist=searchreq_attrlist,
                    serverctrls=[] + [req_ctrl])
            else:
                break
        return True
