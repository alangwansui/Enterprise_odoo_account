# -*- coding: utf-8 -*-
from openerp import http

# class DtdreamResume(http.Controller):
#     @http.route('/dtdream_resume/dtdream_resume/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/dtdream_resume/dtdream_resume/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('dtdream_resume.listing', {
#             'root': '/dtdream_resume/dtdream_resume',
#             'objects': http.request.env['dtdream_resume.dtdream_resume'].search([]),
#         })

#     @http.route('/dtdream_resume/dtdream_resume/objects/<model("dtdream_resume.dtdream_resume"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('dtdream_resume.object', {
#             'object': obj
#         })