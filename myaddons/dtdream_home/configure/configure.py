# -*- coding: utf-8 -*-


class dtdream_notice_config(object):

    # 费用报销模型
    DTDREAM_EXPENSE_REPORT = "dtdream.expense.report"
    #研发模块
    DTDREAM_PROD_APPR ="dtdream_prod_appr"
    DTDREAM_RD_VERSION="dtdream_rd_version"
    DTDREAM_RD_REPLANNING="dtdream.rd.replanning"
    DTDREAM_EXECPTION="dtdream_execption"
    DTDREAM_PROD_SUSPENSION ="dtdream.prod.suspension"
    DTDREAM_PROD_SUSPENSION_RESTORATION="dtdream.prod.suspension.restoration"
    DTDREAM_PROD_TERMINATION="dtdream.prod.termination"

    #外出公干
    DTDREAM_HR_BUSINESS="dtdream_hr_business.dtdream_hr_business"

    #专项审批
    DTDREAM_SPECIAL_APPROVAL='dtdream.special.approval'

    #出差
    DTDREAM_TRAVEL_CHUCHA= 'dtdream.travel.chucha'

    #报备
    #DTDREAM_SALE_BUSINESS_REPORT = 'dtdream.sale.business.report'//未上线

    #休假
    HR_HOLIDAYS = 'hr.holidays'

    #预算
    DTDREAM_BUDGET = 'dtdream.budget'

    #合同评审
    DTDREAM_CONTRACT = 'dtdream.contract'

    #客户接待
    DTDREAM_CUSTOMER_RECEPTION = 'dtdream.customer.reception'

    #IT需求
    DTDREAM_DEMAND_APP = 'dtdream.demand.app'

    #离职
    LEAVING_HANDLE = 'leaving.handle'

    #履历
    DTDREAM_HR_RESUME = 'dtdream.hr.resume'

    #履历修改
    DTDREAM_HR_RESUME_MODIFY = 'dtdream.hr.resume.modify'

    #绩效
    DTDREAM_HR_PERFORMANCE = 'dtdream.hr.performance'


    __conf_list = [
        {
            "model": DTDREAM_EXPENSE_REPORT,
            "fields": {'description': u'费用报销', 'shenqingren': 'create_uid_self', 'shenqishijian': 'write_date', 'dangqianzerenren': 'currentauditperson', 'state': 'yifukuan', 'state_name': 'state'
                       ,'stateList':("yifukuan","draft")}
        },
        {
            "model": DTDREAM_PROD_APPR,
            "fields": {'description': u'研发产品', 'shenqingren': 'PDT', 'shenqishijian': 'write_date','dangqianzerenren': 'current_approver_user', 'state': 'state_05', 'state_name': 'state'
                    , 'stateList': ("state_05","state_00")}
        },
        {
            "model": DTDREAM_RD_VERSION,
            "fields": {'description': u'研发版本', 'shenqingren': 'PDT', 'shenqishijian': 'write_date','dangqianzerenren': 'current_approver_user', 'state': 'released', 'state_name': 'version_state'
                , 'stateList': ("released","draft")}
        },
        {
            "model": DTDREAM_RD_REPLANNING,
            "fields": {'description': u'版本重计划', 'shenqingren': 'create_uid', 'shenqishijian': 'write_date','dangqianzerenren': 'current_approver_user', 'state': 'state_03', 'state_name': 'state'
                , 'stateList': ("state_01","state_03")}
        },
        {
            "model": DTDREAM_EXECPTION,
            "fields": {'description': u'研发例外申请', 'shenqingren': 'create_uid', 'shenqishijian': 'write_date','dangqianzerenren': 'current_approver_user', 'state': 'ysp', 'state_name': 'state'
                , 'stateList': ("ysp","dsp")}
        },
        {
            "model": DTDREAM_PROD_SUSPENSION,
            "fields": {'description': u'研发暂停申请', 'shenqingren': 'create_uid', 'shenqishijian': 'write_date', 'dangqianzerenren': 'current_approver_user', 'state': 'ysp', 'state_name': 'state'
                       , 'stateList': ("ysp","cg")}
        },
        {
            "model": DTDREAM_PROD_SUSPENSION_RESTORATION,
            "fields": {'description': u'研发恢复暂停申请', 'shenqingren': 'create_uid', 'shenqishijian': 'write_date','dangqianzerenren': 'current_approver_user', 'state': 'ysp', 'state_name': 'state'
                        , 'stateList': ("ysp","cg")}
        },
        {
            "model": DTDREAM_PROD_TERMINATION,
            "fields": {'description': u'研发中止申请', 'shenqingren': 'create_uid', 'shenqishijian': 'write_date','dangqianzerenren': 'current_approver_user', 'state': 'ysp', 'state_name': 'state'
                , 'stateList': ("ysp","cg")}
        },
        {
            "model": DTDREAM_TRAVEL_CHUCHA,
            "fields": {'description': u'出差', 'shenqingren': 'name', 'shenqishijian': 'write_date','dangqianzerenren': 'shenpiren', 'state': '99', 'state_name': 'state'
                , 'stateList': ("99","0")}
        },
        {
            "model": DTDREAM_HR_BUSINESS,
            "fields": {'description': u'外出公干', 'shenqingren': 'name', 'shenqishijian': 'write_date','dangqianzerenren': 'current_approver', 'state': '5', 'state_name': 'state'
                , 'stateList': ("5","-8")}
        },
        {
            "model": DTDREAM_SPECIAL_APPROVAL,
            "fields": {'description': u'专项审批', 'shenqingren': 'applicant', 'shenqishijian': 'write_date','dangqianzerenren': 'current_approver_user', 'state': 'state_05', 'state_name': 'state'
                , 'stateList': ("state_05","state_01")}
        },
        {
            "model": HR_HOLIDAYS,
            "fields": {'description': u'休假', 'shenqingren': 'employee_id', 'shenqishijian': 'write_date','dangqianzerenren': 'current_shenpiren', 'state': 'validate', 'state_name': 'state'
                , 'stateList': ("validate","draft")}
        },
        {
            "model": DTDREAM_BUDGET,
            "fields": {'description': u'预算管理', 'shenqingren': 'applicant', 'shenqishijian': 'write_date','dangqianzerenren': 'current_handler', 'state': '4', 'state_name': 'state'
                , 'stateList': ("4","0")}
        },
        {
            "model": DTDREAM_CONTRACT,
            "fields": {'description': u'合同评审', 'shenqingren': 'applicant', 'shenqishijian': 'write_date','dangqianzerenren': 'current_handler_ids', 'state': '9', 'state_name': 'state'
                , 'stateList': ("9","0")}
        },
        {
            "model": DTDREAM_CUSTOMER_RECEPTION,
            "fields": {'description': u'客户接待', 'shenqingren': 'name', 'shenqishijian': 'write_date','dangqianzerenren': 'current_approve', 'state': '99', 'state_name': 'state'
                , 'stateList': ("99","0")}
        },
        {
            "model": DTDREAM_DEMAND_APP,
            "fields": {'description': u'IT需求', 'shenqingren': 'name', 'shenqishijian': 'write_date','dangqianzerenren': 'current_approve', 'state': '99', 'state_name': 'state'
                , 'stateList': ("99","0")}
        },
        {
            "model": LEAVING_HANDLE,
            "fields": {'description': u'离职办理', 'shenqingren': 'name', 'shenqishijian': 'write_date','dangqianzerenren': 'cur_approvers', 'state': '99', 'state_name': 'state'
                , 'stateList': ("99","0")}
        },
        {
            "model": DTDREAM_HR_RESUME,
            "fields": {'description': u'员工履历', 'shenqingren': 'name', 'shenqishijian': 'write_date','dangqianzerenren': 'resume_approve', 'state': '99', 'state_name': 'state'
                , 'stateList': ("99","0")}
        },
        {
            "model": DTDREAM_HR_RESUME_MODIFY,
            "fields": {'description': u'履历修改', 'shenqingren': 'name', 'shenqishijian': 'write_date','dangqianzerenren': 'resume_approve', 'state': '99', 'state_name': 'state'
                , 'stateList': ("99","0")}
        },
        {
            "model": DTDREAM_HR_PERFORMANCE,
            "fields": {'description': u'绩效', 'shenqingren': 'name', 'shenqishijian': 'write_date','dangqianzerenren': 'resume_approve', 'state': '99', 'state_name': 'state'
                , 'stateList': ("99","0")}
        },
        # {
        #     "model": DTDREAM_SALE_BUSINESS_REPORT,
        #     "fields": {'description': u'商务提前报备', 'shenqingren': 'apply_person', 'shenqishijian': 'create_date','dangqianzerenren': 'shenpiren', 'state': 'done', 'state_name': 'state'}
        # },

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

