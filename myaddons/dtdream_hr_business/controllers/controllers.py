# -*- coding: utf-8 -*-
from openerp import http

# class DtdreamHrBusiness(http.Controller):
#     @http.route('/dtdream_hr_business/dtdream_hr_business/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/dtdream_hr_business/dtdream_hr_business/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('dtdream_hr_business.listing', {
#             'root': '/dtdream_hr_business/dtdream_hr_business',
#             'objects': http.request.env['dtdream_hr_business.dtdream_hr_business'].search([]),
#         })

#     @http.route('/dtdream_hr_business/dtdream_hr_business/objects/<model("dtdream_hr_business.dtdream_hr_business"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('dtdream_hr_business.object', {
#             'object': obj
#         })