# -*- coding: utf-8 -*-

__author__ = "g0335"


import ldap

class Error(Exception):
    pass

DTLDAPError = ldap.LDAPError