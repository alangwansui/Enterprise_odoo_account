# -*- coding: utf-8 -*-
from openerp import http

# class DtdreamLimitedLogin(http.Controller):
#     @http.route('/dtdream_limited_login/dtdream_limited_login/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/dtdream_limited_login/dtdream_limited_login/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('dtdream_limited_login.listing', {
#             'root': '/dtdream_limited_login/dtdream_limited_login',
#             'objects': http.request.env['dtdream_limited_login.dtdream_limited_login'].search([]),
#         })

#     @http.route('/dtdream_limited_login/dtdream_limited_login/objects/<model("dtdream_limited_login.dtdream_limited_login"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('dtdream_limited_login.object', {
#             'object': obj
#         })