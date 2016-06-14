# -*- coding: utf-8 -*-
from openerp import http

# class DtdreamExpense(http.Controller):
#     @http.route('/dtdream_expense/dtdream_expense/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/dtdream_expense/dtdream_expense/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('dtdream_expense.listing', {
#             'root': '/dtdream_expense/dtdream_expense',
#             'objects': http.request.env['dtdream_expense.dtdream_expense'].search([]),
#         })

#     @http.route('/dtdream_expense/dtdream_expense/objects/<model("dtdream_expense.dtdream_expense"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('dtdream_expense.object', {
#             'object': obj
#         })