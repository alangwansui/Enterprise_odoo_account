# -*- coding: utf-8 -*-
from openerp import models, fields, api
from datetime import datetime,timedelta
from openerp.exceptions import ValidationError

class dtdream_hr_business(models.Model):
    _name = 'dtdream_hr_business.dtdream_hr_business'
    _inherit = ['mail.thread']
    _description = u"外出公干"
    name = fields.Many2one("hr.employee",string="申请人",required=True,default=lambda self: self.env["hr.employee"].search([("user_id", "=", self.env.user.id)]))

    @api.depends('name')
    def _compute_employee(self):
        for rec in self:
            rec.job_number=rec.name.job_number
            rec.full_name=rec.name.full_name
            rec.department=rec.name.department_id.complete_name


    @api.onchange('name')
    def _chang_approver_fir(self):
        domain = {}
        assitand = self.name.department_id.assitant_id
        ancestors = []
        if assitand:
            if len(assitand)>1:
                self.approver_fir = None
                for x in assitand:
                    ancestors +=[x.id]
                domain['approver_fir'] = [('id', 'in',ancestors)]
                return {'domain': domain}
            else:
                 self.approver_fir = assitand[0]
                 domain['approver_fir'] = [('id', 'in',ancestors)]
                 return {'domain': domain}
        else:
            self.approver_fir = None
            domain['approver_fir'] = [('id', 'in',ancestors)]
            return {'domain': domain}

    @api.one
    def _get_appFir(self):
        domain = {}
        ids = self.env["hr.employee"].search([("user_id", "=", self.env.user.id)])
        assitand = ids.department_id.assitant_id
        ancestors = []
        if assitand:
            if len(assitand)>1:
                for x in assitand:
                    ancestors +=[x.id]
                domain['approver_fir'] = [('id', 'in',ancestors)]
                return {'domain': domain}
            else:
                 self.approver_fir = assitand[0]
                 domain['approver_fir'] = [('id', 'in',ancestors)]
                 return {'domain': domain}
        else:
            domain['approver_fir'] = [('id', 'in',ancestors)]
            return {'domain': domain}

    full_name = fields.Char(compute=_compute_employee,string="姓名")
    job_number = fields.Char(compute=_compute_employee,string="工号")
    department = fields.Char(compute=_compute_employee,string="部门")
    create_time = fields.Datetime(string='申请时间',default=lambda self: datetime.now(),readonly=True)
    approver_fir = fields.Many2one("hr.employee" ,string="第一审批人",store=True,required=True,default=_get_appFir)
    approver_sec = fields.Many2one("hr.employee",string="第二审批人")
    approver_thr = fields.Many2one("hr.employee",string="第三审批人")
    approver_fou = fields.Many2one("hr.employee",string="第四审批人")
    approver_fif = fields.Many2one("hr.employee",string="第五审批人")

    current_approver = fields.Many2one("hr.employee" ,compute=_compute_employee,string="当前审批人",store=True)

    his_app = fields.Many2many("res.users")

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

    employ = fields.Many2one("hr.employee", string="员工")

    @api.constrains("detail_ids")
    def _check_start_end_time(self):
        """检查各行程间时间是否冲突，是否与出差时间冲突,是否与之前提交的出差申请时间冲突"""
        min_start = ""
        cr = self.env["dtdream.travel.journey"].search([("travel_id.name.id", "=", self.name.id),
                                                                     ("travel_id.state", "not in", ("0","-1"))])

        crr = self.env["dtdream_hr_business.business_detail"].search([("business.name.id", "=", self.name.id)])

        for journey in self.detail_ids:
            if journey.startTime < min_start:
                raise ValidationError("外出时间与结束时间填写不合理,各行程间时间存在冲突!")
            min_start = journey.endTime
            for travel in crr:
                if travel.id == journey.id:
                    continue
                if travel.startTime <= journey.startTime < travel.endTime or \
                                        travel.startTime < journey.endTime <= travel.endTime:
                    raise ValidationError("{0}到{1}时间与之前提交的外出申请时间冲突!".format(datetime.strptime(journey.startTime,"%Y-%m-%d %H:%M:%S")+timedelta(hours=8), datetime.strptime(journey.endTime,"%Y-%m-%d %H:%M:%S")+timedelta(hours=8)))
            for detail in cr:
                if detail.starttime <= journey.startTime[:10] < detail.endtime or \
                                        detail.starttime < journey.endTime[:10] <= detail.endtime:
                    raise ValidationError("{0}到{1}时间与外出公干时间重合".format(datetime.strptime(journey.startTime,"%Y-%m-%d %H:%M:%S")+timedelta(hours=8), datetime.strptime(journey.endTime,"%Y-%m-%d %H:%M:%S")+timedelta(hours=8)))

    detail_ids = fields.One2many("dtdream_hr_business.business_detail","business","明细")

    def get_base_url(self,cr,uid):
        base_url = self.pool.get('ir.config_parameter').get_param(cr, uid, 'web.base.url')
        return base_url

    def get_mail_server_name(self):
        return self.env['ir.mail_server'].search([], limit=1).smtp_user

