# -*- coding: utf-8 -*-

from openerp import models, fields, api

class Wizard(models.TransientModel):
    _name = 'shumeng.exam.wizard'

    def _default_attendee(self):
    	print self
    	#{'lang': 'zh_CN', 'tz': False, 'uid': 1, 'active_model': 'shumeng.course.log', 'params': {'action': 411}, 'search_disable_custom_filters': True, 'active_ids': [15], 'active_id': 15}
    	active_id = self._context['active_ids']
        logs = self.env['shumeng.course.log'].browse(active_id)
        exam_obj = self.env['shumeng.exam']
        exam = exam_obj.search([('course_log_id','=',self._context['active_id'])])
        if len(exam) == 0:
            # 初考考生默认全部
            return logs[0].student_ids

        if len(exam) > 0:
            bukao_num = len(exam)
            last_bukao = exam[bukao_num-1]
            access_mark = last_bukao.course_log_id.course_id.access_mark
            attends = []

            for cj in last_bukao.chengji_ids:
                if cj.chengji < access_mark:
                    attends.append(cj.partner_id.id)

            return self.env['res.partner'].browse(attends)

    #TODO: 废弃， 不用选择考试， 直接通过向导快捷创建考试
    exam_id = fields.Many2one('shumeng.exam',string="考试")
    attendee_ids = fields.Many2many('res.partner', string="考生", default=_default_attendee)

    @api.one
    def btn_confirm(self):
    	print self.exam_id
        # 为培训创建考试， 检索该培训的最近的考试， 若无，创建初考， 若有，创建补考
        # 若有补考的时候, 把最近一次补考不及格的加到考生里

        exam_obj = self.env['shumeng.exam']
        chengji_obj = self.env['shumeng.chengji']

        course_log = self.env['shumeng.course.log'].browse(self._context['active_id'])

        exam = exam_obj.search([('course_log_id','=',self._context['active_id'])])
        if len(exam) == 0:
            # 创建初考
            vals = {'name':course_log.name + u'_初考', 'course_log_id':self._context['active_id'], 'type':'chukao'}
            exam_id = exam_obj.create(vals)

        if len(exam) > 0:
            vals = {'name':course_log.name + u'_补考'+str(len(exam)), 'course_log_id':self._context['active_id'], 'type':'bukao', 'chukao_id':exam[0].id}
            exam_id = exam_obj.create(vals)

        if exam_id:
            for a in self.attendee_ids:
                chengji_obj.create({'exam_id':exam_id.id,'partner_id':a.id})

    	
    	