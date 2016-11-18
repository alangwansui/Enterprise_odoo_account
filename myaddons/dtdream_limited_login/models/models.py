# -*- coding: utf-8 -*-
import sys
import os
# sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.getcwd())))+"\Enterprise\web\controllers")
# from main import Home,ensure_db
import openerp
from openerp import models, fields, api
from openerp import http
from openerp.http import request
from openerp.addons.web.controllers.main import ensure_db
from openerp.exceptions import ValidationError


class dtdream_limited_login(models.Model):
    _inherit = "res.users"

    fail_times = fields.Integer(string='连续登录失败次数')

    def _compute_islocked(self):
        for rec in self:
            if rec.fail_times >=5:
                rec.is_locked = True
            else:
                rec.is_locked = False
    is_locked = fields.Boolean(string='账号已被锁定',compute=_compute_islocked)

    @api.multi
    def btn_unlocked(self):
        for rec in self:
            if rec.is_locked == False:
                raise ValidationError("该用户未被锁定，不需要解锁！")
            else:
                rec.fail_times = 0


class Home_inher(openerp.addons.web.controllers.main.Home):

    # @http.route('/', type='http', auth="none")
    # def index(self, s_action=None, db=None, **kw):
    #     return http.local_redirect('/index', query=request.params, keep_hash=True)

    @http.route('/web/login', type='http', auth="none")
    def web_login(self, redirect=None, **kw):
        ensure_db()
        request.params['login_success'] = False
        if request.httprequest.method == 'GET' and redirect and request.session.uid:
            return http.redirect_with_hash(redirect)

        if not request.uid:
            request.uid = openerp.SUPERUSER_ID

        values = request.params.copy()
        try:
            values['databases'] = http.db_list()
        except openerp.exceptions.AccessDenied:
            values['databases'] = None

        if request.httprequest.method == 'POST':
            old_uid = request.uid
            uid = request.session.authenticate(request.session.db, request.params['login'], request.params['password'])
            user = request.env['res.users'].sudo().search([('login','=',request.params['login'])])
            # user.fail_times<5包括了user为空的情况,此时user.fail_times=false=0
            if user.fail_times < 5:
                if uid is not False:
                    request.params['login_success'] = True
                    if user:
                        user.fail_times = 0
                    if not redirect:
                        # redirect = '/index'
                        redirect = '/web'
                    return http.redirect_with_hash(redirect)
                else:
                    if user and user.id != 1:
                        user.fail_times += 1
                    values['error'] = "Wrong login/password"
            else:
                values['error'] = "您已连续5次登陆失败，账号已被锁定，请联系系统管理员解锁"
            request.uid = old_uid
        return request.render('web.login', values)