# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.osv import osv
import re
from datetime import datetime


class dtimport_dtdream_qua_man(osv.osv):
    _name = 'dtimport.dtdream.qua.man'
    _inherit = ['dtimport.wizard']

    def need_import_columns_name(self):
        return {'batchnumber': u'批次号','workid': u'申请人工号', 'manager_id': u'直接主管工号', 'last_year_result': u'绩效等级（去年）',
                'year_before_result': u'绩效等级（前年）','result_post': u'岗位', 'result_rank': u'职级'}

    def return_new_action(self):
        return {'type': 'ir.actions.act_window',
                'res_model': 'dtimport.dtdream.qua.man',
                'name': "导入",
                'view_mode': 'form',
                'view_type': 'form',
                'res_id': self.id,
                'views': [(False, 'form')],
                'target': 'new'}

    # header 是 excel 表头
    def judge_need_import_header(self, need_head, header):
        if u'岗位' in header:
            need_head = {'batchnumber': u'批次号','workid': u'申请人工号','result_post': u'岗位', 'result_rank': u'职级'}
        else:
            need_head = {'workid': u'申请人工号', 'manager_id': u'直接主管工号', 'last_year_result': u'绩效等级（去年）','year_before_result': u'绩效等级（前年）'}
        if any([True for key, val in need_head.items() if header.count(val) > 1 or header.count(val) == 0]):
            return False
        return True

    # need_head  方法need_import_columns_name的返回值 ；header 是 excel 表头
    def judge_data_is_pass(self, record, need_head, header):
        for key, val in need_head.items():
            if val not in header:
                continue
            text = record[header.index(val)]
            text = str(int(text)) if isinstance(text, float) else text
            if key in ['workid', 'manager_id']:                     #数字 工号检查
                if not text.isdigit():
                    return {'code': 1000, 'message': u'%s格式错误' % val}
                else:
                    employee = self.env['hr.employee'].search([('job_number', '=', text)]).id
                    if not employee:
                        return {'code': 1001, 'message': u'员工工号(%s)不存在' % text}
            elif key == 'batchnumber'and not re.match(u'(^RZ\d{4}0[1-9]$)|(^RZ\d{4}1[0-2]$)', text):
                return {'code': 1002, 'message': u'批次号的格式必须是RZ+年份+月份，例：RZ201503' }
        return {'code': 0, 'message': 'ok'}

    def create_or_update_records(self, data_dict):
        workid = data_dict.get('workid', '')
        manager_id = data_dict.get('manager_id','')
        last_year_result = data_dict.get('last_year_result', '')
        year_before_result = data_dict.get('year_before_result', '')
        batchnumber = data_dict.get('batchnumber', '')
        result_post = data_dict.get('result_post', '')
        result_rank = data_dict.get('result_rank', '')

        name = self.env['hr.employee'].search([('job_number', '=', workid)]).id
        manager_id = self.env['hr.employee'].search([('job_number', '=', manager_id)]).id

        record = self.env['dtdream.qualification.management'].search([('name', '=', name), ('batchnumber', '=', batchnumber)])
        if len(record)>0:
            record.write({'manager_id': manager_id or record.manager_id.id,'last_year_result': last_year_result or record.last_year_result,
                          'year_before_result': year_before_result or record.year_before_result,'batchnumber':batchnumber or record.batchnumber,
                          'result_post':result_post or record.result_post,'result_rank':result_rank or record.result_rank})
        elif name and manager_id:
            last_year_result_b = ""
            year_before_result_b = ""
            year1 = str(int(datetime.now().year) - 1) + u'财年年度'
            year2 = str(int(datetime.now().year) - 2) + u'财年年度'
            list1 = self.env["dtdream.hr.performance"].search(
                [('name', '=', name), ('quarter', 'in', (year1, year2))], order="id desc")
            if len(list1) >= 2:
                last_year_result_b = list1[0].result
                year_before_result_b = list1[1].result
            elif len(list1) == 1:
                last_year_result_b = list1[0].result
            employee = self.env['hr.employee'].search([('id', '=', name)])
            self.env['dtdream.qualification.management'].create({'batchnumber': batchnumber, 'name': name,'department_id':employee.department_id.id, 'manager_id': manager_id,
                                                                 'last_year_result': last_year_result or last_year_result_b,'year_before_result': year_before_result or year_before_result_b})