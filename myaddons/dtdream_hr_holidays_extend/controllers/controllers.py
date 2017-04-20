# -*- coding: utf-8 -*-
from openerp import http
from openerp.http import request
from openerp.addons.web.controllers.main import ExcelExport
class DtdreamHrHolidaysExtend(ExcelExport):
    @http.route('/dtdream_hr_holidays_extend/annual_leave_data_proofreading_export/', auth='public')
    def annual_leave_data_proofreading_export(self, active_ids,token):
        excel_header = ['JOB_CODE', 'NAME', 'FULL_NAME', 'LEVEL_DEPARTMENT','SECONDARY_SECTOR','THREE_DEPARTMENT',
                        'WORK_PLACE', 'ENTRY_DAY']
        rowa = [u'工号', u'姓名', u'花名', u'一级部门', u'二级部门', u'三级部门', u'工作地', u'入职时间']

        ids = []
        for id in active_ids.split(','):
            ids.append(int(id))
        holidays = request.env['hr.holidays'].sudo().browse(ids)
        yearlist = [holiday.year for holiday in holidays]

        years =[]
        yearsKey = []
        for year in yearlist:
            if int(year) not in yearsKey:
                yearsKey.append(int(year))
                years.append(int(2017)-int(year))

        yearsKey.sort()
        yearsKey.reverse()
        years.sort()
        for year in years:
            yearha = str(year)+'ANNUAL'
            yearhb = str(year)+'ANNUAL_LE'
            excel_header.append(yearha)
            excel_header.append(yearhb)
            yearha = str(year) + u'年休假配额'
            yearhb = str(year) + u'年休假剩余'
            rowa.append(yearha)
            rowa.append(yearhb)
        excel_values = []
        excel_values.append(rowa)


        ems = set([holiday.employee_id for holiday in holidays])
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
            for year in yearsKey:
                domains = [('employee_id', '=', em.id),('year','=',str(year)),('id','in',ids)]
                result =  request.env['hr.holidays'].sudo().search(domains)
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