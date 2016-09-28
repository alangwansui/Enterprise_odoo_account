# -*- coding: utf-8 -*-
from openerp import http

# class DtdreamHrResume(http.Controller):
#     @http.route('/dtdream_hr_resume/dtdream_hr_resume/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/dtdream_hr_resume/dtdream_hr_resume/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('dtdream_hr_resume.listing', {
#             'root': '/dtdream_hr_resume/dtdream_hr_resume',
#             'objects': http.request.env['dtdream_hr_resume.dtdream_hr_resume'].search([]),
#         })

#     @http.route('/dtdream_hr_resume/dtdream_hr_resume/objects/<model("dtdream_hr_resume.dtdream_hr_resume"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('dtdream_hr_resume.object', {
#             'object': obj
#         })