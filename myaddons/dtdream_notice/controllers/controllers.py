# -*- coding: utf-8 -*-
from openerp import http

# class DtdreamNotice(http.Controller):
#     @http.route('/dtdream_notice/dtdream_notice/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/dtdream_notice/dtdream_notice/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('dtdream_notice.listing', {
#             'root': '/dtdream_notice/dtdream_notice',
#             'objects': http.request.env['dtdream_notice.dtdream_notice'].search([]),
#         })

#     @http.route('/dtdream_notice/dtdream_notice/objects/<model("dtdream_notice.dtdream_notice"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('dtdream_notice.object', {
#             'object': obj
#         })