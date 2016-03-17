# -*- coding: utf-8 -*-
from openerp import http

# class DtdreamAccount(http.Controller):
#     @http.route('/dtdream_account/dtdream_account/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/dtdream_account/dtdream_account/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('dtdream_account.listing', {
#             'root': '/dtdream_account/dtdream_account',
#             'objects': http.request.env['dtdream_account.dtdream_account'].search([]),
#         })

#     @http.route('/dtdream_account/dtdream_account/objects/<model("dtdream_account.dtdream_account"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('dtdream_account.object', {
#             'object': obj
#         })