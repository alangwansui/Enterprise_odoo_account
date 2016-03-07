# -*- coding: utf-8 -*-
import logging
import datetime

from openerp import models, fields, api
from openerp.exceptions import ValidationError


_logger = logging.getLogger(__name__)

# 我们创建的新模型
# shumeng.shumeng
# shumeng.course
# shumeng.course.log
# shumeng.exam
# shumeng.chengji
# shumeng.course.tag
# shumeng.teacher
# shumeng.qingjiadan


class shumeng(models.Model):
    _name = 'shumeng.shumeng'

    name = fields.Char()
    renshu = fields.Integer(string="人数")
    jieshao = fields.Text(string="公司介绍")
    jieshao2 = fields.Html(string="介绍HTML")
    xingzhi = fields.Selection([('guoqi','国企'),('siqi','私企')],"企业性质")
    chengliriqi = fields.Date(string="成立日期")


class shumeng_course(models.Model):
    _name = "shumeng.course"

    @api.depends('keshi_lilun','keshi_shicao')
    def _compute_keshi_total(self):
        for rec in self:
            rec.keshi_total = rec.keshi_shicao + rec.keshi_lilun

    def _compute_search(self, operator, value):
        records = self.search([])
        arr = []
        for record in records:
            if operator == "=":
                if record.keshi_lilun + record.keshi_shicao == value:
                    arr.append(record.id)

        return [('id','in',arr)]

    @api.onchange('keshi_total','ke_shi_price')
    def _onchange_ke_shi(self):
        self.ke_shi_fee = self.keshi_total * self.ke_shi_price

    @api.constrains('keshi_lilun')
    def check_keshi_lilun(self):
        for r in self:
            if r.keshi_lilun > 120:
                raise ValidationError("课程理论课时不能超过120， 当前理论课时为: %s" % r.keshi_lilun)

    @api.depends('course_log_ids')
    def _compute_course_log(self):
        for rec in self:
            #rec.course_log_nums = len([e.id for e in rec.course_log_ids])
            rec.course_log_nums = len(rec.course_log_ids)

    name = fields.Char("课程名称", required=True)
    # TODO: 考试关联到培训（开班）上，所以此字段废弃
    exam_ids = fields.One2many("shumeng.exam", 'course_id', string="考试")
    course_log_ids = fields.One2many("shumeng.course.log", 'course_id', string="开课记录")
    tags_ids = fields.Many2many("shumeng.course.tag", string="标签")
    keshi_lilun = fields.Integer("理论课时")
    keshi_shicao = fields.Integer("实操课时")
    keshi_total = fields.Integer(compute=_compute_keshi_total, search=_compute_search, string="总课时"
        ,help="这是计算字段，默认只读，总课时=理论课时+实操课时")
    access_mark = fields.Integer(string="通过分数线", default=80, required=True)
    zhu_jiang = fields.Many2one("res.users", string="主讲")
    ke_shi_price = fields.Float("课时单价")
    ke_shi_fee = fields.Float("课时费")
    is_validate = fields.Boolean("可用")
    course_log_nums = fields.Integer(compute='_compute_course_log', string="开课次数")
    jieshao = fields.Html("介绍")
    academy_id = fields.Many2one("shumeng.shumeng", string="学院", default=lambda self: self.env.user.xueyuan, readonly=True)

    _sql_constraints = [
        ('name_unique', 'UNIQUE(name)', "名称不能重复！"),
    ]


class shumeng_exam(models.Model):
    _name = "shumeng.exam"

    name = fields.Char("名称", help="为该考试起一个容易识别的名字！")
    shi_chang = fields.Integer("时长",default=120)
    state = fields.Selection(
        [('draft','草稿'),
        ('wait','待批'),
        ('approve','通过'),
        ('done','结束')], string="状态", default="draft")
    # TODO:废弃， 考试与开课记录相关联
    course_id = fields.Many2one("shumeng.course", string="课程")
    course_log_id = fields.Many2one("shumeng.course.log", string="开课记录")
    # TODO: 废弃, 因为course_id字段废弃了
    keshi_total = fields.Integer(related="course_id.keshi_total")
    create_date = fields.Datetime("创建时间")
    start_time = fields.Datetime("开始时间", default=lambda self: datetime.datetime.now())
    test_char = fields.Char("test sql constraints")
    chengji_ids = fields.One2many("shumeng.chengji", 'exam_id', string="成绩", required=True)
    type = fields.Selection([('chukao','初考'),('bukao','补考')], string="类型")
    chukao_id = fields.Many2one("shumeng.exam", string="初考")
    bukao_ids = fields.One2many("shumeng.exam", 'chukao_id', string="补考")

    _sql_constraints = [
        ('nameexam_unique', 'UNIQUE(name)', "名称不能重复！"),
        ('test_char_unique', 'UNIQUE(test_char)', "test char不能重复！"),
    ]



