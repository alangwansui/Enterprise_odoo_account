# -*- coding: utf-8 -*-
from openerp import http

# class ShumengSale(http.Controller):
#     @http.route('/shumeng_sale/shumeng_sale/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/shumeng_sale/shumeng_sale/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('shumeng_sale.listing', {
#             'root': '/shumeng_sale/shumeng_sale',
#             'objects': http.request.env['shumeng_sale.shumeng_sale'].search([]),
#         })

#     @http.route('/shumeng_sale/shumeng_sale/objects/<model("shumeng_sale.shumeng_sale"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('shumeng_sale.object', {
#             'object': obj
#         })