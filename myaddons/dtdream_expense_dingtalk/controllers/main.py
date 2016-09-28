# -*- coding: utf-8 -*-
from openerp import http, models, fields, api, _
from openerp.http import request
from ..api import auth,user,message
import werkzeug, urlparse, re
from werkzeug import url_encode
from openerp.addons.web.controllers import main
import logging
import json
_logger = logging.getLogger(__name__)

class dingTalk(http.Controller):


    @http.route('/dtdream_expense_dingtalk/index', type='http', auth="public")
    def index(self, **kw):
        agentId = request.env['ir.config_parameter'].get_param('dtdream.expense.agentId', default="")
        url = request.env['ir.config_parameter'].get_param('dtdream.expense.agentUrl', default="")
        corpId = request.env['ir.config_parameter'].get_param('dtdream.dingtalk.corpId', default='')
        corpSecret = request.env['ir.config_parameter'].get_param('dtdream.dingtalk.corpSecret', default='')
        last_token = request.env['ir.config_parameter'].get_param('dtdream.dingtalk.token', default='')
        last_ticket = request.env['ir.config_parameter'].get_param('dtdream.dingtalk.ticket', default='')
        last_token_time = request.env['ir.config_parameter'].get_param('dtdream.dingtalk.time', default='')
        now_time =fields.Datetime.from_string(fields.Datetime.now())
        token = None
        ticket = None
        if last_token_time:
            last_time = fields.Datetime.from_string(last_token_time)
            _logger.info("reslut:"+str((now_time-last_time).seconds))
            if (now_time-last_time).seconds <= 7200:

                token = last_token
                ticket = last_ticket

        if not token or not ticket:
            _logger.info("corp:"+ str(corpId))
            result = auth.get_access_token(corpId, corpSecret)
            token = result[1]['access_token']
            result = auth.get_jsapi_ticket(token)
            _logger.info("result:"+ str(result))
            ticket=result[1]['ticket']
            request.env['ir.config_parameter'].sudo().set_param('dtdream.dingtalk.time', now_time)
            request.env['ir.config_parameter'].sudo().set_param('dtdream.dingtalk.token', token)
            request.env['ir.config_parameter'].sudo().set_param('dtdream.dingtalk.ticket', ticket)
        timestamp = auth.get_timestamp()

        noncestr='abcdefg'
        _logger.info("request;"+ str(request.httprequest.url))
        #url="http://dodo.tunnel.qydev.com/dtdream_expense_dingtalk/index"
        _logger.info("url:"+ url);
        url=request.httprequest.url;
        signature = auth.sign(ticket, noncestr, timestamp, url)
        values = {
            'jsticket': ticket,
            'signature': signature,
            'nonceStr': 'abcdefg',
            'timeStamp': timestamp,
            'corpId': corpId,
            'agentId': agentId,
            'token':token
        }


        return http.request.render("dtdream_expense_dingtalk.index",values)

    @http.route('/dtdream_expense_dingtalk/authUser', type='http', auth="none")
    def auth(self, **kw):

        _logger.info("kw:"+str(kw.get("access_token","")))
        token=kw.get("access_token","")
        code=kw.get("code")
        result=user.get_user_id(token,code)
        _logger.info("userId:"+ str(result))
        userid=result[1]['userid']
        _logger.info("userid:"+ str(userid))
        res_users=request.env['res.users'].sudo().search([('dd_userid','=',userid)],limit=1)
        _logger.info("users:"+ str(res_users))
        if res_users:
            res_user=res_users[0]
            uid = request.session.authenticate(request.session.db, res_user.login, userid)

            _logger.info("begin message..")
            # agentId = request.env['ir.config_parameter'].get_param('dtdream.expense.agentId', default="")
            # message.send(token,userid,'','text','hello,me too',agentId);
            _logger.info("end message..")

            _logger.info("user id;"+str(request.session.uid))
            _logger.info("uid:"+ str(uid))
            if uid:
                values={'userid': userid,'errcode':0}
            else:
                valuse={'error':u'登陆失败,请联系管理员','errcode':-1}
            _logger.info("values:"+ str(values))
            return werkzeug.wrappers.Response(json.dumps(values))

    @http.route('/dtdream_expense_dingtalk/main', type='http', auth="user")
    def expense(self, **kw):
        _logger.info("expense.....")
        # expense_ids=request.env['dtdream.expense.record'].sudo().search([])
        # result=[]
        # if expense_ids:
        #     for expense in expense_ids:
        #         expense_detail={
        #             'name':expense.name,
        #             'expensecatelog':expense.expensecatelog.name,
        #             'expensedetail':expense.expensedetail.name,
        #             'invoicevalue':expense.invoicevalue,
        #             'currentdate':expense.currentdate,
        #             'city':expense.city.name,
        #             'province':expense.province.name
        #         }
        #     result.append(expense_detail)

        # _logger.info("begin message..")
        # res_users = request.env['res.users'].sudo().browse(request.session.uid)
        # token = request.env['ir.config_parameter'].get_param('dtdream.dingtalk.token', default='')
        # agentId = request.env['ir.config_parameter'].get_param('dtdream.expense.agentId', default="")
        # url = request.env['ir.config_parameter'].get_param('dtdream.expense.agentUrl', default="")
        # # _logger.info("end message..")
        # text=u"数梦报销"
        # content=u""
        # oa = {
        #         "message_url": url,
        #         "head": {
        #             "bgcolor": "51bcec",
        #             "text": text
        #         },
        #         "body":{
        #             "form": [
        #                 {"key": u"具体信息如下:","value": ""},
        #                 {"key": u"报销人:","value": u"夏雪宜"},
        #                 {"key": u"创建时间:","value": "2016-09-16"},
        #                 {"key": u"报销金额:","value": "1000元"}
        #             ],
        #             "content": u"谁谁有个报销单待你审批"
        #         }
        # }
        # message.send(token,"0335",'','oa',oa, agentId)

        return http.request.render("dtdream_expense_dingtalk.main")
