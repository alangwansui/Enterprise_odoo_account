# -*- coding: utf-8 -*-
from openerp import http

# class DtdreamProjectManage(http.Controller):
#     @http.route('/dtdream_project_manage/dtdream_project_manage/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/dtdream_project_manage/dtdream_project_manage/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('dtdream_project_manage.listing', {
#             'root': '/dtdream_project_manage/dtdream_project_manage',
#             'objects': http.request.env['dtdream_project_manage.dtdream_project_manage'].search([]),
#         })

#     @http.route('/dtdream_project_manage/dtdream_project_manage/objects/<model("dtdream_project_manage.dtdream_project_manage"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('dtdream_project_manage.object', {
#             'object': obj
#         })