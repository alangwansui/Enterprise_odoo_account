# -*- coding: utf-8 -*-
from openerp import http

# class DtdreamSaleContractFee(http.Controller):
#     @http.route('/dtdream_sale_contract_fee/dtdream_sale_contract_fee/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/dtdream_sale_contract_fee/dtdream_sale_contract_fee/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('dtdream_sale_contract_fee.listing', {
#             'root': '/dtdream_sale_contract_fee/dtdream_sale_contract_fee',
#             'objects': http.request.env['dtdream_sale_contract_fee.dtdream_sale_contract_fee'].search([]),
#         })

#     @http.route('/dtdream_sale_contract_fee/dtdream_sale_contract_fee/objects/<model("dtdream_sale_contract_fee.dtdream_sale_contract_fee"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('dtdream_sale_contract_fee.object', {
#             'object': obj
#         })