# -*- coding: utf-8 -*-


class dtdream_notice_config(object):

    #研发模块
    DTDREAM_PROD_APPR ="dtdream_prod_appr"
    DTDREAM_RD_VERSION="dtdream_rd_version"
    DTDREAM_RD_REPLANNING="dtdream.rd.replanning"
    DTDREAM_EXECPTION="dtdream_execption"
    DTDREAM_PROD_SUSPENSION ="dtdream.prod.suspension"
    DTDREAM_PROD_SUSPENSION_RESTORATION="dtdream.prod.suspension.restoration"
    DTDREAM_PROD_TERMINATION="dtdream.prod.termination"


    __conf_list = [
        {
            "model": DTDREAM_PROD_APPR,
            "fields": {'description': u'研发产品', 'shenqingren': 'create_uid', 'shenqishijian': 'create_date','dangqianzerenren': 'current_approver_user', 'state': 'state_05', 'state_name': 'state',
                       'chanpin':'name'}
        },
        {
            "model": DTDREAM_RD_VERSION,
            "fields": {'description': u'研发产品版本', 'shenqingren': 'create_uid', 'shenqishijian': 'create_date','dangqianzerenren': 'current_approver_user', 'state': 'released', 'state_name': 'version_state',
                       'chanpin': 'proName'}
        },
        {
            "model": DTDREAM_RD_REPLANNING,
            "fields": {'description': u'版本重计划', 'shenqingren': 'create_uid', 'shenqishijian': 'create_date','dangqianzerenren': 'current_approver_user', 'state': 'state_03', 'state_name': 'state',
                       'chanpin': 'proname','banben':'version'}
        },
        {
            "model": DTDREAM_EXECPTION,
            "fields": {'description': u'研发例外申请', 'shenqingren': 'create_uid', 'shenqishijian': 'create_date','dangqianzerenren': 'current_approver_user', 'state': 'ysp', 'state_name': 'state',
                       'chanpin':'name','banben':'version'}
        },
        {
            "model": DTDREAM_PROD_SUSPENSION,
            "fields": {'description': u'研发暂停申请', 'shenqingren': 'create_uid', 'shenqishijian': 'create_date', 'dangqianzerenren': 'current_approver_user', 'state': 'ysp', 'state_name': 'state',
                       'chanpin':'project','banben':'version'}
        },
        {
            "model": DTDREAM_PROD_SUSPENSION_RESTORATION,
            "fields": {'description': u'研发恢复暂停申请', 'shenqingren': 'create_uid', 'shenqishijian': 'create_date','dangqianzerenren': 'current_approver_user', 'state': 'ysp', 'state_name': 'state',
                       'chanpin': 'project','banben':'version'}
        },
        {
            "model": DTDREAM_PROD_TERMINATION,
            "fields": {'description': u'研发中止申请', 'shenqingren': 'create_uid', 'shenqishijian': 'create_date','dangqianzerenren': 'current_approver_user', 'state': 'ysp', 'state_name': 'state',
                       'chanpin': 'project','banben':'version'}
        },
    ]

    @classmethod
    def get_fields_by_model(cls, model_name):

        for i in cls.__conf_list:
            if i['model'] == model_name:
                return i
        return False

        # raise Exception('Error: %s is not exist' % model_name)

    def get_config_model_list(self):
        return [{'model': item["model"], 'shenqingren': item['fields']['shenqingren'], 'state': item['fields']['state'], 'state_name': item['fields']['state_name']} for item in self.__conf_list]

