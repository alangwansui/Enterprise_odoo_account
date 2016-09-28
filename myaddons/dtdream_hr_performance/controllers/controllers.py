# -*- coding: utf-8 -*-
from openerp import http

# class Myaddons(http.Controller):
#     @http.route('/myaddons/myaddons/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/myaddons/myaddons/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('myaddons.listing', {
#             'root': '/myaddons/myaddons',
#             'objects': http.request.env['myaddons.myaddons'].search([]),
#         })

#     @http.route('/myaddons/myaddons/objects/<model("myaddons.myaddons"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('myaddons.object', {
#             'object': obj
#         })