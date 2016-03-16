# -*- coding: utf-8 -*-
from openerp import http

# class ShumengHr(http.Controller):
#     @http.route('/shumeng_hr/shumeng_hr/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/shumeng_hr/shumeng_hr/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('shumeng_hr.listing', {
#             'root': '/shumeng_hr/shumeng_hr',
#             'objects': http.request.env['shumeng_hr.shumeng_hr'].search([]),
#         })

#     @http.route('/shumeng_hr/shumeng_hr/objects/<model("shumeng_hr.shumeng_hr"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('shumeng_hr.object', {
#             'object': obj
#         })