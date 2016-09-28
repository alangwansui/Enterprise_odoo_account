# -*- coding: utf-8 -*-

import requests
import requests.exceptions
import json

ERROR_NUM_SUCCESS = 0
ERROR_NUM_HTTPS_ERROR = 1
ERROR_NUM_SENDSMS_ERROR = 2


def send_ms(**kw):
    """

    :param kw:
    :return:

    kw = {
    'url':'',
    'key':'',
    'secret':
    'phone':'',
    'display_name':''
    'code':''
    }
    """

    url = kw['url']
    content = {
        'code': kw['code'],
        'product': '数梦域账号'
    }

    param = {
        'rec_num': kw['phone'],
        'sms_template_code': 'SMS_13023346',
        'sms_free_sign_name': u'身份验证',
        'sms_type': 'normal',
        'sms_param': json.dumps(content)
    }

    headers = {
        'X-Ca-Key': kw['key'],
        'X-Ca-Secret': kw['secret']
    }
    try:
        r = requests.post(url, data=param, headers=headers)

        if r.status_code != 200:
            return ERROR_NUM_HTTPS_ERROR

        info = json.JSONDecoder().decode(r.text)
        if info['success'] == False:
            return ERROR_NUM_SENDSMS_ERROR

    except Exception,e:

        return ERROR_NUM_HTTPS_ERROR

    return ERROR_NUM_SUCCESS


# def send(**kw):
#     url = 'http://localhost:8080/notify-server/rest/mail/send'
#     appkey = "6df107d18140b0fb242b4382e0c7a77a"
#     sn = str(uuid.uuid4())
#     username = "夏雪宜"
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
#     if isinstance(json.dumps(context), str) == False:
#         logging.error(type(context))
#         logging.error("Invalid type %s" % context)
#         return
#     logging.info(json.dumps(context))
#
#     param = {'appkey':appkey, 'sn':sn, 'context':json.dumps(context)}
#     r = requests.post(url=url, data=param)
#     print r.status_code
#     print r.text