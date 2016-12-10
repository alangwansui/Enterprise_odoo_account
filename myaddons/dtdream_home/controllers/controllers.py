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

    @http.route('/dtdream_home/resetpasswd', type='json', auth="user", methods=['POST'], csrf=False)
    def resetpasswd(self, **kw):

        old_password=request.jsonrequest['old_pwd']
        new_password = request.jsonrequest['new_pwd']
        confirm_password = request.jsonrequest['confirm_password']

        if not (old_password.strip() and new_password.strip() and confirm_password.strip()):
            return {'code': 1, 'error': '密码不能为空!', 'title': '修改密码'}

        if new_password != confirm_password:
            return {'code': 2, 'error': '新密码两次输入不一致!',
                    'title': '修改密码'}

        import re
        result = re.match(
            r'^(?![0-9_]+$)(?![a-z_]+$)(?![A-Z_]+$)(?![\W_]+$)(?![0-9a-z]+$)(?![A-Za-z]+$)(?![\Wa-z]+$)(?![0-9A-Z]+$)(?![\WA-Z]+$)(?![0-9\W]+$)[\w\W]{8,}$',
            new_password)
        if not result:
            return {'code': 3, 'error': '密码要符合规则:1.密码长度至少8位字符；;2.同时包含大、小写字母，数字、特殊字符中的三种类型混合组成；',
                    'title': '修改密码'}
        try:
            if request.session.model('res.users').change_password(
                    old_password, new_password):
                return {'code': 0, 'error': '', 'title': '修改密码成功'}
        except Exception:
            return {'code': 4, 'error': '旧密码输入错误,修改密码失败!',
                    'title': '修改密码'}

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