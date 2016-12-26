# -*- coding: utf-8 -*-
from openerp import http
from openerp.http import request,serialize_exception
from openerp.addons.web.controllers.main import ExcelExport
from datetime import datetime
from openerp.exceptions import ValidationError


class DtdreamExpense(ExcelExport):
    @http.route('/dtdream_expense/dtdream_expense_export', type='http',auth='public')
    def dtdream_expense_export(self,data,token):
        index = 0
        pay_type = {u"fukuangeiyuangong":{u"差旅费":u"报",u"日常业务费":u"日报",u"专项业务费":u"专报",u"行政平台费":u"平报",u"其他费用":u"报"},
              u"fukuangeigongyingshang":{u"差旅费":u"付",u"日常业务费":u"日付",u"专项业务费":u"专付",u"行政平台费":u"平付",u"其他费用":u"付"}}
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
        excel_header = ['NO','BATCH','PERIOD','GL_DATE','VENDOR_NUM','VENDOR_NAME',
                      'INVOICE_CODE','INVOICE_TYPE','COMPANY','CSTCENTRE','ACCOUNT','ACCOUNT DESCRIPTION',
                      'TYPE','DESCRIPTION','PRODUCT','REGION','BM','SM',
                      'IC','SPARE','CURRENCY','ACCOUNTED_DR','ACCOUNTED_CR','NET_AMOUNT',]
        excel_values = []
        excel_values.append([u'序号', u'批名', u'日期', u'财务日期', u'工号', u'姓名', u'报销单号', u'模块', u'公司套账', u'成本中心',
                             u'会计科目', u'会计科目名称', u'支付方式', u'摘要', u'产品编码', u'销售区域','',u'销售模式',u'关联公司',
                             u'备用', u'币种', u'借方金额', u'贷方金额', u'净值'])
        for i in range(len(active_ids)):
            dtdream_expense_report = request.env['dtdream.expense.report'].search([('id','=',int(active_ids[i]))])
            if not dtdream_expense_report.batch:
                dtdream_expense_report.batch = batch
            vendor_num = dtdream_expense_report.job_number
            vendor_name = unicode(dtdream_expense_report.full_name)
            vendor_code = dtdream_expense_report.name
            invoice_type = 'AP'
            company = '0010'
            gongyingshang = ''
            product = '0000'
            region = '0000'
            bm = '0000'
            sm = '0000'
            ic = '0000'
            spare = '0000'
            currency = 'CNY'
            cstcenter = dtdream_expense_report.department_number
            accounted_cr = dtdream_expense_report.total_shibaoamount
            tax_total = 0

            if dtdream_expense_report.paycatelog == 'fukuangeigongyingshang':
                gongyingshang = dtdream_expense_report.shoukuanrenxinming

            duplicate_removal = {}
            for record in dtdream_expense_report.record_ids:
                if record.taxamount > 0:
                    tax_total += record.taxamount
                if not dtdream_expense_report.benefitdep_ids:
                    if record.expensedetail.id in duplicate_removal:
                        duplicate_removal[record.expensedetail.id]["description"] += ";"+record.currentdate[:-3]+"@"+(gongyingshang or "")+"@"+(record.actiondesc or "")
                        duplicate_removal[record.expensedetail.id]["accounted_dr"] += record.notaxamount

                    else:
                        duplicate_removal[record.expensedetail.id] = {}
                        duplicate_removal[record.expensedetail.id]["cstcenter"] = cstcenter
                        duplicate_removal[record.expensedetail.id]["account"] = record.expensedetail.account
                        duplicate_removal[record.expensedetail.id]["account_name"] = record.expensedetail.account_name
                        duplicate_removal[record.expensedetail.id]["type"] = pay_type[dtdream_expense_report.paycatelog][record.expensedetail.parentid.name]
                        duplicate_removal[record.expensedetail.id]["description"] = record.currentdate[:-3]+"@"+(gongyingshang or "")+"@"+(record.actiondesc or "")
                        duplicate_removal[record.expensedetail.id]["accounted_dr"] = record.notaxamount
                        duplicate_removal[record.expensedetail.id]["accounted_cr"] = 0
                else:
                    benefitdep_index=record.expensedetail.id
                    for benefitdep in dtdream_expense_report.benefitdep_ids:
                        benefitdep_index += 0.01
                        if benefitdep_index in duplicate_removal:
                            duplicate_removal[benefitdep_index]["description"] += ";"+record.currentdate[:-3]+"@"+(gongyingshang or "")+"@"+(record.actiondesc or "")
                            duplicate_removal[benefitdep_index]["accounted_dr"] += record.notaxamount*float(benefitdep.sharepercent)/100

                        else:
                            duplicate_removal[benefitdep_index] = {}
                            duplicate_removal[benefitdep_index]["cstcenter"] = benefitdep.depcode
                            duplicate_removal[benefitdep_index]["account"] = record.expensedetail.account
                            duplicate_removal[benefitdep_index]["account_name"] = record.expensedetail.account_name
                            duplicate_removal[benefitdep_index]["type"] = pay_type[dtdream_expense_report.paycatelog][record.expensedetail.parentid.name]
                            duplicate_removal[benefitdep_index]["description"] = record.currentdate[:-3]+"@"+(gongyingshang or "")+"@"+(record.actiondesc or "")
                            duplicate_removal[benefitdep_index]["accounted_dr"] = record.notaxamount*float(benefitdep.sharepercent)/100
                            duplicate_removal[benefitdep_index]["accounted_cr"] = 0



            if tax_total > 0:
                duplicate_removal[9999] = {
                    "cstcenter":"000000",
                    "account": "2210101",
                    "account_name": u"应交税金-应交增值税-进项(境内)",
                    "type": pay_type[dtdream_expense_report.paycatelog][dtdream_expense_report.record_ids[0].expensedetail.parentid.name],
                    "description": dtdream_expense_report.record_ids[0].currentdate[:-3]+"@"+(gongyingshang or "")+"@"+(dtdream_expense_report.record_ids[0].actiondesc or ""),
                    "accounted_dr": tax_total,
                    "accounted_cr": 0
                }
            account_credit = request.env['dtdream.expense.account.credit'].search([('paytype','=',dtdream_expense_report.paytype),('paycatelog','=',dtdream_expense_report.paycatelog)])
            duplicate_removal[10000] = {
                "cstcenter": "000000",
                "account": account_credit.account,
                "account_name": account_credit.account_name,
                "type": pay_type[dtdream_expense_report.paycatelog][dtdream_expense_report.record_ids[0].expensedetail.parentid.name],
                "description": dtdream_expense_report.record_ids[0].currentdate[:-3]+"@"+(gongyingshang or "")+"@"+(dtdream_expense_report.record_ids[0].actiondesc or ""),
                "accounted_dr": 0,
                "accounted_cr": accounted_cr

            }
            duplicate_removal_order = sorted(duplicate_removal.iteritems(),key=lambda d: d[0])
            for rec in duplicate_removal_order:
                index += 1
                row = [index, dtdream_expense_report.batch, period, gl_date, vendor_num, vendor_name, vendor_code, invoice_type, company,
                       duplicate_removal[rec[0]]["cstcenter"],
                       duplicate_removal[rec[0]]["account"], duplicate_removal[rec[0]]["account_name"], duplicate_removal[rec[0]]["type"],
                       duplicate_removal[rec[0]]["description"], product, region, bm, sm, ic, spare,currency,
                       duplicate_removal[rec[0]]["accounted_dr"],
                       duplicate_removal[rec[0]]["accounted_cr"],
                       duplicate_removal[rec[0]]["accounted_dr"]-duplicate_removal[rec[0]]["accounted_cr"]]
                excel_values.append(row)
        return request.make_response(
            self.from_data(excel_header, excel_values),
            headers=[
                ('Content-Disposition', 'attachment; filename="%s"'
                 % self.filename("test")),
                ('Content-Type', self.content_type)
            ],
            cookies={'fileToken': token}
        )

