# -*- coding: utf-8 -*-

from openerp import models, fields, api
from datetime import datetime
from openerp.osv import expression
from openerp.exceptions import ValidationError, AccessError
from lxml import etree
import re

class dtdream_qualification_management(models.Model):
    _name = 'dtdream.qualification.management'
    _inherit = ['mail.thread']
    _description = u"任职申请表"

    batchnumber= fields.Char(string="批次号",required=True)

    name = fields.Many2one('hr.employee',string="申请人",required=True)

    @api.onchange('name')
    def _compute_employee_info(self):
        for rec in self:
            rec.department_id = rec.name.department_id.id
            rec.entry_day = rec.name.entry_day
            year1 = str(int(datetime.now().year)-1)+u'财年年度'
            year2 = str(int(datetime.now().year)-2) + u'财年年度'
            list1 = self.env["dtdream.hr.performance"].sudo().search([('name','=',rec.name.id),('quarter','in',(year1,year2))],order="id desc")
            if len(list1)>=2:
                rec.last_year_result = list1[0].result
                rec.year_before_result = list1[1].result
            elif len(list1)==1:
                rec.last_year_result = list1[0].result
                rec.year_before_result =""
            elif len(list1)<1:
                rec.last_year_result =""
                rec.year_before_result =""

    department_id = fields.Many2one('hr.department',string="申请人部门")
    entry_day = fields.Date(string="入职日期",compute=_compute_employee_info)
    manager_id = fields.Many2one('hr.employee',string="直接主管",required=True)
    post_type_id = fields.Many2one('dtdream.post.type',string="岗位类别")
    post_id =fields.Many2one('dtdream.post',string="申请岗位")
    rank = fields.Selection([('P1','助理级P1'),('P2','助理级P2'),('P3','助理级P3'),('P4','初级P4'),('P5','初级P5'),('P6','初级P6'),('P7','中级P7'),('P8','中级P8')
                             ,('P9','中级P9'),('P10','高级P10'),('P11','高级P11'),('P12','高级P12'),('P13','资深P13'),('P14','资深P14'),('P15','资深P15')],string="申请职级")

    last_year = fields.Char(string="年度",default=lambda self: int(datetime.now().year)-1,readonly=True)      #qunian
    last_year_result = fields.Char(string="绩效等级")
    year_before = fields.Char(string="年度",default=lambda self: int(datetime.now().year)-2,readonly=True)    #qiannian
    year_before_result = fields.Char(string="绩效等级")
    attachment = fields.Binary(string="附件(限制25M以下)", store=True)
    attachment_name = fields.Char(string='附件名')
    material_finish = fields.Selection([('Y','是'),('N','否')],string="申请材料是否完成",default="N")
    result_post = fields.Char(string='岗位')
    result_rank = fields.Char(string='职级')
    state = fields.Selection([('state1','待启动'),('state2','启动中'),('state3','认证完成')],string="状态",default="state1")
    dead_line = fields.Datetime(string="截止日期", readonly=True)
    is_over_dead_line = fields.Boolean(string="标识是否超期")


    @api.constrains('material_finish','rank','post_id','attachment')
    def _constraint_material_finish(self):
        if self.material_finish=='Y':
            if not self.rank or not self.post_id:
                raise ValidationError("请填写职级和岗位")
            if self.rank not in ('P1','P2','P3') and not self.attachment:
                raise ValidationError("申请P4级及以上员工需上传附件")

    @api.depends('dead_line')
    def dead_line_char_check(self):
        for rec in self:
            if rec.dead_line:
                rec.dead_line_char=format(datetime.strptime(rec.dead_line, "%Y-%m-%d %H:%M:%S"))[:10]

    dead_line_char = fields.Char(string="截止日期", readonly=True,compute =dead_line_char_check )

    _sql_constraints = [
        ('name_batchnumber_uniq', 'unique (name,batchnumber)', '每个员工每个批次只能有一条记录!')
    ]

    @api.model
    def create(self, vals):
        batchnumber = vals.get("batchnumber")
        p = re.match(u'(^RZ\d{4}0[1-9]$)|(^RZ\d{4}1[0-2]$)', batchnumber)
        if not p:
            raise ValidationError( u'批次号的格式必须是RZ+年份+月份，例：RZ201503' )
        result = super(dtdream_qualification_management, self).create(vals)
        return result

    @api.onchange('post_type_id')
    def onchang_post_type_id(self):
        domain = {}
        if self.post_type_id.id:
            domain["post_id"] = [('post_type_id', '=',self.post_type_id.id)]
            self.post_id = False
        else:
            domain["post_id"] = []
        return {"domain": domain}

    @api.onchange('post_id')
    def onchang_post_id(self):
        if self.post_id.id:
            self.post_type_id = self.post_id.post_type_id.id

    @api.model
    def check_is_over_dead_line(self):
        qua_list = self.sudo().search([("state","=","state2"),("dead_line","<",datetime.now().strftime("%Y-%m-%d %H:%M:%S"))])
        for qua in qua_list:
            qua.is_over_dead_line=True
        qua_list = self.sudo().search([("state", "=", "state2"), ("is_today_youcui", "=",True)])
        for qua in qua_list:
            qua.is_today_youcui = False

    @api.one
    def _compute_write_right(self):
        em = self.env['hr.employee'].search([('user_id', '=', self.env.uid)])
        if self.env.user.has_group("dtdream_qualification_management.group_hr_manage_qua"):
            self.is_manager=True
        if self.env.user.has_group("dtdream_qualification_management.group_hr_inter_qua"):
            department_id = []
            interfaces = self.env["dtdream.pbc.hr.interface"].search([('name', '=', em.id)])
            if len(interfaces) > 0:
                for interface in interfaces:
                    department_id.append(interface.department.id)
                    department_id = self.get_department_id(department_id, interface.department)
            if (self.department_id.id in department_id and self.state!='state3') or \
                    (self.name==em and self.state=='state2' and not self.is_over_dead_line):
                self.is_write_right_jk=True
            else:
                self.is_write_right_jk = False
        if self.name==em and self.state=='state2' and not self.is_over_dead_line:
            self.is_write_right = True
        else:
            self.is_write_right = False

    is_write_right_jk = fields.Boolean(string="是否可写jk",compute = _compute_write_right)
    is_write_right = fields.Boolean(string="是否可写pt", compute=_compute_write_right)
    is_manager = fields.Boolean(string="是否管理员",compute = _compute_write_right,default=True)
    is_today_youcui = fields.Boolean(string="今日已邮催",default=False)


    def get_base_url(self, cr, uid):
        base_url = self.pool.get('ir.config_parameter').get_param(cr, uid, 'web.base.url')
        return base_url

    def get_mail_server_name(self):
        return self.env['ir.mail_server'].sudo().search([], limit=1).smtp_user

    def get_department_id(self,department_id,department):
        if len(department.child_ids) > 0:
            for dep in department.child_ids:
                department_id.append(dep.id)
                if len(dep.child_ids) > 0:
                    self.get_department_id(department_id,dep)
        return department_id

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        params = self._context.get('params', None)
        action = params.get("action", 0) if params else 0
        my_action = self.env["ir.actions.act_window"].search([('id', '=', action)])
        res = super(dtdream_qualification_management, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar,
                                                               submenu=False)
        doc = etree.XML(res['arch'])
        if my_action.name == u"任职资格申请" or my_action.name == u"HRBP" :
            if res['type'] == "form":
                doc.xpath("//form")[0].set("create", "false")
            if res['type'] == "tree":
                doc.xpath("//tree")[0].set("create", "false")
            if res['type'] == "kanban":
                doc.xpath("//kanban")[0].set("create", "false")
        res['arch'] = etree.tostring(doc)
        return res

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        params = self._context.get('params', {})
        action = params.get('action', None)
        if action:
            menu = self.env["ir.actions.act_window"].search([('id', '=', action)]).name
            em = self.env['hr.employee'].search([('user_id', '=', self.env.uid)])
            if menu == u"任职资格申请":
                domain = expression.AND([['&',('state','!=','state1'),'|', ('name', '=', em.id),('manager_id', '=', em.id)], domain])
            if menu ==u"HRBP":
                if not self.env.user.has_group("dtdream_qualification_management.group_hr_manage_qua") and \
                        not self.env.user.has_group("dtdream_qualification_management.group_hr_inter_qua"):
                    raise AccessError('由于安全限制，请求的操作不能被完成。请联系你的系统管理员。\n\n(单据类型: dtdream.qualification.management, 操作: read)')
                department_id=[]
                interfaces = self.env["dtdream.pbc.hr.interface"].search([('name','=',em.id)])
                if len(interfaces)>0:
                    for interface in interfaces:
                        department_id.append(interface.department.id)
                        department_id = self.get_department_id(department_id,interface.department)
                domain = expression.AND([[('department_id.id', '=', department_id)], domain])
            if menu ==u'任职管理员':
                if not self.env.user.has_group("dtdream_qualification_management.group_hr_manage_qua"):
                    raise AccessError('由于安全限制，请求的操作不能被完成。请联系你的系统管理员。\n\n(单据类型: dtdream.qualification.management, 操作: read)')
        return super(dtdream_qualification_management, self).search_read(domain=domain, fields=fields, offset=offset,
                                                          limit=limit, order=order)

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, context=None, orderby=False, lazy=True):
        params = self._context.get('params', {})
        action = params.get('action', None)
        if action:
            menu = self.env["ir.actions.act_window"].search([('id', '=', action)]).name
            em = self.env['hr.employee'].search([('user_id', '=', self.env.uid)])
            if menu == u"任职资格申请":
                domain = expression.AND([['&',('state','!=','state1'),'|', ('name', '=', em.id), ('manager_id', '=', em.id)], domain])
            if menu == u"HRBP":
                if not self.env.user.has_group("dtdream_qualification_management.group_hr_manage_qua") and \
                        not self.env.user.has_group("dtdream_qualification_management.group_hr_inter_qua"):
                    raise AccessError('由于安全限制，请求的操作不能被完成。请联系你的系统管理员。\n\n(单据类型: dtdream.qualification.management, 操作: read)')
                department_id = []
                interfaces = self.env["dtdream.pbc.hr.interface"].search([('name', '=', em.id)])
                if len(interfaces) > 0:
                    for interface in interfaces:
                        department_id.append(interface.department.id)
                        department_id = self.get_department_id(department_id, interface.department)
                domain = expression.AND([[('department_id.id', '=', department_id)], domain])
            if menu ==u'任职管理员':
                if not self.env.user.has_group("dtdream_qualification_management.group_hr_manage_qua"):
                    raise AccessError('由于安全限制，请求的操作不能被完成。请联系你的系统管理员。\n\n(单据类型: dtdream.qualification.management, 操作: read)')
        res = super(dtdream_qualification_management, self).read_group(domain, fields, groupby, offset=offset, limit=limit,orderby=orderby, lazy=lazy)
        return res

    def get_qua_man_menu(self):
        menu = self.env['ir.ui.menu'].search([('name', '=', u'任职资格申请')], limit=1)
        menu_id = menu.parent_id.id
        action = menu.action.id
        return menu_id, action

    @api.model
    def send_youcui_email(self):
        name = self.name
        email_to = name.work_email
        appellation = u'{0},您好：'.format(name.name)
        base_url = self.get_base_url()
        menu_id, action = self.get_qua_man_menu()
        url = '%s/web#id=%s&view_type=form&model=dtdream.qualification.management&action=%s&menu_id=%s' % (
        base_url, self.id, action, menu_id)
        subject = u'【通知】请尽快查看填写你的任职资格申报'
        content = u'您的任职资格申报资料尚未填写完成,请尽快填写补全。'
        self.env['mail.mail'].create({
            'body_html': u'''<p>%s</p>
                                <p>%s</p>
                                <p><a href="%s">点击进入查看</a></p>
                                <p>dodo</p>
                                <p>万千业务，简单有do</p>
                                <p>%s</p>''' % (appellation, content, url, self.write_date[:10]),
            'subject': '%s' % subject,
            'email_from': self.get_mail_server_name(),
            'email_to': '%s' % email_to,
            'auto_delete': False,
        }).send()

    @api.model
    def if_in_hr_rz(self):
        if self.env.user.has_group("dtdream_qualification_management.group_hr_inter_qua") or self.env.user.has_group("dtdream_qualification_management.group_hr_manage_qua"):
            return True


class dtdream_email_number(models.Model):
    _name = 'dtdream.email.number'
    name =fields.Char(default="邮催个数设置")
    number= fields.Integer(string="个数",help=u"个数越大,邮件发送等待时间越长",default=10)


    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        cr = self.env["dtdream.email.number"].search([])
        res = super(dtdream_email_number, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=False)
        if res['type'] == "form":
            if cr:
                doc = etree.XML(res['arch'])
                doc.xpath("//form")[0].set("create", "false")
                res['arch'] = etree.tostring(doc)
        return res

    @api.model
    def create(self, vals):
        specificlist = self.env['dtdream.email.number'].search([])
        if len(specificlist) > 0:
            raise ValidationError(u'个数已设置')
        result = super(dtdream_email_number, self).create(vals)
        return result