# -*- coding: utf-8 -*-
import xmlrpclib


url = "http://localhost:8069"
db = "odoo"
username = 'admin'
password = '123'


common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(url))
print common.version()

uid = common.authenticate(db, username, password, {})
print uid

models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(url))

courses = models.execute_kw(db, uid, password,
    'shumeng.course', 'search',[[]])


print courses

partner = models.execute_kw(db, uid, password,
    'res.partner', 'search_read',
    [[['is_company', '=', False]]])
print partner