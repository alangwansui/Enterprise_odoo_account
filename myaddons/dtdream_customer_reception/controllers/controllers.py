# -*- coding: utf-8 -*-
from openerp import http

# class DtdreamCustomerReception(http.Controller):
#     @http.route('/dtdream_customer_reception/dtdream_customer_reception/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/dtdream_customer_reception/dtdream_customer_reception/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('dtdream_customer_reception.listing', {
#             'root': '/dtdream_customer_reception/dtdream_customer_reception',
#             'objects': http.request.env['dtdream_customer_reception.dtdream_customer_reception'].search([]),
#         })

#     @http.route('/dtdream_customer_reception/dtdream_customer_reception/objects/<model("dtdream_customer_reception.dtdream_customer_reception"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('dtdream_customer_reception.object', {
#             'object': obj
#         })