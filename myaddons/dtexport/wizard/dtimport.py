# -*- coding: utf-8 -*-

from openerp import fields, api
from openerp.osv import osv
import xlrd
import StringIO
import base64


class dtimport_wizard(osv.osv):
    _name = 'dtimport.wizard'

    imported = fields.Integer('有效条数', readonly=True)
    to_import = fields.Text('需要导入的有效条目')
    filename = fields.Char()
    data = fields.Binary(string='请选择上传文件')
    state = fields.Selection([('1', '1'), ('2', '2')], string='状态', default='1')

    def need_import_columns_name(self):
        pass

    def judge_data_is_pass(self, record, need_head, header):
        pass

    def return_new_action(self):
        pass

    def create_or_update_records(self, data_dict):
        pass

    @api.multi
    def button_next(self):
        if not self.data:
            raise osv.except_osv(u'错误', u'请先上传导入文件!')
        xls_file = StringIO.StringIO(base64.decodestring(self.data))
        try:
            workbook = xlrd.open_workbook(file_contents=xls_file.read())
        except Exception, e:
            raise osv.except_osv(u'错误', u'文件格式必须是Excel!')
        worksheet = workbook.sheets()[0]
        need_head = (self.need_import_columns_name())
        to_import = []
        nrows = worksheet.nrows
        for i in range(nrows):
            record = worksheet.row_values(i)
            if i == 0:
                header = record
                if any([True for key, val in need_head.items() if header.count(val) > 1 or header.count(val) == 0]):
                    raise osv.except_osv(u'错误', u'需要导入字段未导入或者导入字段重复，请重新上传!')
            else:
                if all([record[header.index(val)] for key, val in need_head.items() if key != 'result']):
                    result = self.judge_data_is_pass(record, need_head, header)
                    if result.get('code') != 0:
                        raise osv.except_osv(u'错误', u'行号: ' + str(i) + u', 错误信息: ' + result.get('message'))
                    to_import.append({key: record[header.index(val)] for key, val in need_head.items()})
        imported = len(to_import)
        vals = {'state': '2',
                'imported': imported,
                'to_import': to_import}
        self.write(vals)
        return self.return_new_action()

    @api.one
    def button_ok(self):
        to_import = eval(self.to_import)
        if not to_import:
            raise osv.except_osv(u"错误", u"文件中没有需要导入的行")
        for data_dict in to_import:
            self.create_or_update_records(data_dict)


















