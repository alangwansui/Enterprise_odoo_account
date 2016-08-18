# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.exceptions import ValidationError
from openerp.osv import expression
from lxml import etree
import time
import re


class dtdream_hr_performance(models.Model):
    _name = "dtdream.hr.performance"
    _inherit = ['mail.thread']
    _description = u"员工绩效目标"

    @api.onchange('department', 'quarter')
    def _onchange_compute_hr_pbc(self):
        if self.department and self.quarter:
            cr = self.env['dtdream.hr.pbc'].search([('state', '=', '99'), ('quarter', '=', self.quarter), '|', ('name', '=', self.department.parent_id.id), ('name', '=', self.department.id)])
            target = [t.id for crr in cr for t in crr.target]
            self.pbc = [(6, 0, target)]

    def refresh_when_department_changed(self, result=None):
        for cr in result:
            employee = cr.get('name', None)
            if isinstance(employee, tuple) and cr.get('department', None):
                crr = self.env['hr.employee'].search([('id', '=', employee[0])])
                cr['department'] = (crr.department_id.id, crr.department_id.complete_name)
        return result

    @api.multi
    def read(self, fields=None, load='_classic_read'):
        result = super(dtdream_hr_performance, self).read(fields=fields, load=load)
        result = self.refresh_when_department_changed(result)
        if len(result[0]) != 2 and result[0].get('pbc', 1) != 1:
            department = result[0]['department']
            self.department = department[0]
            cr = self.env['dtdream.hr.pbc'].search([('state', '=', '99'), ('quarter', '=', self.quarter), '|', ('name', '=', self.department.parent_id.id), ('name', '=', self.department.id)])
            target_level1 = [t.id for crr in cr for t in crr.target if t.level == 1]
            target_level2 = [t.id for crr in cr for t in crr.target if t.level == 2]
            target = target_level1 + target_level2
            result[0]['pbc'] = target
            self.write({"pbc": [(6, 0, target)]})
        return result

    def update_dtdream_hr_pbc(self):
        for rec in self:
            cr = rec.env['dtdream.hr.pbc'].search([('state', '=', '99'), ('quarter', '=', rec.quarter), '|', ('name', '=', rec.department.parent_id.id), ('name', '=', rec.department.id)])
            target = [t.id for crr in cr for t in crr.target]
            rec.write({"pbc": [(6, 0, target)]})

    @api.depends('name')
    def _compute_employee_info(self):
        for rec in self:
            rec.workid = rec.name.job_number
            rec.department = rec.name.department_id
            rec.onwork = rec.name.Inaugural_state

    @api.depends('name')
    def _compute_name_is_login(self):
        if self.env.user == self.name.user_id:
            self.login = True
        else:
            self.login = False

    def _compute_officer_is_login(self):
        if self.env.user == self.officer.user_id:
            self.is_officer = True
        else:
            self.is_officer = False

    def _compute_login_is_manage(self):
        if self.env.ref("dtdream_hr_performance.group_hr_manage_performance") in self.env.user.groups_id:
            self.manage = True
        else:
            self.manage = False

    def _compute_login_is_inter(self):
        for rec in self:
            if rec.env.ref("dtdream_hr_performance.group_hr_inter_performance") in rec.env.user.groups_id:
                rec.inter = True
            else:
                rec.inter = False

    def check_access_right_create(self, vals):
        department = []
        manage = self.env.ref("dtdream_hr_performance.group_hr_manage_performance") not in self.env.user.groups_id
        if manage:
            inter = self.env['dtdream.pbc.hr.interface'].search([('name.user_id', '=', self.env.user.id)])
            for crr in inter:
                department.append(crr.department.id)
                for depart in crr.department.child_ids:
                    department.append(depart.id)
            employee = self.env['hr.employee'].search([('id', '=', vals.get('name', 0))])
            if employee.department_id.id not in department:
                raise ValidationError("HR接口人只能创建所接口部门员工的绩效考核单!")

    def validate_quarter_check(self, quarter):
        p = re.match(u'\d{4}财年Q[1-4]', quarter)
        if not p:
            raise ValidationError('考核季度格式必须是xxxx财年Q1~Q4, 如2016财年Q1')

    @api.model
    def create(self, vals):
        self.validate_quarter_check(vals.get('quarter'))
        self.check_access_right_create(vals)
        pbc = vals.get('pbc', '')
        if not pbc:
            employee = self.env['hr.employee'].search([('id', '=', vals.get('name', 0))])
            pbc = self.env['dtdream.hr.pbc'].search([('state', '=', '99'), ('quarter', '=', vals.get('quarter', '')),
                                                     '|', ('name', '=', employee.department_id.parent_id.id),
                                                     ('name', '=', employee.department_id.id)])
            vals['pbc'] = [(4, t.id) for crr in pbc for t in crr.target]
        else:
            for val in pbc:
                val[0] = 4
            vals['pbc'] = pbc
        result = super(dtdream_hr_performance, self).create(vals)
        self.unlink_message_subscribe(result.id)
        return result

    @api.multi
    def unlink(self):
        for rec in self:
            manage = rec.env.ref("dtdream_hr_performance.group_hr_manage_performance") not in rec.env.user.groups_id
            if manage:
                raise ValidationError("仅绩效管理员可以删除员工绩效单!")
        return super(dtdream_hr_performance, self).unlink()

    def track_pbc_value_change(self, vals):
        tab = u"<ul class='o_mail_thread_message_tracking'>"
        message = u'''<li>个人绩效目标:<table width='750px' border='1px' style='table-layout:fixed;'><thead><tr>
                    <th style='width: 40px;'>动作</th><th style='width: 100px;'>工作目标</th><th style='width: 310px'>
                    具体描述(请清晰说明完成该目标所需要的关键措施)</th><th style='width: 300px;'>关键事件达成</th>
                    </tr></thead><tbody>'''
        tracked = False
        add = u''
        if vals.get('name', ''):
            name = self.env['hr.employee'].search([('id', '=', vals.get('name'))]).name
            if self.name.name != name:
                tab += u"<li>花名:<span>{0}</span>更改为:<span>{1}</span></li>".format(self.name.name, name)
        if vals.get('officer', ''):
            name = self.env['hr.employee'].search([('id', '=', vals.get('officer'))]).name
            if self.officer.name != name:
                tab += u"<li>一考主管:<span>{0}</span>更改为:<span>{1}</span></li>".format(self.officer.name, name)
        if vals.get('officer_sec', ''):
            name = self.env['hr.employee'].search([('id', '=', vals.get('officer_sec'))]).name
            if self.officer_sec.name != name:
                tab += u"<li>二考主管:<span>{0}</span>更改为:<span>{1}</span></li>".format(self.officer_sec.name, name)
        if vals.get('quarter', ''):
            if vals.get('quarter') != self.quarter:
                tab += u"<li>考核季度:<span>{0}</span>更改为:<span>{1}</span></li>".format(self.quarter, vals.get('quarter'))
        if vals.get('result', ''):
            if vals.get('result') != self.result:
                tab += u"<li>考核结果:<span>{0}</span>更改为:<span>{1}</span></li>".format(self.result, vals.get('result'))
        target = vals.get('pbc_employee', [])
        for rec in target:
            cr = self.env['dtdream.hr.pbc.employee'].search([('id', '=', rec[1])])
            if rec[0] == 1:
                tracked = True
                field = rec[2]
                if field.get('work', None):
                    message += u"<tr><td>修改</td><td style='color: red; word-wrap:break-word;'>%s</td>" % field.get('work')
                else:
                    message += u"<tr><td>修改</td><td style='word-wrap:break-word;'>%s</td>" % cr.work
                if field.get('detail', None):
                    message += u"<td style='color: red;word-wrap:break-word;'>%s</td>" % field.get('detail')
                else:
                    message += u"<td style='word-wrap:break-word;'>%s</td>" % cr.detail
                if field.get('result', None):
                    message += u"<td style='color: red;word-wrap:break-word;'>%s</td>" % field.get('result')
                else:
                    message += u"<td style='word-wrap:break-word;'>%s</td>" % cr.result
                # if field.get('evaluate', None):
                #     message += u"<td style='color: red;word-wrap:break-word;'>%s</td>" % field.get('evaluate')
                # else:
                #     message += u"<td style='word-wrap:break-word;'>%s</td>" % cr.evaluate
            elif rec[0] == 0:
                tracked = True
                field = rec[2]
                add += u'''<tr style='color: red;'><td>新增</td><td style='word-wrap:break-word;'>{0}</td>
                <td style='word-wrap:break-word;'>{1}</td><td style='word-wrap:break-word;'>{2}</td></tr>'''.format(
                    field.get('work', ''), field.get('detail', ''), field.get('result', ''))
            elif rec[0] == 2:
                tracked = True
                message += u'''<tr style='color: red;'><td>删除</td><td style='word-wrap:break-word;'>{0}</td>
                <td style='word-wrap:break-word;'>{1}</td><td style='word-wrap:break-word;'>{2}</td></tr>'''.format(
                    cr.work, cr.detail, cr.result)
        if not tracked:
            message = tab + u'</ul>'
            if message == u"<ul class='o_mail_thread_message_tracking'></ul>":
                return ''
            return message.replace("False", '')
        message = tab + message + add + u"</tbody></table></li></ul>"
        return message.replace("False", '')

    @api.multi
    def write(self, vals, flag=True):
        if vals.get('quarter'):
            self.validate_quarter_check(vals.get('quarter'))
        message = self.track_pbc_value_change(vals)
        if message:
            self.message_post(body=message)
        result = vals.get('result', '')
        if result and result.strip():
            if self.state == "6":
                self.signal_workflow('btn_import')
            else:
                subject = u'【通知】您的绩效考核结果已导入'
                content = u'绩效考核结果已导入,请查看。如有疑问,可咨询各部门HRBP。'
                self.send_mail(self.name, subject=subject, content=content)
                self.message_post(body=u'绩效考核结果导入')
        return super(dtdream_hr_performance, self).write(vals)

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        params = self._context.get('params', {})
        action = params.get('action', None)
        if action:
            menu = self.env["ir.actions.act_window"].search([('id', '=', action)]).name
        if menu == u"所有单据" or menu == u"绩效管理":
            if self.env.ref("dtdream_hr_performance.group_hr_manage_performance") in self.env.user.groups_id:
                domain = domain if domain else []
            elif self.env.ref("dtdream_hr_performance.group_hr_inter_performance") in self.env.user.groups_id:
                cr = self.env['dtdream.pbc.hr.interface'].search([('name.user_id', '=', self.env.user.id)])
                department_id = []
                for crr in cr:
                    department_id.append(crr.department.id)
                    for department in crr.department.child_ids:
                        department_id.append(department.id)
                domain = domain + [("department", 'in', department_id)] if domain else [("department", 'in', department_id)]
            else:
                uid = self._context.get('uid', '')
                if domain:
                    domain = expression.AND([['|', ('department.parent_id.manager_id.user_id', '=', uid), '|',
                                              ('officer_sec.user_id', '=', uid), '|', ('officer.user_id', '=', uid),
                                              '&', ('name.user_id', '=', uid), ('state', '!=', '0')], domain])
                    # value = []
                    # for key in domain:
                    #     value += ['&', key]
                    # value.pop(-2)
                    # a = ['|', '&'] + [('department.parent_id.manager_id.user_id', '=', uid)] + value
                    # b = ['|', '&'] +  [('officer.user_id', '=', uid)] + value
                    # c = ['|', '&'] + [('officer_sec.user_id', '=', uid)] + value
                    # d = ['&', ('name.user_id', '=', uid), '&', ('state', '!=', '0')] + value
                    # domain = a + b + c + d
                else:
                    domain = ['|', ('department.parent_id.manager_id.user_id', '=', uid), '|',
                              ('officer_sec.user_id', '=', uid), '|', ('officer.user_id', '=', uid),
                              '&', ('name.user_id', '=', uid), ('state', '!=', '0')]
        return super(dtdream_hr_performance, self).search_read(domain=domain, fields=fields, offset=offset,
                                                               limit=limit, order=order)

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        params = self._context.get('params', None)
        action = params.get("action", 0) if params else 0
        my_action = self.env["ir.actions.act_window"].search([('id', '=', action)])
        res = super(dtdream_hr_performance, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=False)
        doc = etree.XML(res['arch'])
        if my_action.name != u"绩效管理":
            has_delete = self.env.ref("dtdream_hr_performance.group_hr_manage_performance") not in self.env.user.groups_id
            if res['type'] == "form":
                doc.xpath("//form")[0].set("create", "false")
                if has_delete:
                    doc.xpath("//form")[0].set("delete", "false")
            if res['type'] == "tree":
                doc.xpath("//tree")[0].set("create", "false")
                if has_delete:
                    doc.xpath("//tree")[0].set("delete", "false")
        else:
            inter = self.env.ref("dtdream_hr_performance.group_hr_inter_performance") not in self.env.user.groups_id
            manage = self.env.ref("dtdream_hr_performance.group_hr_manage_performance") not in self.env.user.groups_id
            if inter and manage:
                if res['type'] == "form":
                    doc.xpath("//form")[0].set("create", "false")
                if res['type'] == "tree":
                    doc.xpath("//tree")[0].set("create", "false")
            if manage:
                if res['type'] == "form":
                    doc.xpath("//form")[0].set("delete", "false")
                if res['type'] == "tree":
                    doc.xpath("//tree")[0].set("delete", "false")
        res['arch'] = etree.tostring(doc)
        return res

    def unlink_message_subscribe(self, res_id):
        self.env['mail.followers'].search([('res_model', '=', 'dtdream.hr.performance'), ('res_id', '=', res_id)]).unlink()

    def get_mail_server_name(self):
        return self.env['ir.mail_server'].search([], limit=1).smtp_user

    def get_base_url(self, cr, uid):
        base_url = self.pool.get('ir.config_parameter').get_param(cr, uid, 'web.base.url')
        return base_url

    def get_hr_performance_menu(self):
        menu_id = self.env['ir.ui.menu'].search([('name', '=', u'绩效')], limit=1).id
        menu = self.env['ir.ui.menu'].search([('name', '=', u'所有单据'), ('parent_id', '=', menu_id)], limit=1)
        action = menu.action.id
        return menu_id, action

    def send_mail(self, name, subject, content):
        email_to = name.work_email
        appellation = u'{0},您好：'.format(name.name)
        base_url = self.get_base_url()
        menu_id, action = self.get_hr_performance_menu()
        url = '%s/web#id=%s&view_type=form&model=dtdream.hr.performance&action=%s&menu_id=%s' % (base_url, self.id, action, menu_id)
        subject = subject
        content = content
        self.env['mail.mail'].create({
                'body_html': u'''<p>%s</p>
                                <p>%s</p>
                                <p><a href="%s">点击进入查看</a></p>
                                <p><a href='http://confluence.dtdream.com/pages/viewpage.action?pageId=46465483'>
                                点此查看绩效考核具体流程</a></p>
                                <p>dodo</p>
                                <p>万千业务，简单有do</p>
                                <p>%s</p>''' % (appellation, content, url, self.write_date[:10]),
                'subject': '%s' % subject,
                'email_from': self.get_mail_server_name(),
                'email_to': '%s' % email_to,
                'auto_delete': False,
            }).send()

    @api.model
    def default_get(self, fields):
        rec = super(dtdream_hr_performance, self).default_get(fields)
        if self.env.ref("dtdream_hr_performance.group_hr_manage_performance") in self.env.user.groups_id:
            rec.update({"manage": True})
        else:
            rec.update({"manage": False})
        if self.env.ref('dtdream_hr_performance.group_hr_inter_performance') in self.env.user.groups_id:
            rec.update({"inter": True})
        else:
            rec.update({"inter": False})
        return rec

    @api.depends('name', 'quarter')
    def _compute_has_pbc_log(self):
        cr = self.env['dtdream.hr.pbc'].search([('state', '=', '99'), ('quarter', '=', self.quarter), '|', ('name', '=', self.department.parent_id.id), ('name', '=', self.department.id)])
        target = [t.id for crr in cr for t in crr.target]
        if target:
            self.pbc_log = True
        else:
            self.pbc_log = False

    name = fields.Many2one('hr.employee', string='花名', required=True)
    department = fields.Many2one('hr.department', string='部门', compute=_compute_employee_info, store=True)
    workid = fields.Char(string='工号', compute=_compute_employee_info, store=True)
    quarter = fields.Char(string='考核季度', required=True)
    officer = fields.Many2one('hr.employee', string='一考主管', required=True)
    officer_sec = fields.Many2one('hr.employee', string='二考主管', required=True)
    result = fields.Char(string='考核结果')
    evaluate_officer = fields.Text(string='总体评价', help='请管理者结合员工的关键目标完成进展，以及过程中的绩效沟通进行综合评价。(不少于50字)')
    onwork = fields.Selection([('Inaugural_state_01', '在职'), ('Inaugural_state_02', '离职')],
                              string="在职状态", compute=_compute_employee_info)
    state = fields.Selection([('0', '待启动'),
                              ('1', '待填写绩效目标'),
                              ('2', '待主管确认'),
                              ('3', '待考评启动'),
                              ('4', '待总结'),
                              ('5', '待主管评价'),
                              ('6', '待最终考评'),
                              ('99', '考评完成')
                              ], string='状态', default='0')
    pbc = fields.Many2many('dtdream.pbc.target', string="部门绩效目标")
    pbc_employee = fields.One2many('dtdream.hr.pbc.employee', 'perform', string='个人绩效目标')
    pbc_log = fields.Boolean(compute=_compute_has_pbc_log)
    login = fields.Boolean(compute=_compute_name_is_login)
    is_officer = fields.Boolean(compute=_compute_officer_is_login)
    view_all = fields.Boolean(default=lambda self: True)
    up_officer = fields.Boolean(string='上级部门主管', default=lambda self: True)
    inter = fields.Boolean(string='当前登入者是否接口人', compute=_compute_login_is_inter)
    manage = fields.Boolean(string='当前登入者是否绩效管理员', compute=_compute_login_is_manage)

    _sql_constraints = [
        ('name_quarter_uniq', 'unique (name,quarter)', '每个员工每个季度只能有一条员工绩效目标!')
    ]

    @api.multi
    def wkf_wait_write(self):
        if self.state == '0':
            subject = u'【通知】%s个人绩效目标填写已启动' % self.quarter
            content = u'''您的个人季度绩效目标填写已启动,请根据部门季度绩效目标、及与主管沟通的情况,详细填写%s的工作目标,
            并描述将如何达成该目标,采取哪些措施。''' % self.quarter
            self.send_mail(self.name, subject=subject, content=content)
            self.message_post(body=u'个人绩效目标填写启动')
        elif self.state != '3':
            subject = u'【通知】个人绩效目标已被返回修改'
            content = u"您的个人季度绩效目标已被返回修改,请完善后提交主管确认!"
            self.send_mail(self.name, subject=subject, content=content)
        self.write({'state': '1'})

    @api.multi
    def wkf_confirm(self):
        self.write({'state': '2'})
        subject = u'【通知】%s提交了个人绩效目标' % self.name.name
        content = u'%s的个人季度绩效目标已制定,请确认;如该季度绩效目标不够完善,请点击"返回修改"要求员工进一步调整。' % self.name.name
        self.send_mail(self.officer, subject=subject, content=content)
        self.message_post(body=u'%s提交了个人绩效目标' % self.name.name)

    @api.multi
    def wkf_evaluate(self):
        self.write({'state': '3'})
        subject = u'【通知】%s确认了您的个人绩效目标' % self.officer.name
        content = u"%s已针对您的个人季度绩效目标完成确认,请查阅。" % self.officer.name
        self.send_mail(self.name, subject=subject, content=content)

    @api.multi
    def wkf_conclud(self):
        self.write({'state': '4'})
        subject = u'【通知】%s个人绩效考核已启动' % self.quarter
        content = u"绩效考核已正式启动,请根据个人季度绩效目标、以及实际完成情况,填写%s关键事项达成情况与主要工作成果。" % self.quarter
        self.send_mail(self.name, subject=subject, content=content)
        self.message_post(body=u'个人绩效考评启动')

    @api.multi
    def wkf_rate(self):
        self.write({'state': '5'})
        subject = u'【通知】%s提交了个人绩效目标总结' % self.name.name
        content = u'%s已完成个人工作总结，请根据员工实际工作情况进行评价，指导员工取得更好的进步!' % self.name.name
        self.send_mail(self.officer, subject=subject, content=content)
        self.message_post(body=u'%s提交了个人绩效目标总结' % self.name.name)

    @api.multi
    def wkf_final(self):
        if self.result:
            self.write({'state': '99'})

        else:
            self.write({'state': '6'})
        subject = u'【通知】%s对您的个人绩效目标做了评价' % self.officer.name
        content = u'%s已针对您的工作总结完成了评价,请查阅!' % self.officer.name
        self.send_mail(self.name, subject=subject, content=content)
        self.message_post(body=u'%s对个人绩效目标做了评价' % self.officer.name)

    @api.multi
    def wkf_done(self):
        self.write({'state': '99'})
        subject = u'【通知】您的绩效考核结果已导入'
        content = u'绩效考核结果已导入,请查看。如有疑问,可咨询各部门HRBP。'
        self.send_mail(self.name, subject=subject, content=content)
        self.message_post(body=u'绩效考核结果导入')


