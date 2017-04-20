# -*- coding: utf-8 -*-
from openerp import http

# class DtdreamSaleSignCustomer(http.Controller):
#     @http.route('/dtdream_sale_sign_customer/dtdream_sale_sign_customer/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/dtdream_sale_sign_customer/dtdream_sale_sign_customer/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('dtdream_sale_sign_customer.listing', {
#             'root': '/dtdream_sale_sign_customer/dtdream_sale_sign_customer',
#             'objects': http.request.env['dtdream_sale_sign_customer.dtdream_sale_sign_customer'].search([]),
#         })

#     @http.route('/dtdream_sale_sign_customer/dtdream_sale_sign_customer/objects/<model("dtdream_sale_sign_customer.dtdream_sale_sign_customer"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('dtdream_sale_sign_customer.object', {
#             'object': obj
#         })