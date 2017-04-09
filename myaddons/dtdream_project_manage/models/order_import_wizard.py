# -*- coding: utf-8 -*-

from openerp.osv import osv


class dtimport_project_manage(osv.osv):
    _name = 'dtimport.project.manage'
    _inherit = ['dtimport.wizard']

    def need_import_columns_name(self):
        return {'code': u'订单编号', 'order_type': u'订单类型', 'bom': u'BOM', 'version': u'型号',
                'product_type': u'产品类别', 'product_des': u'产品描述', 'company': u'单位', 'vender': u'生产厂家',
                'num': u'数量', 'need_price': u'应收金额', 'actual_price': u'实收金额'}

    def return_new_action(self):
        return {'type': 'ir.actions.act_window',
                'res_model': 'dtimport.project.manage',
                'name': "导入",
                'view_mode': 'form',
                'view_type': 'form',
                'res_id': self.id,
                'views': [(False, 'form')],
                'context': self._context,
                'target': 'new'}

    def judge_need_import_header(self, need_head, header):
        if any([True for key, val in need_head.items() if header.count(val) > 1 or header.count(val) == 0]):
            return False
        return True

    def judge_data_is_pass(self, record, need_head, header):
        for key, val in need_head.items():
            if val not in header:
                continue
            text = record[header.index(val)]
            if not text:
                continue
            if key == 'num':
                text = str(int(text)) if isinstance(text, float) else text
                if not str(text).isdigit():
                    return {'code': 1000, 'message': u'%s格式错误' % val}
            if key in ['code', 'order_type', 'bom', 'version', 'product_type', 'product_des', 'company', 'vender'] and not text:
                return {'code': 1001, 'message': u'%s不能为空' % val}
            if key in ['need_price', 'actual_price']:
                try:
                    text = float(text)
                except Exception, e:
                    return {'code': 1002, 'message': u'%s格式错误' % val}

        return {'code': 0, 'message': 'ok'}

    def create_or_update_records(self, data_dict):
        code = data_dict.get('code', '')
        order_type = data_dict.get('order_type', '')
        bom = data_dict.get('bom', '')
        version = data_dict.get('version', '')
        product_type = data_dict.get('product_type', '')
        product_des = data_dict.get('product_des', '')
        company = data_dict.get('company', '')
        vender = data_dict.get('vender', '')
        num = data_dict.get('num', '')
        need_price = data_dict.get('need_price', '')
        actual_price = data_dict.get('actual_price', '')
        self.env['dtdream.project.order'].create({'code': code, 'order_type': order_type, 'bom': bom,
                                                  'version': version, 'product_type': product_type,
                                                  'product_des': product_des, 'company': company,
                                                  'actual_price': actual_price, 'need_price': need_price,
                                                  'vender': vender, 'num': num, 'project_manage_id': self._context.get('active_id')})