# 成绩单
class shumeng_chengjidan(models.Model):
    _name = "shumeng.chengji"

    partner_id = fields.Many2one("res.partner")
    exam_id = fields.Many2one("shumeng.exam")
    chengji = fields.Float("成绩")



class shumeng_course_tag(models.Model):
    _name = "shumeng.course.tag"

    name = fields.Char("名称")


class shumeng_teacher(models.Model):
    _name = "shumeng.teacher"

    name = fields.Char("姓名")
    parent_id = fields.Many2one("shumeng.teacher", string="上级")
    child_ids = fields.One2many("shumeng.teacher", 'parent_id', string="下级")
    user_id = fields.Many2one("res.users", string="相关用户")

    

    #开课记录 
class shumeng_course_log(models.Model):
    _name = "shumeng.course.log"

    @api.one
    @api.depends("student_ids")
    def _compute_attends_num(self):
        print self
        self.attends_num = len(self.student_ids)



    name = fields.Char("名称", required=True, default="New")
    course_id = fields.Many2one("shumeng.course", string='课程', required=True)
    start_date = fields.Date("开始时间", required=True)
    end_date = fields.Date("结束时间", required=True)
    state = fields.Selection([('one','一'),('two','二'),('thr','三')], string="状态", default='one')
    student_ids = fields.Many2many('res.partner', string='学生')
    exam_ids = fields.One2many('shumeng.exam', 'course_log_id', string="考试")
    course_keshi = fields.Integer(related="course_id.keshi_total", string="课时")
    attends_num = fields.Integer(compute=_compute_attends_num, string="学员数量", store=True)
    test_int = fields.Integer("ddddd")

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('shumeng.course.log') or 'New'

        result = super(shumeng_course_log, self).create(vals)
        return result


class shumeng_qingjiadan(models.Model):
    _name = "shumeng.qingjiadan"
    _inherit = ['mail.thread']

    @api.one
    def _compute_is_shenpiren(self):
        if self.shengpiren.user_id == self.env.user:
            self.is_shenpiren = True
        else:
            self.is_shenpiren = False

    name = fields.Char("事由")
    tian_shu = fields.Float("天数")
    create_uid = fields.Many2one("res.users", string="请假人")
    shengpiren = fields.Many2one("shumeng.teacher", string="当前审批人")
    is_shenpiren = fields.Boolean(compute=_compute_is_shenpiren, string="是否审批人")
    state = fields.Selection([('draft','我想请假'),('wait','等待，我忍'),('wait2','等待大王'),('approve','通过，谢隆恩'),('refuse','靠，悲剧')])


    @api.multi
    def wkf_draft(self):
        # 注意state字段是没有默认值的
        self.write({'state':'draft'})

    @api.multi
    def wkf_wait(self):
        # 提交之后，更新审批人
        # 若没有审批人
        teacher_obj = self.env['shumeng.teacher']
        teacher = teacher_obj.search([('user_id','=',self.create_uid.id)])
        
        if len(teacher) == 1:
            if teacher.parent_id:
                self.write({'state':'wait','shengpiren':teacher.parent_id.id})
            else:
                self.write({'state':'draft'})
        else:
            self.message_post(body='请假人与教师的对应关系发生错误')
            self.write({'state':'draft'})
            
    @api.multi
    def wkf_wait2(self):
        # 更新审批人字段值，为请假人的上级，注意教师模型，请假人为用户，上级也为用户，之间是通过教师为桥梁关联的
        # 注意找不到上级的情况，流是流过来了，
        if not self.shengpiren.parent_id:
            return
        self.write({'state':'wait2','shengpiren':self.shengpiren.parent_id.id})


    @api.multi
    def wkf_done(self):
        self.write({'state':'approve'})

    @api.multi
    def wkf_refuse(self):
        self.write({'state':'refuse'})



class ResUsers(models.Model):
    _inherit = "res.users"

    xueyuan = fields.Many2one("shumeng.shumeng", string="学院")
    






