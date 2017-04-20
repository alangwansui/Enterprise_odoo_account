# -*- coding: utf-8 -*-
from openerp import http
from openerp.http import request,serialize_exception
from openerp.addons.web.controllers.main import ExcelExport
from datetime import datetime
from openerp.exceptions import ValidationError


class DtdreamExpense(ExcelExport):
    @http.route('/dtdream_reserve_fund/dtdream_reserve_export', type='http',auth='public')
    def dtdream_reserve_export(self, data, token):
        index = 0
        pay_type = {u"付款给员工": u"借", u"付款给供应商": u"借付"}
        active_ids = data.split(',')
        batch_prefix = 'DC'+datetime.strftime(datetime.today(),"%Y%m")[-4:]
        max_batch = request.env['dtdream.expense.report'].sudo().search([('batch','like',batch_prefix+'%')],order='batch desc',limit=1).batch
        if max_batch and int(max_batch[-4:]) < 9999:
            batch = 'DC'+str(int(max_batch[-8:])+1)
        elif max_batch and int(max_batch[-4:]) == 9999:
            raise ValidationError("当月导出数量已达到最大值")
        elif not max_batch:
            batch = batch_prefix+'0001'
        period = datetime.strftime(datetime.today(),"%Y/%m/%d")
        gl_date = period
        excel_header = ['NO', 'BATCH', 'PERIOD', 'GL_DATE', 'VENDOR_NUM', 'VENDOR_NAME',
                        'INVOICE_CODE', 'INVOICE_TYPE', 'COMPANY', 'CSTCENTER', 'ACCOUNT',
                        'ACCOUNT DESCRIPTION', 'TYPE', 'DESCRIPTION', 'PRODUCT', 'REGION',
                        'BM', 'SM', 'IC', 'SPARE', 'CURRENCY', 'ACCOUNTED_DR', 'ACCOUNTED_CR', 'NET_AMOUNT']
        excel_values = []
        excel_values.append([u'序号', u'批名', u'日期', u'财务日期', u'工号', u'姓名', u'备用金单号', u'模块', u'公司套账', u'成本中心',
                             u'会计科目', u'会计科目名称', u'支付方式', u'摘要', u'产品编码', u'销售区域','',u'销售模式',u'关联公司',
                             u'备用', u'币种', u'借方金额', u'贷方金额', u'净值'])
        for i in range(len(active_ids)):
            dtdream_reserve_fund = request.env['dtdream.reserve.fund'].search([('id', '=', int(active_ids[i]))])
            if not dtdream_reserve_fund.batch:
                dtdream_reserve_fund.batch = batch
            vendor_num = dtdream_reserve_fund.applicant.job_number
            vendor_name = unicode(dtdream_reserve_fund.applicant.full_name)
            vendor_code = dtdream_reserve_fund.name
            invoice_type = 'AP-Payments'
            company = '0010'
            gongyingshang = ''
            product = '0000000'
            region = '0000'
            bm = '00'
            sm = '0000'
            ic = '000'
            spare = '0000'
            currency = 'CNY'
            cstcenter = dtdream_reserve_fund.dep_code
            accounted_cr = dtdream_reserve_fund.total_amount

            if dtdream_reserve_fund.pay_to_who == u'付款给供应商':
                gongyingshang = dtdream_reserve_fund.payee_name

            duplicate_removal = {}
            for record in dtdream_reserve_fund.reserve_fund_record:
                if record.name.id in duplicate_removal:
                    duplicate_removal[record.name.id]["accounted_dr"] += record.estimate_amount
                else:
                    duplicate_removal[record.name.id] = {}
                    duplicate_removal[record.name.id]["cstcenter"] = cstcenter
                    duplicate_removal[record.name.id]["account"] = record.name.account
                    duplicate_removal[record.name.id]["account_name"] = record.name.name
                    duplicate_removal[record.name.id]["type"] = pay_type[dtdream_reserve_fund.pay_to_who]
                    duplicate_removal[record.name.id]["description"] = record.pay_time[:-3]+'@'+gongyingshang+'@'+(dtdream_reserve_fund.illustration or "")
                    duplicate_removal[record.name.id]["accounted_dr"] = record.estimate_amount
                    duplicate_removal[record.name.id]["accounted_cr"] = 0
            duplicate_removal[10000] = {
                "cstcenter": "000000",
                "account": "2090100",
                "account_name": u"其它应付款-员工报销款",
                "type": pay_type[dtdream_reserve_fund.pay_to_who],
                "description": dtdream_reserve_fund.reserve_fund_record[0].pay_time[:-3]+'@'+gongyingshang+'@'+(dtdream_reserve_fund.illustration or ""),
                "accounted_dr": 0,
                "accounted_cr": accounted_cr

            }
            duplicate_removal_order = sorted(duplicate_removal.iteritems(), key=lambda d: d[0])
            for rec in duplicate_removal_order:
                index += 1
                row = [index, dtdream_reserve_fund.batch, period, gl_date, vendor_num, vendor_name, vendor_code,
                       invoice_type,
                       company,
                       duplicate_removal[rec[0]]["cstcenter"],
                       duplicate_removal[rec[0]]["account"],
                       duplicate_removal[rec[0]]["account_name"],
                       duplicate_removal[rec[0]]["type"],
                       duplicate_removal[rec[0]]["description"],
                       product, region, bm, sm, ic, spare, currency,
                       round(duplicate_removal[rec[0]]["accounted_dr"], 2),
                       round(duplicate_removal[rec[0]]["accounted_cr"], 2),
                       round(duplicate_removal[rec[0]]["accounted_dr"], 2) - round(duplicate_removal[rec[0]]["accounted_cr"],2)]
                excel_values.append(row)
        return request.make_response(
            self.from_data(excel_header, excel_values),
            headers=[
                ('Content-Disposition', 'attachment; filename="%s"'
                 % self.filename("dtdream_reserve_fund_export")),
                ('Content-Type', self.content_type)
            ],
            cookies={'fileToken': token}
        )

