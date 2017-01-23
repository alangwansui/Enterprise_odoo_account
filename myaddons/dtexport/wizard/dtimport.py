# -*- coding: utf-8 -*-

from openerp import fields
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

    def model_fields_data_provide(self, cr, uid, context=None):
        pass

    def model_export_data_header_field(self, cr, uid, selected, context=None):
        model_obj, fields_list_tuple = self.model_fields_data_provide(cr, uid, context=context)
        to_export_ids = model_obj.search(cr, uid, [('id', 'in', selected)], context=context)
        exported = len(context.get('active_ids')) - len(to_export_ids)
        export_data = model_obj.export_data(cr, uid, selected, [field_name for field_name, fields_string in
                                                                fields_list_tuple], context=context).get('datas', [])
        return fields_list_tuple, export_data, exported, to_export_ids

    def return_vals_construction(self, cr, uid, ids, exported, this_id, out, to_export_ids, context=None):
        pass

    def button_next(self, cr, uid, ids, context=None):
        context = {} if not context else context
        this_id = ids if isinstance(ids, int) else ids[0]
        xls = StringIO.StringIO()
        xls_workbook = xlwt.Workbook(encoding='utf8')
        data_sheet = xls_workbook.add_sheet('data')
        selected = context.get('active_ids')
        fields_list_tuple, export_data, exported, to_export_ids = self.model_export_data_header_field(
            cr, uid, selected, context=context)
        for index, (field_name, fields_string) in enumerate(fields_list_tuple):
            data_sheet.write(0, index, fields_string)
        for row, records in enumerate(export_data):
            for column, record in enumerate(records):
                export_value = str(record or " ")
                data_sheet.write(row+1, column, export_value)
        xls_workbook.save(xls)
        xls.seek(0)
        out = base64.encodestring(xls.getvalue())
        return self.return_vals_construction(cr, uid, ids, exported, this_id, out, to_export_ids, context=context)


class dtimport_wizard(osv.osv):
    _name = 'dtimport.wizard'

    selected = fields.Integer('总导入条数', readonly=True)
    imported = fields.Integer('有效条数', readonly=True)
    to_import = fields.Text('需要导入的有效条目')
    filename = fields.Char(string='12')
    data = fields.Binary(string='请选择上传文件')
    state = fields.Selection([('1', '1'), ('2', '2')], string='状态', default='1')

    def need_column_date_header(self, cr, uid, context=None):
        pass

    def judge_data_is_pass(self, cr, uid, ids, record, need_head, context=None):
        pass

    def return_vals_action(self, cr, uid, ids, this_id, context=None):
        pass

    def judge_and_write_vals(self, cr, uid, ids, data_dict, context=None):
        pass

    def button_next(self, cr, uid, ids, context=None):
        context = {} if not context else context
        this_id = ids if isinstance(ids, int) else ids[0]
        this = self.browse(cr, uid, ids, context)[0]
        xls_file = StringIO.StringIO(base64.decodestring(this.data))
        workbook = xlrd.open_workbook(file_contents=xls_file.read())
        worksheet = workbook.sheets()[0]
        need_head = (self.need_column_date_header(cr, uid, context=context))
        selected = 0
        to_import = []
        nrows = worksheet.nrows
        for i in range(nrows):
            selected += 1
            record = worksheet.row_values(i)
            if i == 0:
                header = record
                if any([True for key, val in need_head.items() if header.count(val) > 1 or header.count(val) == 0]):
                    raise osv.except_osv(u'错误', u'文件格式有误，请重新上传!')
            else:
                if all([record[header.index(val)] for key, val in need_head.items()]):
                    self.judge_data_is_pass(cr, uid, ids, record, need_head, context=context)
                    to_import.append({key: record[header.index(val)] for key, val in need_head.items()})
        if selected > 0:
            selected -= 1
        imported = len(to_import)
        vals = {'state': '2',
                'selected': selected,
                'imported': imported,
                'to_import': to_import}
        self.write(cr, uid, ids, vals, context=context)
        return self.return_vals_action(cr, uid, ids, this_id, context=context)

    def button_ok(self, cr, uid, ids, context=None):
        to_import = eval(self.browse(cr, uid, ids, context=context).to_import)
        if not to_import:
            raise osv.except_osv(u"错误", u"文件中没有需要导入的行")
        for data_dict in to_import:
            self.judge_and_write_vals(cr, uid, ids, data_dict, context=context)
        return True


















