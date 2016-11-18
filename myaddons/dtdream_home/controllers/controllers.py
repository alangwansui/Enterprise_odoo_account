# -*- coding: utf-8 -*-
from openerp import http
from openerp.http import request
import logging

_logger = logging.getLogger(__name__)

class DtdreamHome(http.Controller):
    @http.route('/index', type='http', auth='user')
    def index(self, **kw):
        # return "Hello, world"
        return http.request.render('dtdream_home.home')

    # @http.route('/dtdream_home/dtdream_home/objects/', auth='public')
    # def list(self, **kw):
    #     return http.request.render('dtdream_home.listing', {
    #         'root': '/dtdream_home/dtdream_home',
    #         'objects': http.request.env['dtdream_home.dtdream_home'].search([]),
    #     })
    #
    # @http.route('/dtdream_home/dtdream_home/objects/<model("dtdream_home.dtdream_home"):obj>/', auth='public')
    # def object(self, obj, **kw):
    #     return http.request.render('dtdream_home.object', {
    #         'object': obj
    #     })