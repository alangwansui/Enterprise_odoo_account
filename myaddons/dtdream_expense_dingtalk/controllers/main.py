# -*- coding: utf-8 -*-
from openerp import http, fields
from openerp.http import request
from ..api import auth, user
import werkzeug
import logging
import json
_logger = logging.getLogger(__name__)


def get_data_from_redis():
    import redis
    import openerp
    values = {
        "token": None,
        "ticket": None,
        "time": None
    }

    try:
        redis_host = openerp.tools.config['redis_host']
        redis_port = openerp.tools.config['redis_port']
        redis_pass = openerp.tools.config['redis_pass']
        r = redis.Redis(host=redis_host, password=redis_pass, port=redis_port, db=0)
        if r.get("dtdream.dingtalk.token"):
            values['token'] = r.get("dtdream.dingtalk.token")
        if r.get("dtdream.dingtalk.ticket"):
            values['ticket'] = r.get("dtdream.dingtalk.ticket")
        if r.get("dtdream.dingtalk.time"):
            values['time'] = r.get("dtdream.dingtalk.time")
    except Exception, e:
        _logger.error("get data to redis failed:%s" % e.message)
        pass
    return values


def set_data_to_redis(**kw):
    import redis
    import openerp
    try:
        redis_host = openerp.tools.config['redis_host']
        redis_port = openerp.tools.config['redis_port']
        redis_pass = openerp.tools.config['redis_pass']
        r = redis.Redis(host=redis_host, password=redis_pass, port=redis_port, db=0)
        if kw['token']:
            r.set("dtdream.dingtalk.token", kw['token'])
        else:
            r.delete("dtdream.dingtalk.token")

        if kw['ticket']:
            r.set("dtdream.dingtalk.ticket", kw['ticket'])
        else:
            r.delete("dtdream.dingtalk.ticket")

        if kw['time']:
            r.set("dtdream.dingtalk.time", kw['time'])
        else:
            r.delete("dtdream.dingtalk.time")

        r.save()
    except Exception, e:
        _logger.error("set data to redis failed:%s" % e.message)
        pass
    return


def get_dd_config():
    agentId = request.env['ir.config_parameter'].get_param('dtdream.expense.agentId', default="")
    url = request.env['ir.config_parameter'].get_param('dtdream.expense.agentUrl', default="")
    corpId = request.env['ir.config_parameter'].get_param('dtdream.dingtalk.corpId', default='')
    corpSecret = request.env['ir.config_parameter'].get_param('dtdream.dingtalk.corpSecret', default='')

    values = get_data_from_redis()
    last_token_time = values["time"]
    last_ticket = values['ticket']
    last_token = values['token']

    now_time = fields.Datetime.from_string(fields.Datetime.now())
    token = None
    ticket = None
    if last_token_time:
        last_time = fields.Datetime.from_string(last_token_time)
        _logger.info("result:" + str((now_time - last_time).seconds))
        if (now_time - last_time).seconds <= 7200:
            token = last_token
            ticket = last_ticket
    if not token or not ticket:
        result = auth.get_access_token(corpId, corpSecret)
        token = result[1]['access_token']
        result = auth.get_jsapi_ticket(token)
        ticket = result[1]['ticket']

        _logger.info("corp:" + str(corpId))
        _logger.info("result:" + str(result))

        values['token'] = token
        values['ticket'] = ticket
        values['time'] = now_time
        set_data_to_redis(**values)

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


class dingTalk(http.Controller):

    @http.route('/dtdream_expense_dingtalk/index', type='http', auth="public")
    def index(self, **kw):
        values = get_dd_config()
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

    @http.route('/dtdream_expense_dingtalk/help', type='http', auth="public")
    def consumer_help(self, **kw):
        # values = get_dd_config()
        values = {}
        return http.request.render("dtdream_expense_dingtalk.help", values)

    @http.route('/dtdream_expense_dingtalk/my', type='http', auth="public")
    def consumer_my(self, **kw):
        values = get_dd_config()
        return http.request.render("dtdream_expense_dingtalk.detail", values)
