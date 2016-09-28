# -*- coding: utf-8 -*-
from openerp import http

# class DtdreamGrants(http.Controller):
#     @http.route('/dtdream_grants/dtdream_grants/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/dtdream_grants/dtdream_grants/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('dtdream_grants.listing', {
#             'root': '/dtdream_grants/dtdream_grants',
#             'objects': http.request.env['dtdream_grants.dtdream_grants'].search([]),
#         })

#     @http.route('/dtdream_grants/dtdream_grants/objects/<model("dtdream_grants.dtdream_grants"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('dtdream_grants.object', {
#             'object': obj
#         })