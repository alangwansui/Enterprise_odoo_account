# -*- coding: utf-8 -*-
from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp import http
from openerp import models, fields, api
from openerp.exceptions import ValidationError
from lxml import etree
from openerp.osv import expression

class dtdream_budget_travel(models.Model):
    _name = 'dtdream.budget.travel'
    _description = u'公务差旅费'
    travel_travel = fields.Integer(string='差旅费(元)')
    travel_bus = fields.Integer(string='市内交通费(元)')
    travel_mobile = fields.Integer(string='手机话费(元)')

    @api.onchange('travel_travel','travel_bus','travel_mobile')
    def compute_travel_total(self):
        self.travel_total=self.travel_travel+self.travel_bus+self.travel_mobile
    travel_remark = fields.Char(string='备注')
    travel_budget_id = fields.Many2one('dtdream.budget',string='预算')

    @api.constrains('travel_travel','travel_bus','travel_mobile')
    def check_valid_value(self):
        print self.travel_travel
        if self.travel_travel < 0:
            raise ValidationError('差旅费不能小于0')
        if self.travel_bus < 0:
            raise ValidationError('市内交通费不能小于0')
        if self.travel_mobile < 0:
            raise ValidationError('手机话费不能小于0')


class dtdream_budget_daily(models.Model):
    _name = 'dtdream.budget.daily'
    _description = u'日常业务费'
    daily_name = fields.Char(string='项目或事务名称')
    daily_fee = fields.Integer(string='员工预算金额(元)')
    daily_remark = fields.Char(string='备注')
    daily_budget_id = fields.Many2one('dtdream.budget',string='预算')

    @api.constrains('daily_name','daily_fee')
    def check_fields_null(self):
        if not self.daily_name:
            raise ValidationError("日常业务费的“项目或事务名称”不能为空！")
        if self.daily_fee <= 0:
            raise ValidationError("日常业务费的“员工预算金额”必须大于0！")


class dtdream_budget_zhuanx(models.Model):
    _name = 'dtdream.budget.zhuanx'
    _description = u'专项业务费'
    zhuanx_name = fields.Char(string='专项名称')
    zhuanx_fee = fields.Integer(string='员工预算金额(元)')
    zhuanx_remark = fields.Char(string='备注')
    zhuanx_budget_id = fields.Many2one('dtdream.budget',string='预算')

    @api.constrains('zhuanx_name','zhuanx_fee')
    def check_fields_null(self):
        if not self.zhuanx_name:
            raise ValidationError("专项业务费的“专项名称”不能为空！")
        if self.zhuanx_fee <= 0:
            raise ValidationError("专项业务费的“员工预算金额”必须大于0！")


class dtdream_budget_xingz(models.Model):
    _name = 'dtdream.budget.xingz'
    _description = u'行政平台费'
    xingz_name = fields.Char(string='名称')
    xingz_fee = fields.Integer(string='员工预算金额(元)')
    xingz_remark = fields.Char(string='备注')
    xingz_budget_id = fields.Many2one('dtdream.budget',string='预算')

    @api.constrains('xingz_name','xingz_fee')
    def check_fields_null(self):
        if not self.xingz_name:
            raise ValidationError("行政平台费的“名称”不能为空！")
        if self.xingz_fee <= 0:
            raise ValidationError("行政平台费的“员工预算金额”必须大于0！")


