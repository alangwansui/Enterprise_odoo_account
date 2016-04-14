# -*- coding: utf-8 -*-
from openerp.osv import expression
from openerp import models, fields, api
from datetime import datetime
from openerp.exceptions import ValidationError
# from lxml import etree

class dtdream_hr_business(models.Model):
    _name = 'dtdream_hr_business.dtdream_hr_business'
    _inherit = ['mail.thread']

    name = fields.Many2one("hr.employee",string="申请人",required=True)

    @api.depends('name')
    def _compute_employee(self):
        for rec in self:
            rec.job_number=rec.name.job_number
            rec.full_name=rec.name.full_name
            rec.department=rec.name.department_id.complete_name
            rec.approver_fir = rec.name.department_id.assitant_id

    full_name = fields.Char(compute=_compute_employee,string="姓名")
    job_number = fields.Char(compute=_compute_employee,string="工号")
    department = fields.Char(compute=_compute_employee,string="部门")
    create_time= fields.Datetime(string='申请时间',default=datetime.today(),readonly=1)
    approver_fir = fields.Many2one("hr.employee" ,compute=_compute_employee,string="第一审批人",store=True)
    approver_sec = fields.Many2one("hr.employee",string="第二审批人")
    approver_thr = fields.Many2one("hr.employee",string="第三审批人")
    approver_fou = fields.Many2one("hr.employee",string="第四审批人")
    approver_fif = fields.Many2one("hr.employee",string="第五审批人")

    current_approver = fields.Many2one("hr.employee" ,compute=_compute_employee,string="当前审批人",store=True)

    his_app = fields.Many2many("hr.employee")

    @api.one
    def _compute_is_shenpiren(self):
        if self.name.user_id == self.env.user:
            self.is_shenqingren = True
        else:
            self.is_shenqingren = False
        if self.current_approver.user_id == self.env.user:
            self.is_shenpiren = True
        else:
            self.is_shenpiren = False
        if 1 == self.env.user.id:
            self.is_admin = True
        else:
            self.is_admin = False
        if len(self.create_uid)>0 and self.create_uid != self.env.user:
            self.is_create = False
        else:
            self.is_create = True

    is_create = fields.Boolean(compute=_compute_is_shenpiren, string="是否创建人",default=True)

    is_admin = fields.Boolean(compute=_compute_is_shenpiren, string="是否管理员",)

    is_shenpiren = fields.Boolean(compute=_compute_is_shenpiren, string="当前用户是否审批人",default=True)

    is_shenqingren = fields.Boolean(compute=_compute_is_shenpiren, string="当前用户是否申请人",default=True)

    state = fields.Selection([('-1','草稿'),('0','一级审批'),('1','二级审批'),('2','三级审批'),('3','四级审批'),('4','五级审批'),('5','完成'),('99','驳回')],string="状态",default='-1')

    @api.depends('name','create_time')
    def _compute_title(self):
        for rec in self:
            rec.title = rec.name.name_related +u'于'+rec.create_time+u'提交的外出公干申请'

    title = fields.Char(compute=_compute_title,string="事件")
    detail_ids = fields.One2many("dtdream_hr_business.business_detail","business","明细")


    def send_mail(self):
        print 111111111111111111111111111111111
        self.env['mail.mail'].create({
                'body_html': '1111111111111111111111111111111111111111',
                'subject': '%s' % self['title'],
                'email_to': '%s' % self['name']['user_id']['email'],
                'auto_delete': False,
            }).send()

    @api.model
    def create(self, vals):
        empl = self.env['hr.employee'].browse(vals['name'])
        if not empl['department_id']['assitant_id']:
            raise ValidationError("请先配置该部门的行政助理")
        result = super(dtdream_hr_business, self).create(vals)
        # result.send_mail()
        return  result

    @api.model
    def wkf_draft(self):                            #创建
        if self.state=='99':
            self.message_post(body=u'重启流程，状态：驳回 --> '+u'草稿')
        self.write({'state': '-1'})

    @api.model
    def wkf_first(self):                            #提交
        lg = len(self.detail_ids)
        if lg<=0:
            raise ValidationError("请至少填写一条明细")
        self.write({'state': '0'})
        self.write({'current_approver':self.approver_fir.id})
        self.message_post(body=u'批准，状态：草稿 --> '+u'一级审批')

    @api.model
    def wkf_sec(self):                                      #第一审批人批准
        lg = len(self.detail_ids)
        if lg<=0:
            raise ValidationError("请至少填写一条明细")
        self.write({'his_app': [(4, self.current_approver.user_id.id)]})
        if self.approver_sec:
            self.write({'state': '1'})
            self.write({'current_approver':self.approver_sec.id})
            self.message_post(body=u'批准，状态：一级审批 --> '+u'二级审批')
            print self.his_app
        else:
            raise ValidationError("配置第二审批人")

    @api.model
    def wkf_thr(self):                                      #第二审批人批准
        lg = len(self.detail_ids)
        if lg<=0:
            raise ValidationError("请至少填写一条明细")
        self.write({'his_app': [(4, self.current_approver.user_id.id)]})
        if self.approver_thr:
            self.write({'state': '2'})
            self.write({'current_approver':self.approver_thr.id})
            self.message_post(body=u'批准，状态：二级审批 --> '+u'三级审批')
        else:
            self.write({'state': '5'})
            self.message_post(body=u'批准，状态：二级审批 --> '+u'批准')
            # self.write({'current_approver':-10})
            print self.his_app

    @api.model
    def wkf_fou(self):                                       #第三审批人批准
        lg = len(self.detail_ids)
        if lg<=0:
            raise ValidationError("请至少填写一条明细")
            self.write({'his_app': [(4, self.current_approver.user_id.id)]})
        if self.approver_fou:
            self.write({'state': '3'})
            self.write({'current_approver':self.approver_fou.id})
            self.message_post(body=u'批准，状态：三级审批 --> '+u'四级审批')
        else:
            self.write({'state': '5'})
            self.message_post(body=u'批准，状态：三级审批 --> '+u'批准')
            # self.write({'current_approver':-10})


    @api.model
    def wkf_fif(self):                                       #第四审批人批准
        lg = len(self.detail_ids)
        if lg<=0:
            raise ValidationError("请至少填写一条明细")
            self.write({'his_app': [(4, self.current_approver.user_id.id)]})
        if self.approver_fif:
            self.write({'state': '4'})
            self.write({'current_approver':self.approver_fif.id})
            self.message_post(body=u'批准，状态：四级审批 --> '+u'五级审批')
        else:
            self.write({'state': '5'})
            self.message_post(body=u'批准，状态：四级审批 --> '+u'批准')
            # self.write({'current_approver':-10})

    @api.model
    def wkf_accept(self):                                        #第五审批人批准
        lg = len(self.detail_ids)
        if lg<=0:
            raise ValidationError("请至少填写一条明细")
            self.write({'his_app': [(4, self.current_approver.user_id.id)]})
        self.write({'state': '5'})
        self.message_post(body=u'批准，状态：五级审批 --> '+u'批准')
        # self.write({'current_approver':-10})

    @api.model
    def wkf_refuse(self):                                       #各审批人驳回
        self.write({'state': '99'})
        self.write({'his_app': [(4, self.current_approver.user_id.id)]})
        self.write({'current_approver':self.name.id})


    # @api.multi
    # def unlink(self):
    #     for record in self:
    #         if record.state != '-1' or record.name.id != self.user.id:
    #             raise ValidationError("您不是申请人或该流程已提交审批")
    #         record.detail_ids.unlink()
    #     return super(dtdream_hr_business, self).unlink()

class business_detail(models.Model):
    _name = "dtdream_hr_business.business_detail"
    name=fields.Char()
    place = fields.Char("外出地点" , required="1")
    startTime = fields.Datetime("开始时间" ,required="1")
    endTime = fields.Datetime("结束时间" ,required="1")
    reason = fields.Text("事由",required="1")
    business = fields.Many2one("dtdream_hr_business.dtdream_hr_business",ondelete="cascade")


    def _check_date(self, cr, uid, ids, context=None):
        for event in self.browse(cr, uid, ids, context=context):
            if event.endTime < event.startTime:
                return False
        return True

    _constraints = [
        (_check_date, u'开始时间不能晚于结束时间!', ["startTime","endTime"]),
        ]
