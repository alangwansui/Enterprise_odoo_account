# -*- coding: utf-8 -*-
"""
create by g0335
"""


class DTError(object):
    DT_ERROR_NUM_SUCCESS = 10000
    DT_ERROR_NUM_INVALID_MAIL_PARM = 10001
    DT_ERROR_NUM_INVALID_PHONE_PARM = 10002
    DT_ERROR_NUM_REGISTRY_MAIL_FAILED = 10003
    DT_ERROR_NUM_SEND_MAIL_FAILED = 10004
    DT_ERROR_NUM_HTTPS_FAILED = 10005
    DT_ERROR_NUM_SEND_SMS_FAILED = 10006
    DT_ERROR_NUM_ERROR = 10007
    DT_ERROR_NUM_INVALID_RESET_PARAM = 10008
    DT_ERROR_NUM_INVALID_RESET_PARAM_PASS = 10009
    DT_ERROR_NUM_INVALID_RESET_PARAM_PASS_REG = 10010
    DT_ERROR_NUM_RESET_CODE_EXPIRATION = 10011
    DT_ERROR_NUM_RESET_CODE_INVALID = 10012
    DT_ERROR_NUM_LDAP_ERROR = 10013
    DT_ERROR_NUM_LDAP_BIND_FAILED = 10014
    DT_ERROR_NUM_LDAP_USER_IS_NOT_EXIST = 10015
    DT_ERROR_NUM_LDAP_MODIFY_PASSWORD_FAILED = 10016

    __error_list = [
        {"code": DT_ERROR_NUM_SUCCESS, "message": u"操作成功"},
        {"code": DT_ERROR_NUM_INVALID_MAIL_PARM, "message": u"非法参数，请检查邮箱是否正确"},
        {"code": DT_ERROR_NUM_INVALID_PHONE_PARM, "message": u"非法参数，请检查手机是否正确"},
        {"code": DT_ERROR_NUM_REGISTRY_MAIL_FAILED, "message": u"服务器内部错误，注册邮箱失败"},
        {"code": DT_ERROR_NUM_SEND_MAIL_FAILED, "message": u"服务器内部错误，邮箱发送验证码失败"},
        {"code": DT_ERROR_NUM_HTTPS_FAILED, "message": u"服务器内部错误，手机发送验证码http请求异常"},
        {"code": DT_ERROR_NUM_SEND_SMS_FAILED, "message": u"服务器内部错误，手机发送验证码失败"},
        {"code": DT_ERROR_NUM_ERROR, "message": u"服务器内部错误"},
        {"code": DT_ERROR_NUM_INVALID_RESET_PARAM, "message": u"非法参数, 请检查参数是否正确"},
        {"code": DT_ERROR_NUM_INVALID_RESET_PARAM_PASS, "message": u"非法参数, 密码不一致"},
        {"code": DT_ERROR_NUM_INVALID_RESET_PARAM_PASS_REG, "message": u"非法参数, \
        密码要符合规则:1、密码长度至少8位字符；2、同时包含大、小写字母，数字、特殊字符中的三种类型混合组成"},
        {"code": DT_ERROR_NUM_RESET_CODE_EXPIRATION, "message": u"非法参数, 验证码超时"},
        {"code": DT_ERROR_NUM_RESET_CODE_INVALID, "message": u"非法参数, 验证码不正确"},
        {"code": DT_ERROR_NUM_LDAP_ERROR, "message": u"服务器内部错误, 域控服务器连接失败"},
        {"code": DT_ERROR_NUM_LDAP_BIND_FAILED, "message": u"服务器内部错误, 域控服务器绑定失败"},
        {"code": DT_ERROR_NUM_LDAP_USER_IS_NOT_EXIST, "message": u"非法参数, 用户不存在"},
        {"code": DT_ERROR_NUM_LDAP_MODIFY_PASSWORD_FAILED, "message": u"服务器内部错误, 重置密码失败"}
    ]

    @classmethod
    def get_error_msg(cls, error_num):

        # check error_num is None
        # todo

        for i in cls.__error_list:
            if i['code'] == error_num:
                return i

        # raise error_num is not exist
        # todo