#提交审批邮件通知
    def send_mail(self):
        base_url = self.get_base_url()
        link = '/web#id=%s&view_type=form&model=dtdream_hr_business.dtdream_hr_business' % self.id
        url = base_url+link
        email_to=self.current_approver.work_email
        app_time=  self.create_time[:10]
        subject = u'%s于%s提交外出公干申请，请您审批！' %(self.name.user_id.name,app_time)
        appellation= self.current_approver.user_id.name+u'，您好：'
        content = u'%s提交的外出公干申请正等待您的审批！' %(self.name.user_id.name)
        self.env['mail.mail'].create({
                'body_html': u'''<p>%s</p>
                             <p>%s</p>
                             <p> 请点击链接进入审批:
                             <a href="%s">%s</a></p>
                            <p>dodo</p>
                             <p>万千业务，简单有do</p>
                             <p>%s</p>''' % (appellation,content, url,url,self.write_date[:10]),
                'subject': '%s' % subject,
                'email_to': '%s' % email_to,
                'auto_delete': False,
                'email_from':self.get_mail_server_name(),
            }).send()

#申请通过/驳回通知申请人 
    def send_mail_to_app(self):
        base_url = self.get_base_url()
        link = '/web#id=%s&view_type=form&model=dtdream_hr_business.dtdream_hr_business' % self.id
        url = base_url+link
        email_to=self.name.work_email
        app_time=  self.create_time[:10]
        subject = u'%s您于%s提交外出公干申请已被%s批准，请您查看！' %(self.name.user_id.name,app_time,self.current_approver.user_id.name)
        content = u'%s您提交的外出公干申请已被%s批准，请您查看！' %(self.name.user_id.name,self.current_approver.user_id.name)
        if self.state=='99':
            subject = u'%s您于%s提交外出公干申请已被%s驳回，请您查看！' %(self.name.user_id.name,app_time,self.current_approver.user_id.name)
            content = u'%s您提交的外出公干申请已被%s驳回，请您查看！' %(self.name.user_id.name,self.current_approver.user_id.name)
        appellation= self.name.user_id.name+u'，您好：'
        self.env['mail.mail'].create({
                'body_html': u'''<p>%s</p>
                             <p>%s</p>
                             <p> 请点击链接进入查看:
                             <a href="%s">%s</a></p>
                              <p>dodo</p>
                             <p>万千业务，简单有do</p>
                             <p>%s</p>''' % (appellation,content, url,url,self.write_date[:10]),
                'subject': '%s' % subject,
                'email_to': '%s' % email_to,
                'auto_delete': False,
                'email_from':self.get_mail_server_name(),
            }).send()

    @api.model
    def create(self, vals):
        empl = self.env['hr.employee'].browse(vals['name'])
        result = super(dtdream_hr_business, self).create(vals)
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
        self.message_post(body=u'提交，状态：草稿 --> '+u'一级审批')
        self.send_mail()

    @api.model
    def wkf_sec(self):                                      #第一审批人批准
        lg = len(self.detail_ids)
        if lg<=0:
            raise ValidationError("请至少填写一条明细")
        self.write({'his_app': [(4, self.current_approver.user_id.id)]})
        if self.approver_sec:
            self.write({'state': '1'})
            self.send_mail_to_app()
            self.write({'current_approver':self.approver_sec.id})
            self.message_post(body=u'批准，状态：一级审批 --> '+u'二级审批')
            self.send_mail()
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
            self.send_mail_to_app()
            self.write({'current_approver':self.approver_thr.id})
            self.message_post(body=u'批准，状态：二级审批 --> '+u'三级审批')
            self.send_mail()
        else:
            self.write({'state': '5'})
            self.message_post(body=u'批准，状态：二级审批 --> '+u'批准')
            self.send_mail_to_app()

    @api.model
    def wkf_fou(self):                                       #第三审批人批准
        lg = len(self.detail_ids)
        if lg<=0:
            raise ValidationError("请至少填写一条明细")
            self.write({'his_app': [(4, self.current_approver.user_id.id)]})
        if self.approver_fou:
            self.write({'state': '3'})
            self.send_mail_to_app()
            self.write({'current_approver':self.approver_fou.id})
            self.message_post(body=u'批准，状态：三级审批 --> '+u'四级审批')
            self.send_mail()
        else:
            self.write({'state': '5'})
            self.message_post(body=u'批准，状态：三级审批 --> '+u'批准')
            self.send_mail_to_app()

    @api.model
    def wkf_fif(self):                                       #第四审批人批准
        lg = len(self.detail_ids)
        if lg<=0:
            raise ValidationError("请至少填写一条明细")
            self.write({'his_app': [(4, self.current_approver.user_id.id)]})
        if self.approver_fif:
            self.write({'state': '4'})
            self.send_mail_to_app()
            self.write({'current_approver':self.approver_fif.id})
            self.message_post(body=u'批准，状态：四级审批 --> '+u'五级审批')
            self.send_mail()
        else:
            self.write({'state': '5'})
            self.message_post(body=u'批准，状态：四级审批 --> '+u'批准')
            self.send_mail_to_app()

    @api.model
    def wkf_accept(self):                                        #第五审批人批准
        lg = len(self.detail_ids)
        if lg<=0:
            raise ValidationError("请至少填写一条明细")
            self.write({'his_app': [(4, self.current_approver.user_id.id)]})
        self.write({'state': '5'})
        self.message_post(body=u'批准，状态：五级审批 --> '+u'批准')
        self.send_mail_to_app()

    @api.model
    def wkf_refuse(self):                                       #各审批人驳回
        self.write({'state': '99'})
        self.write({'his_app': [(4, self.current_approver.user_id.id)]})
        self.send_mail_to_app()
        self.write({'current_approver':self.name.id})