class dtdream_hr_pbc_employee(models.Model):
    _name = "dtdream.hr.pbc.employee"

    @api.depends('inter')
    def _compute_state_related(self):
        for rec in self:
            rec.state = rec.perform.state
            rec.officer = rec.perform.officer

    @api.depends('inter')
    def _compute_name_is_login(self):
        for rec in self:
            if rec.env.user == rec.perform.name.user_id:
                rec.login = True
            else:
                rec.login = False

    def _compute_login_is_officer(self):
        for rec in self:
            if rec.env.user == rec.perform.officer.user_id:
                rec.officer = True
            else:
                rec.officer = False

    def _compute_login_is_manage(self):
        for rec in self:
            rec.manage = rec.perform.manage

    def _compute_login_is_inter(self):
        for rec in self:
            rec.inter = rec.perform.inter

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state == '4' and rec.env.user == rec.perform.name.user_id:
                raise ValidationError("无法删除审批中的记录!")
            if rec.state == '5' and rec.env.user == rec.perform.officer.user_id:
                raise ValidationError("主管无法删除员工个人绩效目标记录!")
        return super(dtdream_hr_pbc_employee, self).unlink()

    @api.model
    def create(self, vals):
        performance = self.env['dtdream.hr.performance'].search([('id', '=', vals.get('perform', 0))])
        state = performance.state
        inter = self.env.ref("dtdream_hr_performance.group_hr_inter_performance") not in self.env.user.groups_id
        manage = self.env.ref("dtdream_hr_performance.group_hr_manage_performance") in self.env.user.groups_id
        if state not in ("1", "4") and inter:
            raise ValidationError("无法新增员工个人绩效目标记录!")
        elif state not in ("1", "4") and not inter and not manage and performance.name.user_id == self.env.user:
            raise ValidationError("无法新增员工个人绩效目标记录!")
        return super(dtdream_hr_pbc_employee, self).create(vals)

    @api.model
    def default_get(self, fields):
        rec = super(dtdream_hr_pbc_employee, self).default_get(fields)
        if self.env.ref("dtdream_hr_performance.group_hr_manage_performance") in self.env.user.groups_id:
            rec.update({"manage": True})
        else:
            rec.update({"manage": False})
        if self.env.ref("dtdream_hr_performance.group_hr_inter_performance") in self.env.user.groups_id:
            rec.update({"inter": True})
        else:
            rec.update({"inter": False})
        return rec

    perform = fields.Many2one('dtdream.hr.performance')
    work = fields.Text(string='工作目标')
    detail = fields.Text(string='具体描述(请清晰说明完成该目标所需要的关键措施)')
    result = fields.Text(string='关键事件达成')
    evaluate = fields.Text(string='主管评价')
    login = fields.Boolean(compute=_compute_name_is_login)
    officer = fields.Boolean(compute=_compute_login_is_officer)
    manage = fields.Boolean(string='当前登入者是否绩效管理员', compute=_compute_login_is_manage)
    inter = fields.Boolean(string='当前登入者是否接口人', compute=_compute_login_is_inter)
    state = fields.Selection([('0', '待启动'),
                              ('1', '待填写绩效目标'),
                              ('2', '待主管确认'),
                              ('3', '待考评启动'),
                              ('4', '待总结'),
                              ('5', '待主管评价'),
                              ('6', '待最终考评'),
                              ('99', '考评完成')
                              ], string='状态', default='1', compute=_compute_state_related)


