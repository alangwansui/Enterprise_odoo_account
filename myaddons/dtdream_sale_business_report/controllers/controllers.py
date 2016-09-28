# -*- coding: utf-8 -*-
from openerp import http

# class DtdreamSaleBusinessReport(http.Controller):
#     @http.route('/dtdream_sale_business_report/dtdream_sale_business_report/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/dtdream_sale_business_report/dtdream_sale_business_report/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('dtdream_sale_business_report.listing', {
#             'root': '/dtdream_sale_business_report/dtdream_sale_business_report',
#             'objects': http.request.env['dtdream_sale_business_report.dtdream_sale_business_report'].search([]),
#         })

#     @http.route('/dtdream_sale_business_report/dtdream_sale_business_report/objects/<model("dtdream_sale_business_report.dtdream_sale_business_report"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('dtdream_sale_business_report.object', {
#             'object': obj
#         })