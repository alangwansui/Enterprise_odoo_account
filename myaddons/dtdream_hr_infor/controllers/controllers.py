# -*- coding: utf-8 -*-
from openerp import http

# class DtdreamHrInfor(http.Controller):
#     @http.route('/dtdream_hr_infor/dtdream_hr_infor/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/dtdream_hr_infor/dtdream_hr_infor/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('dtdream_hr_infor.listing', {
#             'root': '/dtdream_hr_infor/dtdream_hr_infor',
#             'objects': http.request.env['dtdream_hr_infor.dtdream_hr_infor'].search([]),
#         })

#     @http.route('/dtdream_hr_infor/dtdream_hr_infor/objects/<model("dtdream_hr_infor.dtdream_hr_infor"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('dtdream_hr_infor.object', {
#             'object': obj
#         })