class dtdream_hr_pbc(models.Model):
    _name = "dtdream.hr.pbc"
    _inherit = ['mail.thread']
    _description = u'部门绩效目标'

    def get_inter_employee(self):
        cr = self.env['dtdream.pbc.hr.config'].search([], limit=1)
        inter = [rec.name.user_id for rec in cr.interface]
        return inter

    @api.multi
    def _compute_login_is_manage(self):
        for rec in self:
            if rec.env.ref("dtdream_hr_performance.group_hr_manage_performance") not in rec.env.user.groups_id:
                rec.manage = False
            else:
                rec.manage = True

    @api.multi
    def _compute_inter_edit(self):
        for rec in self:
            if rec.env.ref("dtdream_hr_performance.group_hr_inter_performance") not in rec.env.user.groups_id:
                rec.inter_edit = False
            else:
                department = []
                inter = rec.env['dtdream.pbc.hr.interface'].search([('name.user_id', '=', rec.env.user.id)])
                for crr in inter:
                    department.append(crr.department.id)
                    for depart in crr.department.child_ids:
                        department.append(depart.id)
                if rec.name.id not in department:
                    rec.inter_edit = False
                else:
                    rec.inter_edit = True

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        if self.env.ref("dtdream_hr_performance.group_hr_inter_performance") in self.env.user.groups_id:
            domain = domain if domain else []
        else:
            crr = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)])
            department_id = [department.id for department in crr.department_id.parent_id]
            department_id.append(crr.department_id.id)
            domain = domain + [("name", 'in', department_id), ('state', '=', '99')] if domain else\
                [("name", 'in', department_id), ('state', '=', '99')]
        return super(dtdream_hr_pbc, self).search_read(domain=domain, fields=fields, offset=offset,
                                                       limit=limit, order=order)

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(dtdream_hr_pbc, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=False)
        doc = etree.XML(res['arch'])
        inter = self.env.ref("dtdream_hr_performance.group_hr_inter_performance") not in self.env.user.groups_id
        manage = self.env.ref("dtdream_hr_performance.group_hr_manage_performance") not in self.env.user.groups_id
        if inter and manage:
            if res['type'] == "form":
                doc.xpath("//form")[0].set("create", "false")
                doc.xpath("//form")[0].set("edit", "false")
            if res['type'] == "tree":
                doc.xpath("//tree")[0].set("create", "false")
                doc.xpath("//tree")[0].set("edit", "false")
        res['arch'] = etree.tostring(doc)
        return res

    @api.multi
    def unlink(self):
        for rec in self:
            department = []
            manage = rec.env.ref("dtdream_hr_performance.group_hr_manage_performance") not in rec.env.user.groups_id
            if manage:
                inter = rec.env['dtdream.pbc.hr.interface'].search([('name.user_id', '=', rec.env.user.id)])
                if rec.env.ref("dtdream_hr_performance.group_hr_inter_performance") not in rec.env.user.groups_id:
                    raise ValidationError("普通员工无法删除部门绩效目标!")
                for crr in inter:
                    department.append(crr.department.id)
                    for depart in crr.department.child_ids:
                        department.append(depart.id)
                if rec.name.id not in department:
                    raise ValidationError("HR接口人只能删除所接口部门的部门绩效目标!")
        return super(dtdream_hr_pbc, self).unlink()

    def track_pbc_value_change(self, vals):
        tab = u"<ul class='o_mail_thread_message_tracking'>"
        message = u'''<li>部门目标:<table width='800px' border='1px' style='table-layout:fixed;'><thead><tr>
                    <th style='width: 40px;'>动作</th><th style='width: 300px;'>业务目标</th><th style='width: 460px'>
                    关键指标,关键动作,行为</th></tr></thead><tbody>'''
        tracked = False
        add = u''
        if vals.get('name', ''):
            name = self.env['hr.department'].search([('id', '=', vals.get('name'))]).complete_name
            tab += u"<li>部门:<span>{0}</span>更改为:<span>{1}</span></li>".format(self.name.complete_name, name)
        if vals.get('quarter', ''):
            tab += u"<li>考核季度:<span>{0}</span>更改为:<span>{1}</span></li>".format(self.quarter, vals.get('quarter'))
        target = vals.get('target', [])
        for rec in target:
            cr = self.env['dtdream.pbc.target'].search([('id', '=', rec[1])])
            if rec[0] == 1:
                tracked = True
                field = rec[2]
                if field.get('num', None):
                    message += u"<tr><td>修改</td><td style='color: red; word-wrap:break-word;'>%s</td>" % field.get('num')
                else:
                    message += u"<tr><td>修改</td><td style='word-wrap:break-word;'>%s</td>" % cr.num
                if field.get('works', None):
                    message += u"<td style='color: red;word-wrap:break-word;'>%s</td>" % field.get('works')
                else:
                    message += u"<td style='word-wrap:break-word;'>%s</td>" % cr.works
            elif rec[0] == 0:
                tracked = True
                field = rec[2]
                add += u'''<tr style='color: red;'><td>新增</td><td style='word-wrap:break-word;'>{0}</td>
                <td style='word-wrap:break-word;'>{1}</td></tr>'''.format(field.get('num'), field.get('works'))
            elif rec[0] == 2:
                tracked = True
                message += u'''<tr style='color: red;'><td>删除</td><td style='word-wrap:break-word;'>{0}</td>
                <td style='word-wrap:break-word;'>{1}</td></tr>'''.format(cr.num, cr.works)
        if not tracked:
            message = tab + u'</ul>'
            if message == u"<ul class='o_mail_thread_message_tracking'></ul>":
                return ''
            return message
        message = tab + message + add + u"</tbody></table></li></ul>"
        return message

    def validate_quarter_check(self, quarter):
        p = re.match(u'\d{4}财年Q[1-4]', quarter)
        if not p:
            raise ValidationError('考核季度格式必须是xxxx财年Q1~Q4, 如2016财年Q1')

    @api.multi
    def write(self, vals, flag=True):
        if vals.get('quarter'):
            self.validate_quarter_check(vals.get('quarter'))
        message = self.track_pbc_value_change(vals)
        if message:
            self.message_post(body=message)
        if flag:
            department = []
            manage = self.env.ref("dtdream_hr_performance.group_hr_manage_performance") not in self.env.user.groups_id
            if manage:
                inter = self.env['dtdream.pbc.hr.interface'].search([('name.user_id', '=', self.env.user.id)])
                for crr in inter:
                    department.append(crr.department.id)
                    for depart in crr.department.child_ids:
                        department.append(depart.id)
                if self.name.id not in department:
                    raise ValidationError("HR接口人只能编辑所接口部门的部门绩效目标!")
            employee = self.env['hr.employee'].search(['|', ('department_id', '=', self.name.id), ('department_id', 'in', [cr.id for cr in self.name.child_ids])])
            if vals.get('target', '') or vals.get('quarter', '') or vals.get('name'):
                for name in employee:
                    subject = u'【温馨提示】%s部门绩效业务目标修改通知'% self.quarter
                    content = u'%s%s部门绩效业务目标或关键指标,关键动作,行为已修改,请进入dodo绩效查看，或点击链接' % (self.name.complete_name, self.quarter)
                    self.send_mail(name, subject=subject, content=content)
                    time.sleep(0.01)
        return super(dtdream_hr_pbc, self).write(vals)

    def unlink_message_subscribe(self, res_id):
        self.env['mail.followers'].search([('res_model', '=', 'dtdream.hr.pbc'), ('res_id', '=', res_id)]).unlink()

    @api.model
    def create(self, vals):
        self.validate_quarter_check(vals.get('quarter'))
        department = []
        manage = self.env.ref("dtdream_hr_performance.group_hr_manage_performance") not in self.env.user.groups_id
        if manage:
            inter = self.env['dtdream.pbc.hr.interface'].search([('name.user_id', '=', self.env.user.id)])
            for crr in inter:
                department.append(crr.department.id)
                for depart in crr.department.child_ids:
                    department.append(depart.id)
            if vals.get('name', '') not in department:
                raise ValidationError("HR接口人只能创建所接口部门的部门绩效目标!")
        result = super(dtdream_hr_pbc, self).create(vals)
        self.unlink_message_subscribe(result.id)
        return result

    def get_base_url(self, cr, uid):
        base_url = self.pool.get('ir.config_parameter').get_param(cr, uid, 'web.base.url')
        return base_url

    def get_hr_performance_menu(self):
        menu = self.env['ir.ui.menu'].search([('name', '=', u'部门绩效目标')], limit=1)
        menu_id = menu.parent_id.id
        action = menu.action.id
        return menu_id, action

    def get_mail_server_name(self):
        return self.env['ir.mail_server'].search([], limit=1).smtp_user

    def send_mail(self, name, subject, content):
        email_to = name.work_email
        appellation = u'{0},您好：'.format(name.name)
        base_url = self.get_base_url()
        menu_id, action = self.get_hr_performance_menu()
        url = '%s/web#id=%s&view_type=form&model=dtdream.hr.pbc&action=%s&menu_id=%s' % (base_url, self.id, action, menu_id)
        subject = subject
        content = content
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

    def _get_name_domain(self):
        inter = self.env.ref("dtdream_hr_performance.group_hr_inter_performance") in self.env.user.groups_id
        manage = self.env.ref("dtdream_hr_performance.group_hr_manage_performance") not in self.env.user.groups_id
        if inter and manage:
            department = []
            departments = self.env['dtdream.pbc.hr.interface'].search([('name.user_id', '=', self.env.user.id)])
            for crr in departments:
                department.append(crr.department.id)
                for depart in crr.department.child_ids:
                    department.append(depart.id)
            return [('id', 'in', department)]
        else:
            return [('id', '!=', False)]

    name = fields.Many2one('hr.department', string='部门', required=True, domain=_get_name_domain)
    is_inter = fields.Boolean(string="是否接口人", default=lambda self: True)
    is_in_department = fields.Boolean(string='是否所在部门')
    manage = fields.Boolean(string='是否绩效管理员', compute=_compute_login_is_manage)
    inter_edit = fields.Boolean(string='是否可以编辑', compute=_compute_inter_edit, default=lambda self: True)
    quarter = fields.Char(string='考核季度', required=True)
    state = fields.Selection([('0', '草稿'),
                              ('99', '完成'),
                              ], string='状态', default='0')
    target = fields.One2many('dtdream.pbc.target', 'target', string='工作内容')

    _sql_constraints = [
        ('name_quarter_uniq', 'unique (name,quarter)', '每个季度只能有一条绩效目标!')
    ]

    @api.multi
    def wkf_done(self):
        self.write({'state': '99'})
        employee = self.env['hr.employee'].search(['|', ('department_id', '=', self.name.id), ('department_id', 'in', [cr.id for cr in self.name.child_ids])])
        for name in employee:
            subject = u'【通知】%s%s部门绩效业务目标已制定' % (self.name.complete_name,self.quarter)
            content = u'%s%s部门绩效业务目标已制定，请查看' % (self.name.complete_name,self.quarter)
            self.send_mail(name, subject=subject, content=content)
            time.sleep(0.01)


