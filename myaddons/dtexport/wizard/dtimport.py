# -*- coding: utf-8 -*-

from openerp import fields, api
from openerp.osv import osv
import xlwt
import xlrd
import StringIO
import base64


class dtexport_wizard(osv.osv):
    _name = 'dtexport.wizard'

    selected = fields.Integer('当前已选', readonly=True, default=lambda s, c, u, ctx: len(ctx.get('active_ids')))
    exported = fields.Integer('之前已导入', readonly=True)
    filename = fields.Char('文件名', readonly=True)
    data = fields.Binary('文件', readonly=True)
    state = fields.Selection([('1', '1'), ('2', '2')], string='状态', default='1')

    def model_fields_data_provide(self):
        pass

    @api.multi
    def model_export_data_header_field(self, selected):
        model_obj, fields_list_tuple = self.model_fields_data_provide()
        to_export_ids = model_obj.search([('id', 'in', selected)])
        exported = len(self._context.get('active_ids')) - len(to_export_ids)
        export_data = model_obj.export_data(selected, [field_name for field_name, fields_string in
                                                       fields_list_tuple]).get('datas', [])
        return fields_list_tuple, export_data, exported, to_export_ids

    def return_vals_construction(self, exported, this_id, out, to_export_ids):
        pass

    @api.one
    def button_next(self):
        this_id = self._context.get('active_id')
        xls = StringIO.StringIO()
        xls_workbook = xlwt.Workbook(encoding='utf8')
        data_sheet = xls_workbook.add_sheet('data')
        selected = self._context.get('active_ids')
        fields_list_tuple, export_data, exported, to_export_ids = self.model_export_data_header_field(selected)
        for index, (field_name, fields_string) in enumerate(fields_list_tuple):
            data_sheet.write(0, index, fields_string)
        for row, records in enumerate(export_data):
            for column, record in enumerate(records):
                export_value = str(record or " ")
                data_sheet.write(row+1, column, export_value)
        xls_workbook.save(xls)
        xls.seek(0)
        out = base64.encodestring(xls.getvalue())
        return self.return_vals_construction(exported, this_id, out, to_export_ids)


class dtimport_wizard(osv.osv):
    _name = 'dtimport.wizard'

    selected = fields.Integer('总导入条数', readonly=True)
    imported = fields.Integer('有效条数', readonly=True)
    to_import = fields.Text('需要导入的有效条目')
    filename = fields.Char(string='12')
    data = fields.Binary(string='请选择上传文件')
    state = fields.Selection([('1', '1'), ('2', '2')], string='状态', default='1')

    def need_column_date_header(self):
        pass

    def judge_data_is_pass(self, record, need_head, header):
        pass

    @api.one
    def return_vals_action(self):
        pass

    def judge_and_write_vals(self, data_dict):
        pass

    @api.one
    def button_next(self):
        xls_file = StringIO.StringIO(base64.decodestring(self.data))
        workbook = xlrd.open_workbook(file_contents=xls_file.read())
        worksheet = workbook.sheets()[0]
        need_head = (self.need_column_date_header())
        selected = 0
        to_import = []
        nrows = worksheet.nrows
        for i in range(nrows):
            selected += 1
            record = worksheet.row_values(i)
            if i == 0:
                header = record
                if any([True for key, val in need_head.items() if header.count(val) > 1 or header.count(val) == 0]):
                    raise osv.except_osv(u'错误', u'需要导入字段未导入或者导入字段重复，请重新上传!')
            else:
                if all([record[header.index(val)] for key, val in need_head.items() if key != 'result']):
                    self.judge_data_is_pass(record, need_head, header)
                    to_import.append({key: record[header.index(val)] for key, val in need_head.items()})
        if selected > 0:
            selected -= 1
        imported = len(to_import)
        vals = {'state': '2',
                'selected': selected,
                'imported': imported,
                'to_import': to_import}
        self.write(vals)
        return self.return_vals_action()

    @api.one
    def button_ok(self):
        to_import = eval(self.to_import)
        if not to_import:
            raise osv.except_osv(u"错误", u"文件中没有需要导入的行")
        for data_dict in to_import:
            self.judge_and_write_vals(data_dict)
        return True


















