# -*- coding: utf-8 -*-
from openerp import api, models

class ParticularReport(models.AbstractModel):
    _name = 'report.shumeng.advance_custom_report'

    def max(a,b):
    	return a if a >= b else b

    @api.multi
    def render_html(self, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('shumeng.advance_custom_report')

        courses = self.env[report.model].browse(self._ids)
        # 取每个人的最高成绩
        cj_res = {}
        cj = {}
        for rec in courses:
        	if not rec.course_log_ids:
        		return

        	exam = rec.course_log_ids[0].exam_ids
        	for e in exam:
        		for c in e.chengji_ids:
        			pid = c.partner_id.id
        			if c.partner_id in cj:
        				cj[c.partner_id] = max(cj[c.partner_id], c.chengji)
        			else:
        				cj[c.partner_id] = c.chengji
        	cj_res[rec.id] = cj

        print "~~~~~~~~~report~~~~~~~~~~~"
        print cj_res

        
        docargs = {
            'doc_ids': self._ids,
            'doc_model': report.model,
            'docs': courses,
            'chengji': cj_res,
        }

        return report_obj.render('shumeng.advance_custom_report', docargs)