class dtdream_pbc_target(models.Model):
    _name = "dtdream.pbc.target"
    _order = "target,level"

    def _compute_department_target(self):
        for rec in self:
            rec.depart_target = rec.target.name.complete_name
            level = 1
            if rec.depart_target:
                level = len(rec.depart_target.split('/'))
            rec.write({"level": level})

    target = fields.Many2one('dtdream.hr.pbc', string='部门绩效目标')
    depart_target = fields.Char(compute=_compute_department_target)
    level = fields.Integer(default=lambda self: 1, string="部门类型")
    num = fields.Text(string='业务目标', required=True)
    works = fields.Text(string='关键指标,关键动作,行为', required=True)


class dtdream_pbc_hr_config(models.Model):
    _name = "dtdream.pbc.hr.config"

    @api.model
    def create(self, vals):
        config = self.search([])
        if config:
            raise ValidationError("已经存在一条配置!")
        return super(dtdream_pbc_hr_config, self).create(vals)

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(dtdream_pbc_hr_config, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=False)
        doc = etree.XML(res['arch'])
        config = self.search([])
        if res['type'] == "form" and config:
            doc.xpath("//form")[0].set("create", "false")
        res['arch'] = etree.tostring(doc)
        return res

    interface = fields.One2many('dtdream.pbc.hr.interface', 'inter', string='业务接口部门设置')
    name = fields.Char(default=lambda self: '业务接口人配置')