class dtdream_budget(models.Model):
    _name = 'dtdream.budget'
    _inherit =['mail.thread']
    _description = u'预算管理'
    current_handler = fields.Many2one('hr.employee',string="当前审批人")

    @api.depends('state')
    def compute_is_current_handler(self):
        for this_self in self:
            if this_self.env.user.id == this_self.current_handler.user_id.id:
                this_self.is_current_handler = True

    def check_approve_rights(self):
        # 审批权限
        if not self.is_current_handler:
            raise ValidationError("您不是当前审批人！")
        return self.is_current_handler
    is_current_handler = fields.Boolean(string='是否当前审批人',default=False,compute=compute_is_current_handler)

    @api.constrains('applicant')
    def compute_is_applicant(self):
        if self.env.user.id == self.applicant.user_id.id:
            self.is_applicant = True
        else:
            self.is_applicant =False

    @api.constrains('applicant')
    def get_manager_and_signer(self):
        if self.applicant.department_id.manager_id.id:
            self.manager=self.env['hr.employee'].search([('id','=',self.applicant.department_id.manager_id.id)])
        else:
            raise ValidationError("您的部门主管没有配置，请联系hr进行配置。")

        if self.applicant.department_id.budget_sign_one.id:
            self.signer_one=self.env['hr.employee'].search([('id','=',self.applicant.department_id.budget_sign_one.id)])
        else:
            raise ValidationError("您的部门预算权签人没有配置，请联系预算业务管理员进行配置。")

        if self.applicant.department_id.budget_sign_two.id:
            self.signer_two=self.env['hr.employee'].search([('id','=',self.applicant.department_id.budget_sign_two.id)])


    is_applicant = fields.Boolean(string='是否申请人',default=True,compute=compute_is_applicant)
    his_handler=fields.Many2many('hr.employee',string="历史审批人")

    applicant = fields.Many2one('hr.employee',string="申请人",default=lambda self:self.env['hr.employee'].search([('user_id','=',self.env.user.id)]))
    manager = fields.Many2one('hr.employee',string="主管",default=lambda self:self.env['hr.employee'].search([('id','=',self.applicant.department_id.manager_id.id)]))
    signer_one = fields.Many2one('hr.employee',string="第一权签人")
    signer_two = fields.Many2one('hr.employee',string="第二权签人")


    apply_time = fields.Datetime(string='申请时间',default=datetime.now())
    # full_name = fields.Char(string="姓名",default = lambda self:self.env['hr.employee'].search([('user_id','=',self.env.user.id)]).full_name)
    # job_number = fields.Char(string="工号",default = lambda self:self.env['hr.employee'].search([('user_id','=',self.env.user.id)]).job_number)
    department = fields.Many2one("hr.department",string="部门",default=lambda self:self.env['hr.employee'].search([('user_id','=',self.env.user.id)]).department_id.id)
    department_code = fields.Char(string="部门编码",default = lambda self:self.env['hr.employee'].search([('user_id','=',self.env.user.id)]).department_id.code)
    @api.one
    @api.depends("name")
    def _compute_fields(self):
        max_rec = ''
        id_prefix = 'YS'+datetime.strftime(datetime.today(),"%Y%m%d")
        self._cr.execute("select budget_id from dtdream_budget where budget_id like '"+id_prefix+"%' order by id desc limit 1")
        for rec in self._cr.fetchall():
            max_rec = rec[0]
        if max_rec:
            self.budget_id='YS'+str(int(max_rec[2:])+1)
        else:
            self.budget_id=id_prefix+'001'
    budget_id=fields.Char(string="单号",compute=_compute_fields,store=True)
    state=fields.Selection([("0","草稿"),("1","主管审批"),("2","第一权签人审批"),("3","第二权签人审批"),("4","已审批")],string="状态")

    name = fields.Many2one('dtdream.budget.month',string="预算月份",
                           domain=[('name','>',datetime.strftime(datetime.today()+relativedelta(months=0),"%Y%m")),
                                   ('name','<',datetime.strftime(datetime.today()+relativedelta(months=13),"%Y%m"))],default=lambda self:self.name.search([('name','=',datetime.strftime(datetime.today()+relativedelta(months=1),"%Y%m"))]).id)
    expensed_travel=fields.Integer(string='已报销差旅费(元)')
    expensed_daily=fields.Integer(string='已报销日常业务费(元)')
    expensed_zhuanx=fields.Integer(string='已报销专项业务费(元)')
    expensed_xingz=fields.Integer(string='已报销行政平台费(元)')

    def _default_fee_travel(self):
        return [(0, 0, {'travel_travel': 0.00, 'travel_bus': 0.00, 'travel_mobile': 0.00, 'travel_remark': ''})]
    def _default_fee_dzx(self,x,y,z):
        return [(0, 0, {x: '合计', y: 0.00, z: ''})]
    fee_travel = fields.One2many('dtdream.budget.travel','travel_budget_id',string='公务差旅费',default=_default_fee_travel,track_visibility='onchange')

    @api.depends('fee_travel')
    def _compute_fee_travel_total(self):
        self.fee_travel_total = 0
        for rec in self.fee_travel:
            self.fee_travel_total = rec.travel_travel+rec.travel_bus+rec.travel_mobile
    fee_travel_total = fields.Integer(string='公务差旅费合计(元)',compute=_compute_fee_travel_total,store=True)
    fee_daily = fields.One2many('dtdream.budget.daily','daily_budget_id',string='日常业务费')

    @api.depends('fee_daily')
    def _compute_fee_daily_total(self):
        self.fee_daily_total=0
        for rec in self.fee_daily:
            self.fee_daily_total += rec.daily_fee
    fee_daily_total=fields.Integer(string='日常业务费合计(元)',compute=_compute_fee_daily_total,store=True)
    fee_zhuanx = fields.One2many('dtdream.budget.zhuanx','zhuanx_budget_id',string='专项业务费')

    @api.depends('fee_zhuanx')
    def _compute_fee_zhuanx_total(self):
        self.fee_zhuanx_total=0
        for rec in self.fee_zhuanx:
            self.fee_zhuanx_total += rec.zhuanx_fee
    fee_zhuanx_total=fields.Integer(string='专项业务费合计(元)',compute=_compute_fee_zhuanx_total,store=True)
    fee_xingz = fields.One2many('dtdream.budget.xingz','xingz_budget_id',string='行政平台费')

    @api.depends('fee_xingz')
    def _compute_fee_xingz_total(self):
        self.fee_xingz_total=0
        for rec in self.fee_xingz:
            self.fee_xingz_total += rec.xingz_fee
    fee_xingz_total=fields.Integer(string='行政平台费合计(元)',compute=_compute_fee_xingz_total,store=True)

    @api.one
    @api.depends('fee_travel','fee_daily','fee_zhuanx','fee_xingz')
    def compute_all_total(self):
        self.all_total = self.fee_travel_total+self.fee_daily_total+self.fee_zhuanx_total+self.fee_xingz_total
    all_total = fields.Integer(string='总金额(元)',compute = compute_all_total,store=True)

    @api.constrains('all_total')
    def check_all_total(self):
        if self.all_total == 0:
            raise ValidationError("请至少填写一项费用类别！")

    def send_email(self):
        base_url = self.env['ir.config_parameter'].search([('key','=','web.base.url')]).value
        link='/web?#id=%s&view_type=form&model=dtdream.budget'%self.id
        url=base_url+link
        self.env['mail.mail'].create({
                'subject': u'%s于%s提交：%s 月份的预算申请，请您审批！' % (self.applicant.name, self.apply_time[:10],self.name.name),
                'body_html': u'''
                <p>%s，您好：</p>
                <p>%s提交的预算正等待您的审批！</p>
                <p> 请点击链接进入审批:
                <a href="%s">%s</a></p>
                <p>dodo</p>
                <p>万千业务，简单有do</p>
                <p>%s</p>
                ''' % (self.current_handler.name, self.applicant.name, url, url,datetime.today().strftime('%Y-%m-%d')),
                'email_from':self.env['ir.mail_server'].search([], limit=1).smtp_user,
                'email_to': self.current_handler.work_email,
            }).send()
        return url

    @api.multi
    def wkf_draft(self):
        # 草稿状态
        self.state='0'
        self.current_handler = ''

    @api.multi
    def wkf_manager_review(self):
        # 主管审批
        if self.state == '0':
            message = u"<table border=1><tr><th>状态</th><th>提交人</th></tr><tr><td>草稿-->主管审批</td><td>%s</td></tr></table>" \
                   % self.applicant.nick_name
            self.message_post(body=message)
        self.state = '1'
        self.current_handler = self.manager
        self.send_email()

    @api.multi
    def wkf_signer_one_review(self):
        # 第一权签人审批
        if self.state == '0':
            message = u"<table border=1><tr><th>状态</th><th>提交人</th></tr><tr><td>草稿-->第一权签人审批</td><td>%s</td></tr></table>" \
                   % self.applicant.nick_name
            self.message_post(body=message)
        self.state='2'
        self.current_handler = self.signer_one
        self.send_email()

    @api.multi
    def wkf_signer_two_review(self):
        # 第二权签人审批
        if self.state == '0':
            message = u"<table border=1><tr><th>状态</th><th>提交人</th></tr><tr><td>草稿-->第二权签人审批</td><td>%s</td></tr></table>" \
                   % self.applicant.nick_name
            self.message_post(body=message)
        self.state='3'
        self.current_handler = self.signer_two
        self.send_email()

    @api.multi
    def wkf_reviewed(self):
        # 已审批
        if self.state == '0':
            message = u"<table border=1><tr><th>状态</th><th>提交人</th></tr><tr><td>草稿-->已审批</td><td>%s</td></tr></table>" \
                   % self.applicant.nick_name
            self.message_post(body=message)
        self.state='4'
        self.current_handler=''

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):

        params = self._context.get('params', None)
        action = params.get("action", 0) if params else 0
        my_action = self.env["ir.actions.act_window"].search([('id', '=', action)])
        res = super(dtdream_budget, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=False)
        doc = etree.XML(res['arch'])
        if my_action.name != u"我的申请":
            if res['type'] == "form":
                doc.xpath("//form")[0].set("create", "false")
            if res['type'] == "tree":
                doc.xpath("//tree")[0].set("create", "false")
        res['arch'] = etree.tostring(doc)
        return res
    _sql_constraints = [
          ('budget_id_unique','unique(constract_id)','预算编号重复，请刷新页面重新填写！'),
          ('one_budget_monthly','unique(applicant,name)','每个月只能填写一次预算！')
     ]
