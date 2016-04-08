# -*- coding: utf-8 -*-
from openerp import http

# class DtdreamTravel(http.Controller):
#     @http.route('/dtdream_travel/dtdream_travel/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/dtdream_travel/dtdream_travel/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('dtdream_travel.listing', {
#             'root': '/dtdream_travel/dtdream_travel',
#             'objects': http.request.env['dtdream_travel.dtdream_travel'].search([]),
#         })

#     @http.route('/dtdream_travel/dtdream_travel/objects/<model("dtdream_travel.dtdream_travel"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('dtdream_travel.object', {
#             'object': obj
#         })