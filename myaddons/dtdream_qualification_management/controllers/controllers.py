# -*- coding: utf-8 -*-
from openerp import http

# class DtdreamQualificationManagement(http.Controller):
#     @http.route('/dtdream_qualification_management/dtdream_qualification_management/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/dtdream_qualification_management/dtdream_qualification_management/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('dtdream_qualification_management.listing', {
#             'root': '/dtdream_qualification_management/dtdream_qualification_management',
#             'objects': http.request.env['dtdream_qualification_management.dtdream_qualification_management'].search([]),
#         })

#     @http.route('/dtdream_qualification_management/dtdream_qualification_management/objects/<model("dtdream_qualification_management.dtdream_qualification_management"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('dtdream_qualification_management.object', {
#             'object': obj
#         })