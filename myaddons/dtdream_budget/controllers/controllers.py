# -*- coding: utf-8 -*-
from openerp import http

# class DtdreamBudget(http.Controller):
#     @http.route('/dtdream_budget/dtdream_budget/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/dtdream_budget/dtdream_budget/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('dtdream_budget.listing', {
#             'root': '/dtdream_budget/dtdream_budget',
#             'objects': http.request.env['dtdream_budget.dtdream_budget'].search([]),
#         })

#     @http.route('/dtdream_budget/dtdream_budget/objects/<model("dtdream_budget.dtdream_budget"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('dtdream_budget.object', {
#             'object': obj
#         })