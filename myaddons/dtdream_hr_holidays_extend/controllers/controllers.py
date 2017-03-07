# -*- coding: utf-8 -*-
from openerp import http
from openerp.http import request
from openerp.addons.web.controllers.main import ExcelExport
class DtdreamHrHolidaysExtend(ExcelExport):
    @http.route('/dtdream_hr_holidays_extend/annual_leave_data_proofreading_export/', auth='public')
    def annual_leave_data_proofreading_export(self, data,token):
        excel_header = ['JOB_CODE', 'NAME', 'FULL_NAME', 'LEVEL_DEPARTMENT','SECONDARY_SECTOR','THREE_DEPARTMENT',
                        'WORK_PLACE', 'ENTRY_DAY', '2015ANNUAL', '2015ANNUAL_LE',
                         '2016ANNUAL', '2016ANNUAL_LE',
                         '2017ANNUAL', '2017ANNUAL_LE']
        excel_values = []
        excel_values.append([u'工号', u'姓名', u'花名', u'一级部门', u'二级部门', u'三级部门', u'工作地', u'入职时间', u'2015年休假配额', u'2015年休假剩余',u'2016年休假配额', u'2016年休假剩余',
                             u'2017年休假配额', u'2017年休假剩余'])

        years=['2','1','0']
        ems = request.env['hr.employee'].sudo().search([('Inaugural_state', '=', 'Inaugural_state_01')])
        for em in ems:
            row = [em.job_number, em.full_name, em.name]
            department=em.department_id
            if not department.parent_id:
                row.append(department.name)
                row.append("")
                row.append("")
            else:
                if not department.parent_id.parent_id:
                    row.append(department.parent_id.name)
                    row.append(department.name)
                    row.append("")
                else:
                    row.append(department.parent_id.parent_id.name)
                    row.append(department.parent_id.name)
                    row.append(department.name)
            row.append(em.work_place)
            row.append(em.entry_day)
            for year in years:
                domains = [('employee_id', '=', em.id), ('type', '=', 'add'), ('create_type', '=', 'manage'),
                           ('state', '=', 'validate'),('year','=',year)]
                result =  request.env['hr.holidays'].sudo().search_read(domain=domains)
                if len(result)>0:
                    row.append(result[0]['nxj_fenpei'])
                    row.append(result[0]['nxj_yue'])
                else:
                    row.append("")
                    row.append("")
            excel_values.append(row)
        return request.make_response(
            self.from_data(excel_header, excel_values),
            headers=[
                ('Content-Disposition', 'attachment; filename="%s"'
                 % self.filename("dtdream_hr_holidays")),
                ('Content-Type', self.content_type)
            ],
            cookies={'fileToken': token}
        )