#
    @api.multi
    def write(self, vals):

        if self.env.user.id != self.applicant.user_id.id:
            message_post_body=u"<table border=1><tr><th>字段</th><th>原值</th><th>新值</th></tr>"
            for val in vals:
                if val=='fee_daily':
                    for rec in vals[val]:
                        if rec[0]==2:
                            message_post_body+=u"<tr><td>日常业务费：项目或事务名称</td><td>%s</td><td>删除</td></tr>"%self['fee_daily'].search([('id','=',rec[1])])['daily_name']
                        elif rec[0]==0 or rec[0]==1:
                            for field in rec[2]:
                                message_post_body+=u"<tr><td>%s</td><td>%s</td><td>%s</td></tr>"%(("日常业务费："+self.env['dtdream.budget.daily']._columns[field].string).decode('utf-8'),self['fee_daily'].search([('id','=',rec[1])])[field] or "",rec[2][field] or "")
                elif val=='fee_travel':
                    for rec in vals[val]:
                        if rec[0]==2:
                            message_post_body+=u"<tr><td>公务差旅费</td><td>%s</td><td>删除</td></tr>"%self['fee_travel'].search([('id','=',rec[1])])['travel_name']
                        elif rec[0]==0 or rec[0]==1:
                            for field in rec[2]:
                                message_post_body+=u"<tr><td>%s</td><td>%s</td><td>%s</td></tr>"%(("公务差旅费："+self.env['dtdream.budget.travel']._columns[field].string).decode('utf-8'),self['fee_travel'].search([('id','=',rec[1])])[field] or "",rec[2][field] or "")
                elif val=='fee_zhuanx':
                    for rec in vals[val]:
                        if rec[0]==2:
                            message_post_body+=u"<tr><td>专项业务费：专项名称</td><td>%s</td><td>删除</td></tr>"%self['fee_zhuanx'].search([('id','=',rec[1])])['zhuanx_name']
                        elif rec[0]==0 or rec[0]==1:
                            for field in rec[2]:
                                message_post_body+=u"<tr><td>%s</td><td>%s</td><td>%s</td></tr>"%(("专项业务费："+self.env['dtdream.budget.zhuanx']._columns[field].string).decode('utf-8'),self['fee_zhuanx'].search([('id','=',rec[1])])[field] or "",rec[2][field] or "")
                elif val=='fee_xingz':
                    for rec in vals[val]:
                        if rec[0]==2:
                            message_post_body+=u"<tr><td>行政平台费：名称</td><td>%s</td><td>删除</td></tr>"%self['fee_xingz'].search([('id','=',rec[1])])['xingz_name']
                        elif rec[0]==0 or rec[0]==1:
                            for field in rec[2]:
                                message_post_body+=u"<tr><td>%s</td><td>%s</td><td>%s</td></tr>"%(("行政平台费："+self.env['dtdream.budget.xingz']._columns[field].string).decode('utf-8'),self['fee_xingz'].search([('id','=',rec[1])])[field] or "",rec[2][field] or "")
                elif val=='name':
                    message_post_body+=u"<tr><td>预算月份</td><td>%s</td><td>%s</td></tr>"%(self.env['dtdream.budget.month'].search([('id','=',self.name.id)]).name,self.env['dtdream.budget.month'].search([('id','=',vals[val])]).name)
            message_post_body+="</table>"
            if message_post_body != u"<table border=1><tr><th>字段</th><th>原值</th><th>新值</th></tr></table>":
                self.message_post(body=message_post_body)

        return super(dtdream_budget,self).write(vals)

    @api.model
    def send_email_regularly(self):
        if datetime.today().strftime('%d')=='25' or datetime.today().strftime('%d')=='30' or (datetime.today().strftime('%d')=='28' and datetime.today().strftime('%m')=='02'):
            action = self.env['ir.actions.act_window'].search([('name','=',u'我的申请'),('res_model','=','dtdream.budget')]).id
            menu_id = self.env['ir.ui.menu'].search([('name','=',u'预算管理')]).id
            base_url = self.env['ir.config_parameter'].search([('key','=','web.base.url')]).value
            url = base_url+'/web#min=1&limit=80&view_type=list&model=dtdream.budget&menu_id=%s&action=%s' % (menu_id,action)
            # url=base_url+link
            # 需要写预算部门的一级部门主管
            manager_fir = self.env['hr.department'].search([('is_budget_department','=',True),('parent_id','=',False)])
            # 需要写预算的部门
            in_department_ids = self.env['hr.department'].search([('is_budget_department','=',True)])
            # 除去一级部门主管需要写预算的人
            # in_ids = self.env['hr.employee'].search([('department_id','in',[rec.id for rec in in_department_ids]),('id','not in',[pe.id for pe in manager_fir])])
            # 除去一级部门主管需要写预算的人&下月预算没填写的人
            people = self.env['hr.employee'].search(['&','&',('department_id','in',[rec.id for rec in in_department_ids]),('id','not in',[pe.manager_id.id for pe in manager_fir]),'|',('budget_ids','=',False),('budget_ids','not like',datetime.strftime(datetime.today()+relativedelta(months=1),"%Y%m"))])

            if people:
                people_email_list = ''
                for person in people:
                    people_email_list += self.env['hr.employee'].search([('id','=',person.id)]).work_email+';'

                self.env['mail.mail'].create({
                        'subject': u'预算定时提醒' ,
                        'body_html': u'''
                        <p>您下月的预算还没有填写，请<a href="%s">点击此处</a>前往填写！</p>
                        <p>dodo</p
                        <p>万千业务，简单有do</p>
                        <p>%s</p>'''% (url,datetime.today().strftime('%Y-%m-%d')) ,
                        'email_from':self.env['ir.mail_server'].search([], limit=1).smtp_user,
                        'email_to': people_email_list,
                    }).send()


