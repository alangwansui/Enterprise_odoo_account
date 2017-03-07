# -*- coding: utf-8 -*-
from openerp import models, fields, api
import datetime
import openerp

class dtdream_verification_code(models.Model):
    _name = 'dtdream.verification.code'
    _description = u"验证表"
    login= fields.Char(string="帐号")
    key = fields.Char(string="验证码")
    time = fields.Datetime(string="时间")



    @api.model
    def save_verification_code(self,login=None,sn=None):
        vals={
            'login':login,
            'key':sn,
            'time':datetime.datetime.now()
        }
        result = super(dtdream_verification_code, self).create(vals)
        if result.id:
            return True
        return False

    #检验验证码
    @api.model
    def check_verification_code(self,login=None,sn=None):
        try:
            deadline = openerp.tools.config['deadline']
        except Exception,e:
            deadline=5
        code = self.env['dtdream.verification.code'].search([('login','=',login)],limit=1,order="id desc")
        if code and code.key==sn:
            betweenTime = (datetime.datetime.now() - datetime.datetime.strptime(str(code.time), "%Y-%m-%d %H:%M:%S"))
            if betweenTime.days>0:
                return {'code': 10001, 'message': u'验证码失效,请重新获取'}
            if betweenTime.seconds>int(deadline)*60:
                return {'code': 10001, 'message': u'验证码失效,请重新获取'}
            else:
                code.write({'time':datetime.datetime.now()})
                return {'code':10000,'message':u'验证成功'}
        else:
            return {'code': 10002, 'message': u'验证码输入错误，请重新输入'}

    #获取上次登录时间
    @api.model
    def get_statistics_time(self,login=None):
        list = self.env['dtdream.verification.code'].search([('login', '=', login)],order="id desc")
        if len(list)==1:
            res = {
                "times": len(list),
                "previous_date": list[0].time[:10],
            }
        else:
            res = {
                "times": len(list),
                "previous_date": list[1].time[:10],
            }
        return res