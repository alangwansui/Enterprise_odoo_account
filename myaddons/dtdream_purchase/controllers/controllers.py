# -*- coding: utf-8 -*-
from openerp import http

# class DtdreamPurchase(http.Controller):
#     @http.route('/dtdream_purchase/dtdream_purchase/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/dtdream_purchase/dtdream_purchase/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('dtdream_purchase.listing', {
#             'root': '/dtdream_purchase/dtdream_purchase',
#             'objects': http.request.env['dtdream_purchase.dtdream_purchase'].search([]),
#         })

#     @http.route('/dtdream_purchase/dtdream_purchase/objects/<model("dtdream_purchase.dtdream_purchase"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('dtdream_purchase.object', {
#             'object': obj
#         })