# -*- coding: utf-8 -*-
from openerp import http

# class DtdreamContract(http.Controller):
#     @http.route('/dtdream_contract/dtdream_contract/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/dtdream_contract/dtdream_contract/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('dtdream_contract.listing', {
#             'root': '/dtdream_contract/dtdream_contract',
#             'objects': http.request.env['dtdream_contract.dtdream_contract'].search([]),
#         })

#     @http.route('/dtdream_contract/dtdream_contract/objects/<model("dtdream_contract.dtdream_contract"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('dtdream_contract.object', {
#             'object': obj
#         })