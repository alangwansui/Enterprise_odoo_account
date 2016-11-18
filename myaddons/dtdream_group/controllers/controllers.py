# -*- coding: utf-8 -*-
from openerp import http

# class DtdreamGroup(http.Controller):
#     @http.route('/dtdream_group/dtdream_group/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/dtdream_group/dtdream_group/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('dtdream_group.listing', {
#             'root': '/dtdream_group/dtdream_group',
#             'objects': http.request.env['dtdream_group.dtdream_group'].search([]),
#         })

#     @http.route('/dtdream_group/dtdream_group/objects/<model("dtdream_group.dtdream_group"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('dtdream_group.object', {
#             'object': obj
#         })