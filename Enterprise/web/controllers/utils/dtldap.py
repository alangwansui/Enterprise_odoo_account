# -*- coding: utf-8 -*-
import ldap
import base64
import hashlib
import binascii
import logging
from ldap.filter import filter_format

import json

from openerp.modules.registry import RegistryManager
_logger = logging.getLogger(__name__)


class DTLDAPPError(Exception):

    ERROR_NUM_LDAP_BIND_FAILED = 1
    ERROR_NUM_LDAP_ERROR = 2
    ERROR_NUM_LDAP_USER_IS_NOT_EXIST = 3
    ERROR_NUM_LDAP_MODIFY_PASSWORD_FAILED = 4

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class DTLDAP(object):

    def __init__(self, db, login, ssl=False, domain=None, certfile=None):
        self.db = db
        self.login = login
        self.ssl = ssl
        self.domain = domain
        self.certfile = certfile
        self.connect, self.conf = self._init_connect(db, login, ssl, domain, certfile)

    def _init_connect(self, db, login, ssl=False, domain=None, certfile=None):
        registry = RegistryManager.get(db)
        with registry.cursor() as cr:
            for conf in self._get_ldap_dicts(cr):
                try:
                    ldap_filter = filter_format(conf['ldap_filter'], (login,))
                except TypeError:
                    ldap_filter = '(cn=%s)' % (login)

                try:
                    if ssl:
                        conf['ldap_server'] = domain
                        conf['ldap_server_port'] = 636

                    connect = self._query(conf, ldap_filter)
                    if connect:
                        return connect, conf
                        break
                except DTLDAPPError, e:
                    raise DTLDAPPError(e.value)

            if connect is None:
                raise DTLDAPPError(DTLDAPPError.ERROR_NUM_LDAP_USER_IS_NOT_EXIST)

    def _get_ldap_dicts(self, cr, ids=None):
        """
        Retrieve res_company_ldap resources from the database in dictionary
        format.

        :param list ids: Valid ids of model res_company_ldap. If not \
        specified, process all resources (unlike other ORM methods).
        :return: ldap configurations
        :rtype: list of dictionaries
        """

        if ids:
            id_clause = 'AND id IN (%s)'
            args = [tuple(ids)]
        else:
            id_clause = ''
            args = []
        cr.execute("""
            SELECT id, company, ldap_server, ldap_server_port, ldap_binddn,
                   ldap_password, ldap_filter, ldap_base, "user", create_user,
                   ldap_tls
            FROM res_company_ldap
            WHERE ldap_server != '' """ + id_clause + """ ORDER BY sequence
        """, args)
        return cr.dictfetchall()

    def _connect(self, conf):

        """
        # ldaps method

        """
        if self.ssl:
            uri = 'ldaps://%s:%d' % (conf['ldap_server'],
                                     conf['ldap_server_port'])
            ldap.set_option(ldap.OPT_PROTOCOL_VERSION, ldap.VERSION3)
            ldap.set_option(ldap.OPT_X_TLS_CACERTFILE, self.certfile)
            ldap.set_option(ldap.OPT_X_TLS, ldap.OPT_X_TLS_DEMAND)
            ldap.set_option(ldap.OPT_X_TLS_DEMAND, True)
            # ldap.set_option(ldap.OPT_DEBUG_LEVEL, 255)
        else:
            uri = 'ldap://%s:%d' % (conf['ldap_server'],
                                    conf['ldap_server_port'])

        connection = ldap.initialize(uri)

        if conf['ldap_tls']:
            connection.start_tls_s()

        return connection

    def _query(self, conf, ldap_filter, retrieve_attributes=None):

        try:
            conn = self._connect(conf)
            ldap_password = conf['ldap_password'] or ''
            ldap_binddn = conf['ldap_binddn'] or ''
            conn.simple_bind_s(ldap_binddn.encode('utf-8'), ldap_password.encode('utf-8'))
            results = conn.search_st(conf['ldap_base'], ldap.SCOPE_SUBTREE,
                                     ldap_filter, retrieve_attributes, timeout=60)
            if results:
                return conn
            else:
                conn.unbind()
                return None

        except ldap.INVALID_CREDENTIALS:
            raise DTLDAPPError(DTLDAPPError.ERROR_NUM_LDAP_BIND_FAILED)
        except ldap.LDAPError, e:
            raise DTLDAPPError(DTLDAPPError.ERROR_NUM_LDAP_ERROR)

        return None

    def _get_ldap_conf(self, db):
        registry = RegistryManager.get(db)
        with registry.cursor() as cr:
            return self._get_ldap_dicts(cr)

    def unbind(self):
        self.connect.unbind()

    def query_user(self, login):

        try:
            ldap_filter = filter_format(self.conf['ldap_filter'], (login,))
            entry = self.connect.search_st(self.conf['ldap_base'], ldap.SCOPE_SUBTREE, ldap_filter, timeout=60)
        except Exception, e:
            entry = []

        return entry

    def reset_password(self, **kw):
        """"
        kw = {
        'login':''
        'sn':''
        'passwd':''
        'passwd2':''
        'db_name':''
        'uid':''
        }
        """
        password = kw['passwd']
        cn = kw['login']

        unicode_pass = unicode('\"' + str(password) + '\"')
        password_value = unicode_pass.encode('utf-16-le')
        reset_pass = [(ldap.MOD_REPLACE, 'unicodePwd', [password_value])]

        dn = ('cn=%s,' % cn) + self.conf['ldap_base']

        try:
            self.connect.modify_s(dn, reset_pass)
        except Exception, e:
            raise DTLDAPPError(DTLDAPPError.ERROR_NUM_LDAP_MODIFY_PASSWORD_FAILED)
