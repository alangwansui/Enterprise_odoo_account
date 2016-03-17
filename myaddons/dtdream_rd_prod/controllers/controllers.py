# -*- coding: utf-8 -*-
from openerp import http

# class DtdreamRdProd(http.Controller):
#     @http.route('/dtdream_rd_prod/dtdream_rd_prod/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/dtdream_rd_prod/dtdream_rd_prod/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('dtdream_rd_prod.listing', {
#             'root': '/dtdream_rd_prod/dtdream_rd_prod',
#             'objects': http.request.env['dtdream_rd_prod.dtdream_rd_prod'].search([]),
#         })

#     @http.route('/dtdream_rd_prod/dtdream_rd_prod/objects/<model("dtdream_rd_prod.dtdream_rd_prod"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('dtdream_rd_prod.object', {
#             'object': obj
#         })