# -*- coding: utf-8 -*-
from openerp import http

# class DtdreamPartner(http.Controller):
#     @http.route('/dtdream_partner/dtdream_partner/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/dtdream_partner/dtdream_partner/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('dtdream_partner.listing', {
#             'root': '/dtdream_partner/dtdream_partner',
#             'objects': http.request.env['dtdream_partner.dtdream_partner'].search([]),
#         })

#     @http.route('/dtdream_partner/dtdream_partner/objects/<model("dtdream_partner.dtdream_partner"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('dtdream_partner.object', {
#             'object': obj
#         })