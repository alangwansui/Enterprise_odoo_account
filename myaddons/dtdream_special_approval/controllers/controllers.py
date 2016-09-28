# -*- coding: utf-8 -*-
from openerp import http

# class DtdreamSpecialApproval(http.Controller):
#     @http.route('/dtdream_special_approval/dtdream_special_approval/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/dtdream_special_approval/dtdream_special_approval/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('dtdream_special_approval.listing', {
#             'root': '/dtdream_special_approval/dtdream_special_approval',
#             'objects': http.request.env['dtdream_special_approval.dtdream_special_approval'].search([]),
#         })

#     @http.route('/dtdream_special_approval/dtdream_special_approval/objects/<model("dtdream_special_approval.dtdream_special_approval"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('dtdream_special_approval.object', {
#             'object': obj
#         })