class business_detail(models.Model):
    _name = "dtdream_hr_business.business_detail"
    name=fields.Char()

    @api.constrains("place", "startTime", "endTime", "reason")
    def _check_start_end_address(self):
        if not self.place or not self.startTime or not self.endTime or not self.reason:
            raise ValidationError(u"外出地点,开始时间,结束时间,事由为必填项!")

    place = fields.Char("外出地点" )
    startTime = fields.Datetime("开始时间")
    endTime = fields.Datetime("结束时间")
    reason = fields.Text("事由")
    business = fields.Many2one("dtdream_hr_business.dtdream_hr_business",ondelete="cascade")


    def _check_date(self, cr, uid, ids, context=None):
        for event in self.browse(cr, uid, ids, context=context):
            if event.endTime < event.startTime:
                return False
        return True

    _constraints = [
        (_check_date, u'开始时间不能晚于结束时间!', ["startTime","endTime"]),
        ]
class dtdream_business_hr(models.Model):
    _inherit = 'hr.employee'

    @api.depends("travel_ids_business")
    def _compute_business_log(self):
        cr = self.env["dtdream_hr_business.dtdream_hr_business"].search([("name.id", "=", self.id)])
        self.business_log_nums = len(cr)

    @api.one
    def _compute_business_has_view(self):
        if self.user_id == self.env.user:
            self.can_view_business = True
        else:
            self.can_view_business = False
    can_view_business = fields.Boolean(compute="_compute_business_has_view")
    travel_ids_business = fields.One2many("dtdream_hr_business.dtdream_hr_business", "employ", string="外出公干")
    business_log_nums = fields.Integer(compute='_compute_business_log', string="外出公干记录",stroe=True)