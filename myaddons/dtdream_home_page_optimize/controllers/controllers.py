# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.addons.web.controllers.main import ensure_db
from openerp import http
from openerp.http import request
import werkzeug.utils
import openerp


class Home_page_extend(openerp.addons.web.controllers.main.Home):

    @http.route('/web', type='http', auth="none")
    def web_client(self, s_action=None, **kw):
        ensure_db()
        if not request.session.uid:
            return werkzeug.utils.redirect('/web/login', 303)
        if kw.get('redirect'):
            return werkzeug.utils.redirect(kw.get('redirect'), 303)

        request.uid = request.session.uid
        return request.render('dtdream_home_page_optimize.home_page')
