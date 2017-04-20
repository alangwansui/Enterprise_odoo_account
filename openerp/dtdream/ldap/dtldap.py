# -*- coding: utf-8 -*-
import sys

reload(sys)

sys.setdefaultencoding('utf-8')

__author__ = "g0335"

import ldap
from constant.constant import *
from exception.exception import *
class DTLdap(object):
    def __init__(self, host=LDAP_HOST, port=LDAPS_PORT, dn=LDAP_DN, passwd=LDAP_PASS, ou=LDAP_OU, base=LDAP_BASE, cacertfile=LDAP_CA_CERT_FILE):
        ldap.set_option(ldap.OPT_PROTOCOL_VERSION, ldap.VERSION3)
        ldap.set_option(ldap.OPT_X_TLS_CACERTFILE, cacertfile)
        ldap.set_option(ldap.OPT_X_TLS, ldap.OPT_X_TLS_DEMAND)
        ldap.set_option(ldap.OPT_X_TLS_DEMAND, True)

        self.__connecion = ldap.initialize('ldaps://%s:%d' % (host, port))
        self.__connecion.simple_bind_s(dn.encode('utf-8'), passwd.encode('utf-8'))
        self.__ou = ou
        self.__base = base


    def unbind(self):
        self.__connecion.unbind()


    def search(self, cn, category="Person", attr_list=None):
        '''
        search person or group in AD

        :param cn: common name in AD
        :param category:
        :param attr_list:
        :return:
        '''
        if cn is None:
            raise DTLDAPError('cn cannot be none')
        if category != "Person" and category != "Group":
            raise DTLDAPError('Error category params.')
        ldap_filter = "(&(objectCategory=%s)(sAMAccountName=%s))" % (category, cn)
        if attr_list is None:
            attr_list = ['*']
        entries = self.__connecion.search_s(self._get_base(), ldap.SCOPE_SUBTREE, ldap_filter, attr_list)
        return entries

    def _get_base(self):
        # base = "%s,%s" % (self.__ou, self.__base)
        base = "%s" % (self.__base)
        return base

    def create_user(self, user, **kw):
        '''
        create a user in AD
        :param user: the name of user, Common Name in AD
        :param kw: {
            #花名
            'displayName':'测试',
            #邮箱
            'mail':'test2017_test2017@dtdream.com',
            #部门
            'physicalDeliveryOfficeName':'信息开发部',
            #电话
            'telephoneNumber': '12312341234'
        }
        :return:
        '''
        if len(kw.items()) == 0:
            raise DTLDAPError('Error params when create a new user')

        if self.is_user_exist(user):
            return

        attrs = []
        attrs.append(('cn', [user]))
        attrs.append(('sn', [user]))
        attrs.append(('name', [user]))
        attrs.append(('sAMAccountName', [user]))
        attrs.append(('userPrincipalName', ['%s@dtdream.com' % (user)]))

        attrs.append(('physicalDeliveryOfficeName', [kw['physicalDeliveryOfficeName']]))
        attrs.append(('telephoneNumber', [kw['telephoneNumber']]))
        attrs.append(('mail', [kw['mail']]))
        attrs.append(('displayName', [kw['displayName']]))

        ctrl = AD_USERCTRL_ACCOUNT_DISABLED | AD_USERCTRL_NORMAL_ACCOUNT
        attrs.append(('userAccountControl', [str(ctrl)]))
        attrs.append(('objectClass', ['user']))
        dn = 'cn=%s,%s' % (user, self._get_base())
        self.__connecion.add_s(dn, attrs)

        self.change_passwd(user, passwd=kw['passwd'])
        self.change_user_ctrl(user)

    def delete_user(self, user):
        '''
        delete user from AD
        :param user: the name of user, Common Name in AD
        :return:
        '''
        ldap_filter = '(&(objectClass=user)(sAMAccountName=%s))' % user
        attr_list = ['*']
        entries = self.__connecion.search_s(self._get_base(), ldap.SCOPE_SUBTREE, ldap_filter, attr_list)
        for res in entries:
            self.__connecion.delete_s(res[0])

    def modify_user(self, user, **kw):
        '''

        :param user:
        :param kw: {
            #花名
            'displayName':'测试',
            #邮箱
            'mail':'test2017_test2017@dtdream.com',
            #部门
            'physicalDeliveryOfficeName':'信息开发部',
            #电话
            'telephoneNumber': '12312341234'
        }
        :return:
        '''
        if self.is_user_exist(user):
            mods =[]
            mods.append((ldap.MOD_REPLACE, 'displayName', [kw['displayName']]))
            mods.append((ldap.MOD_REPLACE, 'mail', [kw['mail']]))
            mods.append((ldap.MOD_REPLACE, 'physicalDeliveryOfficeName', [kw['physicalDeliveryOfficeName']]))
            mods.append((ldap.MOD_REPLACE, 'telephoneNumber', [kw['telephoneNumber']]))
            dn = "cn=%s,%s" % (user, self._get_base())
            self.__connecion.modify_s(dn, mods)


    def create_ou(self, ou):
        '''
        Create OU
        :param ou: the name of OU
        :return:
        '''
        attrs = []
        attrs.append(('objectClass', ['organizationalUnit']))
        attrs.append(('ou', [ou]))
        dn = 'ou=%s, %s' % (ou, self.__base)
        self.__connecion.add_s(dn, attrs)

    def delete_ou(self, name):
        '''
        Delete OU
        :param name: the name of OU
        :return:
        '''
        dn = 'ou=%s, %s' % (name, self.__base)
        try:
            self.__connecion.delete_s(dn)
        except Exception,e:
            pass


    def delete_group(self, name):
        '''
        delete group from AD
        :param name: the name of group, Common Name in AD.
        :return:
        '''
        dn = "cn=%s, %s" % (name, self._get_base())
        try:
            self.__connecion.delete_s(dn)
        except Exception,e:
            pass

    def create_group(self, name):
        '''
        create group in AD
        :param name: the name of group, Common Name in AD.
        :return:
        '''
        attrs = []
        attrs.append(('cn', [name.encode("utf-8")]))
        attrs.append(('sAMAccountName', [name.encode("utf-8")]))
        attrs.append(('objectClass', ['group']))
        dn = 'cn=%s,%s' % (name, self._get_base())
        dn = dn.encode("utf-8")
        self.__connecion.add_s(dn, attrs)


    def is_group_exist(self, name):
        '''
        :param name: the name of group
        :return:
        '''
        entries = self.search(name, 'Group')
        if len(entries) > 0:
            return True
        return False

    def is_user_exist(self, name):
        '''
        :param name: the name of user
        :return:
        '''
        entries = self.search(name)
        if len(entries) > 0:
            return True
        return False

    def is_user_in_group(self, user, group):
        '''
        :param user: the name of user
        :param group: the name of group
        :return:
        '''
        ldap_filter = '(&(cn=%s)(&(objectCategory=Person)(memberOf:1.2.840.113556.1.4.1941:=CN=%s,%s)))' % (user, group, self._get_base())
        attr_list = ['*']
        entries = self.__connecion.search_s(self._get_base(), ldap.SCOPE_SUBTREE, ldap_filter, attr_list)
        if len(entries) > 0:
            return True
        return False

    def add_user_to_group(self, user, group):
        '''
        :param user: the name of user
        :param group: the name of group
        :return:
        '''
        if self.is_user_in_group(user, group):
            return
        mods = []
        user = 'cn=%s,%s' % (user, self._get_base())
        user = user.encode("utf-8")
        mods.append((ldap.MOD_ADD, 'member', [user]))
        dn = "cn=%s,%s" % (group, self._get_base())
        dn = dn.encode("utf-8")
        print dn
        self.__connecion.modify_s(dn, mods)

    def del_user_from_group(self, user, group):
        '''
        :param user: the name of user
        :param group: the name of group
        :return:
        '''
        if self.is_user_in_group(user, group):
            mods = []
            user = 'cn=%s,%s' % (user, self._get_base())
            user = user.encode("utf-8")
            mods.append((ldap.MOD_DELETE, 'member', [user]))
            dn = "cn=%s,%s" % (group, self._get_base())
            dn = dn.encode("utf-8")
            self.__connecion.modify_s(dn, mods)

    def change_passwd(self, user, passwd):
        '''
        :param user: the name of user
        :param passwd: the password of user config.
        :return:
        '''
        if self.is_user_exist(user):
            unicode_pass = unicode('\"'+str(passwd) + '\"')
            passwd_value = unicode_pass.encode('utf-16-le')
            reset_pass = [(ldap.MOD_REPLACE, 'unicodePwd', [passwd_value])]
            dn = "cn=%s,%s" % (user, self._get_base())
            dn = dn.encode("utf-8")
            self.__connecion.modify_s(dn, reset_pass)

    def change_user_ctrl(self, user):
        mods = []
        ctrl = AD_USERCTRL_NORMAL_ACCOUNT
        mods.append((ldap.MOD_REPLACE, 'userAccountControl', [str(ctrl)]))
        dn = "cn=%s,%s" % (user, self._get_base())
        dn = dn.encode("utf-8")
        self.__connecion.modify_s(dn, mods)