class dtdream_pbc_hr_interface(models.Model):
    _name = "dtdream.pbc.hr.interface"

    name = fields.Many2one('hr.employee', string='HR接口人')
    department = fields.Many2one('hr.department', string='接口业务部门')
    inter = fields.Many2one('dtdream.pbc.hr.config')


class dtdream_hr_pbc_start(models.TransientModel):
    _name = "dtdream.hr.pbc.start"

    @api.one
    def start_hr_pbc(self):
        context = dict(self._context or {})
        pbc = context.get('active_ids', []) or []
        performance = self.env['dtdream.hr.performance'].browse(pbc)
        for per in performance:
            if per.state == '0' and per.onwork == 'Inaugural_state_01':
                per.signal_workflow('btn_start')
        return {'type': 'ir.actions.act_window_close'}

    @api.one
    def start_hr_pbc_evaluate(self):
        context = dict(self._context or {})
        pbc = context.get('active_ids', []) or []
        performance = self.env['dtdream.hr.performance'].browse(pbc)
        for per in performance:
            if per.state == '3':
                per.signal_workflow('btn_start2')
        return {'type': 'ir.actions.act_window_close'}

    @api.one
    def start_hr_pbc_manage_submit(self):
        context = dict(self._context or {})
        pbc = context.get('active_ids', []) or []
        performance = self.env['dtdream.hr.performance'].browse(pbc)
        for rec in performance:
            if rec.state in ('1', '4', '5'):
                rec.signal_workflow('btn_submit')
            elif rec.state == '2':
                rec.signal_workflow('btn_agree')
        return {'type': 'ir.actions.act_window_close'}

    @api.one
    def start_hr_pbc_send_mail(self):
        context = dict(self._context or {})
        pbc = context.get('active_ids', []) or []
        performance = self.env['dtdream.hr.performance'].browse(pbc)
        for rec in performance:
            if rec.state == '1':
                subject = u'【通知】请尽快填写您的个人季度绩效目标'
                content = u'您的个人季度绩效目标仍未完成填写,请尽快提交。'
                rec.send_mail(rec.name, subject=subject, content=content)
            elif rec.state == '2':
                subject = u'【通知】请尽快审阅%s的个人季度绩效目标' % rec.name.name
                content = u'您对%s的个人季度绩效目标仍未完成确认,请尽快审阅。'% rec.name.name
                rec.send_mail(rec.officer, subject=subject, content=content)
            elif rec.state == '4':
                subject = u'【通知】请尽快填写您的个人季度关键事项达成情况与主要工作成果'
                content = u'您的个人季度关键事项达成情况与主要工作成果仍未完成填写,请尽快提交。'
                rec.send_mail(rec.name, subject=subject, content=content)
            elif rec.state == '5':
                subject = u'【通知】请尽快评价%s的个人工作总结' % rec.name.name
                content = u'您对%s的个人工作总结仍未完成评价,请尽快提交。'% rec.name.name
                rec.send_mail(rec.officer, subject=subject, content=content)
            time.sleep(0.01)
        return {'type': 'ir.actions.act_window_close'}

    @api.one
    def start_hr_pbc_submit(self):
        context = dict(self._context or {})
        pbc = context.get('active_ids', []) or []
        performance = self.env['dtdream.hr.pbc'].browse(pbc)
        for rec in performance:
            if rec.state == '0':
                if rec.env.ref("dtdream_hr_performance.group_hr_manage_performance") in rec.env.user.groups_id:
                    rec.signal_workflow('btn_submit')
                else:
                    department = []
                    inter = rec.env['dtdream.pbc.hr.interface'].search([('name.user_id', '=', rec.env.user.id)])
                    for crr in inter:
                        department.append(crr.department.id)
                        for depart in crr.department.child_ids:
                            department.append(depart.id)
                    if rec.name.id in department:
                        rec.signal_workflow('btn_submit')
        return {'type': 'ir.actions.act_window_close'}


