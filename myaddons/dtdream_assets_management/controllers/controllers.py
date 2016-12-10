# -*- coding: utf-8 -*-
from openerp import http

# class DtdreamAssetsManagement(http.Controller):
#     @http.route('/dtdream_assets_management/dtdream_assets_management/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/dtdream_assets_management/dtdream_assets_management/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('dtdream_assets_management.listing', {
#             'root': '/dtdream_assets_management/dtdream_assets_management',
#             'objects': http.request.env['dtdream_assets_management.dtdream_assets_management'].search([]),
#         })

#     @http.route('/dtdream_assets_management/dtdream_assets_management/objects/<model("dtdream_assets_management.dtdream_assets_management"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('dtdream_assets_management.object', {
#             'object': obj
#         })