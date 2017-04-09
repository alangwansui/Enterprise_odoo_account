#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "g0335"

from hashlib import sha1
import base64
import hmac
from datetime import *
import string, random
import urllib
import httplib
import logging

_logger = logging.getLogger(__name__)


def id_generator(size=6, chars=string.ascii_uppercase + string.digits +string.ascii_lowercase):
    return ''.join(random.choice(chars) for _ in range(size))

def percentEncode(string):
    return urllib.quote(string, safe='-_.~')

def getReqString(key, value):
    return key + "=" +value

def send_sms(recNum, smsparam, signatureVersion='1.0', version='2016-09-27',templateCode = "SMS_27380177"):
    """
    :param recNum: Target Phone number
    :param smsparam: SMS Param String with {}, {"code": "1234", "product", "dodo"}
    :param signatureVersion: default=1.0
    :param version: default=2016-09-27
    :return:
    """

    # SET YOUR ACCESS KEY ID and ACCESS KEY SECRET
    accessKeyID = "1zFWrgiAjDipR3Ge"
    accessKeySecret = "9c1ydKIbXfEMM43uqEAkhyls0fz2Lh"

    # SET Your SMS signature, must be audited
    signName = "数梦工场身份验证"

    # SET Your Template Code, must be audited


    # Random string
    signatureNonce = id_generator(16)

    # Timestamp GMT
    timestamp = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

    params = (
        ("AccessKeyId", accessKeyID),
        ("Action", "SingleSendSms"),
        ("Format", "JSON"),
        ("ParamString", smsparam),
        ("RecNum", recNum),
        ("RegionId", "cn-hangzhou"),
        ("SignName", signName),
        ("SignatureMethod", "HMAC-SHA1"),
        ("SignatureNonce", signatureNonce),
        ("SignatureVersion", signatureVersion),
        ("TemplateCode", templateCode),
        ("Timestamp", timestamp),
        ("Version", version))

    paramstr = ""
    reqstr = ""

    # Change param key and value, generate request/Paramstring
    for item in params:
        paramstr = paramstr + getReqString(percentEncode(item[0]), percentEncode(item[1]))
        paramstr += "&"
        reqstr = reqstr + getReqString(item[0], item[1])
        reqstr += "&"

    paramstr = paramstr[0:len(paramstr) - 1]
    reqstr = reqstr[0:len(reqstr) - 1]

    stringToSign = "POST" + "&" + percentEncode('/') + "&" + percentEncode(paramstr)

    # Calculate Signature, HMAC-SHA1
    secretKey = accessKeySecret + "&"
    hmac_obj = hmac.new(secretKey.encode('utf-8'), stringToSign.encode('utf-8'), sha1)
    signature = percentEncode(base64.b64encode(hmac_obj.digest()).decode('utf-8'))

    try:
        # connect sms.aliyuncs.com
        conn = httplib.HTTPSConnection('sms.aliyuncs.com')

        # Request Body
        reqbody = "Signature=" + signature + "&" + reqstr

        # Request headers
        headerdata = {
            "Content-Type": "application/x-www-form-urlencoded",
            "charset": "utf-8"
        }
        _logger.info("%s" % (reqbody))
        conn.request(method='POST', url='https://sms.aliyuncs.com/', body=reqbody, headers=headerdata)
        response = conn.getresponse()
        status = response.status
        _logger.info("%d:%s" % (response.status, response.read()))

    except Exception, e:
        status = -1
        _logger.warning("%s" % e.message)

    return status



# for example
# RecNum = "18758024833"
# smsparam = "{'code':'1234', 'product':'dodo'}"
#
# send_sms(RecNum, smsparam)
