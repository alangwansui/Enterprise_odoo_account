# -*- coding: utf-8 -*-
import xmlrpclib


url = "http://localhost:8111"
db = "odoo9"
username = 'admin'
password = 'odoo9'


common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(url))
print common.version()

uid = common.authenticate(db, username, password, {})
print uid

models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(url))

courses = models.execute_kw(db, uid, password,
    'shumeng.course', 'search',
    [[]])

print courses