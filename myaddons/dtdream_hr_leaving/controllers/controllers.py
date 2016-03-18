# -*- coding: utf-8 -*-
from openerp import http

# class DtdreamHrLeaving(http.Controller):
#     @http.route('/dtdream_hr_leaving/dtdream_hr_leaving/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/dtdream_hr_leaving/dtdream_hr_leaving/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('dtdream_hr_leaving.listing', {
#             'root': '/dtdream_hr_leaving/dtdream_hr_leaving',
#             'objects': http.request.env['dtdream_hr_leaving.dtdream_hr_leaving'].search([]),
#         })

#     @http.route('/dtdream_hr_leaving/dtdream_hr_leaving/objects/<model("dtdream_hr_leaving.dtdream_hr_leaving"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('dtdream_hr_leaving.object', {
#             'object': obj
#         })