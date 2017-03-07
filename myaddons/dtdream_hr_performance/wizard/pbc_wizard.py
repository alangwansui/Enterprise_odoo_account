# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.osv import osv
import re


class Wizard_reject(models.TransientModel):
    _name = 'dtdream.hr.performance.reject.wizard'

    liyou = fields.Text("理由", required=True)

    @api.one
    def btn_confirm(self):
        # 将理由发送到chatter
        performance = self.env['dtdream.hr.performance'].browse(self._context['active_id'])
        performance.message_post(body=u"返回修改," + u"理由:" + self.liyou)
        performance.signal_workflow('btn_revise')


class Wizard_agree(models.TransientModel):
    _name = 'dtdream.hr.performance.agree.wizard'

    liyou = fields.Text("意见")

    @api.one
    def btn_confirm(self):
        # 将理由发送到chatter
        performance = self.env['dtdream.hr.performance'].browse(self._context['active_id'])
        if self.liyou:
            body = u"同意," + u"建议:" + self.liyou
        else:
            body = u"同意"
        performance.message_post(body=body)
        performance.signal_workflow('btn_agree')


class dtimport_hr_performance(osv.osv):
    _name = 'dtimport.hr.performance'
    _inherit = ['dtimport.wizard']

    def need_import_columns_name(self):
        return {'workid': u'工号', 'quarter': u'考核季度', 'officer': u'一考主管', 'officer_sec': u'二考主管',
                'time_range': u'考核时间范围', 'result': u'考核结果'}

    def return_new_action(self):
        return {'type': 'ir.actions.act_window',
                'res_model': 'dtimport.hr.performance',
                'name': "导入",
                'view_mode': 'form',
                'view_type': 'form',
                'res_id': self.id,
                'views': [(False, 'form')],
                'target': 'new'}

    def judge_need_import_header(self, need_head, header):
        if u'考核结果' in header:
            need_head = {'workid': u'工号',  'quarter': u'考核季度', 'result': u'考核结果'}
        else:
            need_head = {'workid': u'工号', 'quarter': u'考核季度', 'officer': u'一考主管', 'officer_sec': u'二考主管',
                         'time_range': u'考核时间范围'}
        if any([True for key, val in need_head.items() if header.count(val) > 1 or header.count(val) == 0]):
            return False
        return True

    def judge_data_is_pass(self, record, need_head, header):
        for key, val in need_head.items():
            if val not in header:
                continue
            text = record[header.index(val)]
            text = str(int(text)) if isinstance(text, float) else text
            if key in ['workid', 'officer', 'officer_sec']:
                if not text.isdigit():
                    return {'code': 1000, 'message': u'%s格式错误' % val}
                else:
                    employee = self.env['hr.employee'].search([('job_number', '=', text)]).id
                    if not employee:
                        return {'code': 1001, 'message': u'员工工号(%s)不存在' % text}
            elif key == 'quarter'and not re.match(u'(^\d{4}财年Q[1-4]$)|(^\d{4}财年年度$)', text):
                return {'code': 1002, 'message': u'考核季度的格式必须是XXXX财年Q1~Q4，' +
                                                 u'或XXXX财年年度；如2016财年Q1，或2016财年年度'}
            elif key == 'time_range' and text not in ('1', '2', '3', '4', '5'):
                return {'code': 1003, 'message': u'考核时间格式不正确,取值需在("1", "2", "3", "4", "5")中'}
        return {'code': 0, 'message': 'ok'}

    def create_or_update_records(self, data_dict):
        workid = data_dict.get('workid', '')
        quarter = data_dict.get('quarter', '')
        result = data_dict.get('result', '')
        time_range = data_dict.get('time_range', '')
        time_range = str(int(time_range)) if isinstance(time_range, float) else time_range
        name = self.env['hr.employee'].search([('job_number', '=', workid)]).id
        officer = self.env['hr.employee'].search([('job_number', '=', data_dict.get('officer', ''))]).id
        officer_sec = self.env['hr.employee'].search([('job_number', '=', data_dict.get('officer_sec', ''))]).id
        record = self.env['dtdream.hr.performance'].search([('name', '=', name), ('quarter', '=', quarter)])
        if record:
            record.write({'quarter': quarter or record.quarter, 'time_range': time_range or record.time_range,
                          'result': result or record.result, 'officer': officer or record.officer.id, 'officer_sec':
                              officer_sec or record.officer_sec.id})
        elif quarter and time_range and name and officer and officer_sec:
            self.env['dtdream.hr.performance'].create({'name': name, 'quarter': quarter, 'officer': officer,
                                                       'time_range': time_range, 'officer_sec': officer_sec})




