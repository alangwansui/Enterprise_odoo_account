# -*- coding: utf-8 -*-
from openerp import http

# class DtdreamSale(http.Controller):
#     @http.route('/dtdream_sale/dtdream_sale/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/dtdream_sale/dtdream_sale/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('dtdream_sale.listing', {
#             'root': '/dtdream_sale/dtdream_sale',
#             'objects': http.request.env['dtdream_sale.dtdream_sale'].search([]),
#         })

#     @http.route('/dtdream_sale/dtdream_sale/objects/<model("dtdream_sale.dtdream_sale"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('dtdream_sale.object', {
#             'object': obj
#         })