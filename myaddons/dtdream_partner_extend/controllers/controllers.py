# -*- coding: utf-8 -*-
from openerp import http

# class DtdreamPartnerExtend(http.Controller):
#     @http.route('/dtdream_partner_extend/dtdream_partner_extend/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/dtdream_partner_extend/dtdream_partner_extend/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('dtdream_partner_extend.listing', {
#             'root': '/dtdream_partner_extend/dtdream_partner_extend',
#             'objects': http.request.env['dtdream_partner_extend.dtdream_partner_extend'].search([]),
#         })

#     @http.route('/dtdream_partner_extend/dtdream_partner_extend/objects/<model("dtdream_partner_extend.dtdream_partner_extend"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('dtdream_partner_extend.object', {
#             'object': obj
#         })