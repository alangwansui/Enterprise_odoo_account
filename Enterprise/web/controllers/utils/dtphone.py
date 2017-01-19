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


def send_sms_aliyun(**kw):
    from openerp.dtdream.aliyun.sms import send_sms
    recNum = kw['phone'].encode('utf-8')
    smsparam = ("{'code': '%s','product': 'dodo'}" % kw['code']).encode('utf-8')
    status = send_sms(recNum, smsparam)

    if status == 200:
        return ERROR_NUM_SUCCESS
    elif status == -1:
        return ERROR_NUM_HTTPS_ERROR
    else:
        return ERROR_NUM_SENDSMS_ERROR
