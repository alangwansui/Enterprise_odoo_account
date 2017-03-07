# -*- coding: utf-8 -*-
from openerp import http

# class DtdreamSaleDataReport(http.Controller):
#     @http.route('/dtdream_sale_data_report/dtdream_sale_data_report/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/dtdream_sale_data_report/dtdream_sale_data_report/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('dtdream_sale_data_report.listing', {
#             'root': '/dtdream_sale_data_report/dtdream_sale_data_report',
#             'objects': http.request.env['dtdream_sale_data_report.dtdream_sale_data_report'].search([]),
#         })

#     @http.route('/dtdream_sale_data_report/dtdream_sale_data_report/objects/<model("dtdream_sale_data_report.dtdream_sale_data_report"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('dtdream_sale_data_report.object', {
#             'object': obj
#         })