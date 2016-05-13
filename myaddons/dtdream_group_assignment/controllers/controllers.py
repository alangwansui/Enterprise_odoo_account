# -*- coding: utf-8 -*-
from openerp import http

# class DtdreamGroupAssignment(http.Controller):
#     @http.route('/dtdream_group_assignment/dtdream_group_assignment/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/dtdream_group_assignment/dtdream_group_assignment/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('dtdream_group_assignment.listing', {
#             'root': '/dtdream_group_assignment/dtdream_group_assignment',
#             'objects': http.request.env['dtdream_group_assignment.dtdream_group_assignment'].search([]),
#         })

#     @http.route('/dtdream_group_assignment/dtdream_group_assignment/objects/<model("dtdream_group_assignment.dtdream_group_assignment"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('dtdream_group_assignment.object', {
#             'object': obj
#         })