class dtdream_budget_wizard(models.TransientModel):
     _name = "dtdream.budget.wizard"
     reason = fields.Text("意见")
     temp=fields.Char(string="存储信息")

     @api.one
     def btn_confirm(self):

         current_record=self.env['dtdream.budget'].browse(self._context['active_id'])
         state_old = dict(self.env['dtdream.budget']._columns['state'].selection)[current_record.state]
         shenpiren = ''
         state_new = ''
         if current_record.state == '1':
             current_record.write({"his_handler": [(4,current_record.manager.id)]})
             shenpiren = current_record.manager.nick_name
         elif current_record.state == '2':
             current_record.write({"his_handler": [(4,current_record.signer_one.id)]})
             shenpiren = current_record.signer_one.nick_name
         elif current_record.state == '3':
             current_record.write({"his_handler": [(4,current_record.signer_two.id)]})
             shenpiren = current_record.signer_two.nick_name
         if self.temp=='reject':
             current_record.signal_workflow('btn_reject')
             state_new = dict(self.env['dtdream.budget']._columns['state'].selection)[current_record.state]

         elif self.temp=='agree':
             current_record.signal_workflow('btn_agree')
             state_new = dict(self.env['dtdream.budget']._columns['state'].selection)[current_record.state]

         message = u"<table border=1><tr><th>状态</th><th>审批人</th><th>审批意见</th></tr><tr><td>%s-->%s</td><td>%s</td><td>%s</td></tr></table>" \
                   % (unicode(state_old,'utf-8'), unicode(state_new,'utf-8'), shenpiren,self.reason)
         current_record.message_post(body=message)


