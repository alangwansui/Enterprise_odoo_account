# -*- coding: utf-8 -*-
from openerp import http, fields
from openerp.http import request
from ..api import auth, user
import werkzeug
import logging
import json
_logger = logging.getLogger(__name__)


class dingTalk(http.Controller):

    @http.route('/dtdream_expense_dingtalk/index', type='http', auth="public")
    def index(self, **kw):
        values = self.get_dd_config()
        return http.request.render("dtdream_expense_dingtalk.index", values)

    @http.route('/dtdream_expense_dingtalk/authUser', type='http', auth="none")
    def auth(self, **kw):
        _logger.info("kw:"+str(kw.get("access_token", "")))
        token = kw.get("access_token", "")
        code = kw.get("code")
        result = user.get_user_id(token, code)
        _logger.info("userId:" + str(result))
        userid = result[1]['userid']
        _logger.info("userid:" + str(userid))
        res_users = request.env['res.users'].sudo().search([('dd_userid', '=', userid)], limit=1)
        _logger.info("users:" + str(res_users))
        if res_users:
            res_user = res_users[0]
            uid = request.session.authenticate(request.session.db, res_user.login, userid)

            # _logger.info("begin message..")
            # agentId = request.env['ir.config_parameter'].get_param('dtdream.expense.agentId', default="")
            # message.send(token,userid,'','text','hello,me too',agentId);
            # _logger.info("end message..")

            _logger.info("user id:" + str(request.session.uid))
            _logger.info("uid:" + str(uid))
            if uid:
                values = {'userid': userid, 'errcode': 0}
            else:
                values = {'error': u'登陆失败,请联系管理员', 'errcode':-1}
            _logger.info("values:" + str(values))

            return werkzeug.wrappers.Response(json.dumps(values))

    @http.route('/dtdream_expense_dingtalk/main', type='http', auth="user")
    def expense(self, **kw):
        _logger.info("expense.....")
        return http.request.render("dtdream_expense_dingtalk.main")

    @http.route('/dtdream_expense_dingtalk/main_index', type='http', auth="public")
    def main_index(self, **kw):
        return http.request.render("dtdream_expense_dingtalk.main_index")

    @http.route('/dtdream_expense_dingtalk/my', type='http', auth="public")
    def consumer_my(self, **kw):
        values = self.get_dd_config()
        return http.request.render("dtdream_expense_dingtalk.detail", values)

    def get_dd_config(self):
        agentId = request.env['ir.config_parameter'].get_param('dtdream.expense.agentId', default="")
        url = request.env['ir.config_parameter'].get_param('dtdream.expense.agentUrl', default="")
        corpId = request.env['ir.config_parameter'].get_param('dtdream.dingtalk.corpId', default='')
        corpSecret = request.env['ir.config_parameter'].get_param('dtdream.dingtalk.corpSecret', default='')
        last_token = request.env['ir.config_parameter'].get_param('dtdream.dingtalk.token', default='')
        last_ticket = request.env['ir.config_parameter'].get_param('dtdream.dingtalk.ticket', default='')
        last_token_time = request.env['ir.config_parameter'].get_param('dtdream.dingtalk.time', default='')
        now_time = fields.Datetime.from_string(fields.Datetime.now())
        token = None
        ticket = None
        if last_token_time:
            last_time = fields.Datetime.from_string(last_token_time)
            _logger.info("reslut:" + str((now_time - last_time).seconds))
            if (now_time - last_time).seconds <= 3600:
                token = last_token
                ticket = last_ticket
        if not token or not ticket:
            _logger.info("corp:" + str(corpId))
            result = auth.get_access_token(corpId, corpSecret)
            token = result[1]['access_token']
            result = auth.get_jsapi_ticket(token)
            _logger.info("result:" + str(result))
            ticket = result[1]['ticket']
            request.env['ir.config_parameter'].sudo().set_param('dtdream.dingtalk.time', now_time)
            request.env['ir.config_parameter'].sudo().set_param('dtdream.dingtalk.token', token)
            request.env['ir.config_parameter'].sudo().set_param('dtdream.dingtalk.ticket', ticket)
        timestamp = auth.get_timestamp()
        noncestr = 'abcdefg'
        _logger.info("request;" + str(request.httprequest.url))
        _logger.info("url:" + url)
        _logger.info("ticket:" + ticket)
        url = request.httprequest.url
        signature = auth.sign(ticket, noncestr, timestamp, url)
        values = {
            'jsticket': ticket,
            'signature': signature,
            'nonceStr': 'abcdefg',
            'timeStamp': timestamp,
            'corpId': corpId,
            'agentId': agentId,
            'token': token
        }
        return values

    # @http.route('/dtdream_expense_dingtalk/detail', type='http', auth="public")
    # def consumer_detail(self, **kw):
    #     values = self.get_dd_config()
    #     return http.request.render("dtdream_expense_dingtalk.detail", values)
    #
    # @http.route('/dtdream_expense_dingtalk/create_detail', type='http', auth="public")
    # def consumer_detail_create(self, **kw):
    #     values = self.get_dd_config()
    #     return http.request.render("dtdream_expense_dingtalk.detail", values)
    #
    # @http.route('/dtdream_expense_dingtalk/receipts', type='http', auth="public")
    # def consumer_receipts(self, **kw):
    #     values = self.get_dd_config()
    #     return http.request.render("dtdream_expense_dingtalk.detail", values)
    #
    # @http.route('/dtdream_expense_dingtalk/approval', type='http', auth="public")
    # def consumer_approval(self, **kw):
    #     values = self.get_dd_config()
    #     return http.request.render("dtdream_expense_dingtalk.detail", values)
    #
    # @http.route('/dtdream_expense_dingtalk/logs', type='http', auth="public")
    # def consumer_logs(self, **kw):
    #     values = self.get_dd_config()
    #     return http.request.render("dtdream_expense_dingtalk.detail", values)

