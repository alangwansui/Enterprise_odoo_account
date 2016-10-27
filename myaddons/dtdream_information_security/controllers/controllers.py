# -*- coding: utf-8 -*-
from openerp import http

# class DtdreamInformationSecurity(http.Controller):
#     @http.route('/dtdream_information_security/dtdream_information_security/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/dtdream_information_security/dtdream_information_security/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('dtdream_information_security.listing', {
#             'root': '/dtdream_information_security/dtdream_information_security',
#             'objects': http.request.env['dtdream_information_security.dtdream_information_security'].search([]),
#         })

#     @http.route('/dtdream_information_security/dtdream_information_security/objects/<model("dtdream_information_security.dtdream_information_security"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('dtdream_information_security.object', {
#             'object': obj
#         })