class dtdream_hr_employee_extend(models.Model):
    _inherit = "hr.employee"
    budget_ids = fields.One2many('dtdream.budget','applicant',string='预算')

    @api.model
    def search_read(self,domain=None, fields=None, offset=0, limit=None, order=None, context=None):
        # 在tree视图的时候去掉一级部门主管，只在“查看未填写预算员工”菜单下有效
        try:
            menu = self.env["ir.actions.act_window"].search([('id','=',context['params']['action'])]).name
            print menu
            if menu == u'查看未填写预算员工':
                top_department = self.env['hr.department'].search([('parent_id','=',False),('is_budget_department','=',True)])
                top_manager = []
                for department in top_department:
                    top_manager.append(department.manager_id.id)
                    top_manager.append(department.manager_id.id)

                domain = expression.AND([[('id','not in',top_manager)],domain])
            recs = super(dtdream_hr_employee_extend, self).search_read(domain=domain, fields=fields, offset=offset,limit=limit, order=order)
            # for rec in recs:
            return super(dtdream_hr_employee_extend, self).search_read(domain=domain, fields=fields, offset=offset,limit=limit, order=order)
        except:
            recs = super(dtdream_hr_employee_extend, self).search_read(domain=domain, fields=fields, offset=offset,limit=limit, order=order)
            # for rec in recs:
            return super(dtdream_hr_employee_extend, self).search_read(domain=domain, fields=fields, offset=offset,limit=limit, order=order)

