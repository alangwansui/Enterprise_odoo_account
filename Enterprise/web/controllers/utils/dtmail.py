# -*- coding: utf-8 -*-
import uuid
import requests
import requests.exceptions
import json
import datetime

from openerp.addons.base.ir.ir_mail_server import ir_mail_server as IrMailServer
from openerp.modules.registry import RegistryManager

MAIL='''
<html>
<body>
<p>亲爱的%s,您好!</p>
<p>您于刚才提交了域账号密码重置的申请。如果不是您本人提交的操作，请直接忽略此邮件。</p>
<p>验证码为%s;请您在三分钟内完成重置。</p>
<p>谢谢！</p>
<p><a href="http://dodo.dtdream.com">数梦dodo平台</a></p>
<p>%s</p>
</body>
</html>
'''
MAIL_SUBJECT = '数梦域账号用户密码找回身份验证'

ERROR_NUM_SUCCESS = 0
ERROR_NUM_REGISTRY_ERROR = 1
ERROR_NUM_SENDMAIL_ERROR = 2


def send_mail(**kw):

    username = kw['display_name']
    code = kw['code']
    date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    body = MAIL % (username, code, date)

    mail_to = [kw['mail_to'], ]
    mail_from = kw['mail_from']
    db = kw['db_name']
    uid = kw['uid']

    try:

        registry = RegistryManager.get(db)
        ir_mail_server_obj = registry.get('ir.mail_server')
    except Exception, e:
        return ERROR_NUM_REGISTRY_ERROR

    try:
        msg = ir_mail_server_obj.build_email(
            email_from=mail_from,
            email_to=mail_to,
            subject=MAIL_SUBJECT,
            body=body,
            subtype='html'
        )

        ir_mail_server_obj.send_email(registry.cursor(), uid, msg, mail_server_id=None)

    except Exception, e:
        return ERROR_NUM_SENDMAIL_ERROR

    return ERROR_NUM_SUCCESS

# def send(**kw):
#     sn = str(uuid.uuid4())
#     url = kw['url'] + '/notify-server/rest/mail/send'
#     appkey = kw['appkey']
#     username = kw['displayname']
#
#     import code
#     code = code.generate_verification_code()
#     date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
#     mail_tmplate= MAIL % (username, code, date)
#     mailTo="gaoq@dtdream.com"
#     context = {
#             "mailTo":"%s" % mailTo,
#             "subject":"数梦域账号用户密码找回身份验证",
#             "mailMode":"0",
#             "context": "%s" % mail_tmplate
#     }
#
#     param = {'appkey':appkey, 'sn':sn, 'context':json.dumps(context)}
#     try:
#         r = requests.post(url=url, data=param)
#         result = {
#             "code":"0",
#             "message":"success operate",
#             "verify": code
#         }
#
#         print r.status_code
#         print r.text
#     except Exception, e:
#         return {
#             "code":"1004",
#             "message":e.message
#         }
#
#     if r.status_code != 200:
#         result['code'] = "1003"
#         result['message'] = "send mail failed"
#
#     retvalue = eval(r.text)
#     if retvalue['state'] != 1:
#         result['code'] = "1004"
#         result['message'] = retvalue['result']
#
#     return result