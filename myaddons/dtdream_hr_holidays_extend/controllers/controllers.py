# -*- coding: utf-8 -*-
from openerp import http

# class DtdreamHrHolidaysExtend(http.Controller):
#     @http.route('/dtdream_hr_holidays_extend/dtdream_hr_holidays_extend/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/dtdream_hr_holidays_extend/dtdream_hr_holidays_extend/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('dtdream_hr_holidays_extend.listing', {
#             'root': '/dtdream_hr_holidays_extend/dtdream_hr_holidays_extend',
#             'objects': http.request.env['dtdream_hr_holidays_extend.dtdream_hr_holidays_extend'].search([]),
#         })

#     @http.route('/dtdream_hr_holidays_extend/dtdream_hr_holidays_extend/objects/<model("dtdream_hr_holidays_extend.dtdream_hr_holidays_extend"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('dtdream_hr_holidays_extend.object', {
#             'object': obj
#         })