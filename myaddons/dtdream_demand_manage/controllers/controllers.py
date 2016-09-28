# -*- coding: utf-8 -*-
from openerp import http

# class DtdreamDemandManage(http.Controller):
#     @http.route('/dtdream_demand_manage/dtdream_demand_manage/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/dtdream_demand_manage/dtdream_demand_manage/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('dtdream_demand_manage.listing', {
#             'root': '/dtdream_demand_manage/dtdream_demand_manage',
#             'objects': http.request.env['dtdream_demand_manage.dtdream_demand_manage'].search([]),
#         })

#     @http.route('/dtdream_demand_manage/dtdream_demand_manage/objects/<model("dtdream_demand_manage.dtdream_demand_manage"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('dtdream_demand_manage.object', {
#             'object': obj
#         })