class dtdream_hr_department_zx(models.Model):
    _inherit = "hr.department"
    budget_sign_one = fields.Many2one("hr.employee",string="预算第一权签人")
    budget_sign_two = fields.Many2one("hr.employee",string="预算第二权签人")
    is_budget_department = fields.Boolean(string='是否要求预算申请')

    @api.constrains('is_budget_department')
    def _sub_deparment(self):
        children = self.child_ids
        for child in children:
            child.write({'is_budget_department':self.is_budget_department})


class dtdream_budget_month(models.Model):
    _name="dtdream.budget.month"
    name=fields.Char(string='预算月份')

class dtdream_budget_batch_operation(models.Model):
    _name = "dtdream.budget.batch.operation"
    temp = fields.Char(string="存储信息")

    @api.multi
    def batch_approval(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []
        for id in active_ids:
            current_record = self.env['dtdream.budget'].search([('id','=',id)])
            state_old = dict(self.env['dtdream.budget']._columns['state'].selection)[current_record.state]
            shenpiren = current_record.current_handler.nick_name
            state_new = ''
            if current_record.state == '1' or current_record.state == '2' or current_record.state == '3':
                current_record.write({"his_handler": [(4,current_record.current_handler.id)]})
                current_record.signal_workflow('btn_agree')
                state_new = dict(self.env['dtdream.budget']._columns['state'].selection)[current_record.state]
                message = u"<table border=1><tr><th>状态</th><th>审批人</th><th>审批意见</th></tr><tr><td>%s-->%s</td><td>%s</td><td>无</td></tr></table>" \
                   % (unicode(state_old,'utf-8'), unicode(state_new,'utf-8'), shenpiren)
                current_record.message_post(body=message)








