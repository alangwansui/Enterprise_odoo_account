# -*- coding: utf-8 -*-
from openerp import http

# class DtdreamSaleOrderApproval(http.Controller):
#     @http.route('/dtdream_sale_order_approval/dtdream_sale_order_approval/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/dtdream_sale_order_approval/dtdream_sale_order_approval/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('dtdream_sale_order_approval.listing', {
#             'root': '/dtdream_sale_order_approval/dtdream_sale_order_approval',
#             'objects': http.request.env['dtdream_sale_order_approval.dtdream_sale_order_approval'].search([]),
#         })

#     @http.route('/dtdream_sale_order_approval/dtdream_sale_order_approval/objects/<model("dtdream_sale_order_approval.dtdream_sale_order_approval"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('dtdream_sale_order_approval.object', {
#             'object': obj
#         })