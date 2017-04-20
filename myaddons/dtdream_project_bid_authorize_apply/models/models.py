# -*- coding: utf-8 -*-

from openerp import models, fields, api
from datetime import datetime
from lxml import etree
from openerp .exceptions import ValidationError
from openerp.osv import expression
from openerp.exceptions import AccessError


#项目招投标授权申请
class dtdream_project_bid_authorize_apply(models.Model):
    _name = "dtdream.project.bid.authorize.apply"
    _description = u"项目招投标申请授权"
    _inherit = ['mail.thread']

    @api.multi
    def read(self, fields=None, load='_classic_read'):

        # domain = self.get_access_domain(domain=[])
        # access_records = [rec.id for rec in self.search(domain)]
        # for record in self:
        #     if record.id not in access_records:
        #         raise AccessError(u"您无权限访问该记录。")
        return super(dtdream_project_bid_authorize_apply, self).read(fields=fields, load=load)

    def get_access_domain(self, domain):
        leads_view = self.env['crm.lead'].search([])

        ex_domain = [('rep_pro_name.id', 'in', [rec.id for rec in leads_view])]


        # if self.user_has_groups('dtdream_sale.group_dtdream_sale_high_manager') or self.user_has_groups(
        #         'dtdream_sale.group_dtdream_weekly_report_manager') or self.user_has_groups(
        #         'dtdream_sale.group_dtdream_company_manager') or self.user_has_groups(
        #         'dtdream_sale.group_dtdream_market_manager'):
        #         ex_domain = []
        # ['&', ('rep_pro_name.id', 'in', [23, 20, 19, 18, 17, 16, 14, 13, 12, 11, 10, 9]), u'|', u'&',
        #  [u'state', u'=', u'5'], u'|', u'&', [u'fuwu_shenpi_state', u'=', False], [u'shenpiren05.user_id', u'=', 1],
        #  u'&', [u'fawu_shenpi_state', u'=', False], [u'shenpiren06.user_id', u'=', 1], u'&',
        #  [u'shenpiren.user_id.id', u'=', 1], [u'state', u'not in', [u'0', u'done']]]
        if domain:
            return expression.AND([ex_domain, domain])
        else :
            return expression.OR([ex_domain,['|',('history_shenpirens.user_id.id','=',self._uid),('shenpirens.user_id','=',self._uid)]])

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        if domain and( domain[0]== ['state','=','wait_shenpi'] or domain[0]==['state','=','shenpi_done']):
            domain = domain[1:]
            pass
        else:
            domain = self.get_access_domain(domain)
        return super(dtdream_project_bid_authorize_apply, self).search_read(domain=domain, fields=fields, offset=offset,limit=limit, order=order)




    def get_base_url(self, cr, uid):
        base_url = self.pool.get('ir.config_parameter').get_param(cr, uid, 'web.base.url')
        return base_url

    def get_mail_server_name(self):
        return self.env['ir.mail_server'].search([], limit=1).smtp_user

    def dtdream_send_mail(self, subject, content, email_to,appellation,email_cc=None):
        base_url = self.get_base_url()
        link = '/web#id=%s&view_type=form&model=dtdream.project.bid.authorize.apply' % self.id
        url = base_url+link
        email_to = email_to
        subject = subject
        content = content
        self.env['mail.mail'].create({
                'body_html': u'''<p>%s</p>
                                <p>%s</p>
                                <a href="%s">点击进入查看</a></p>
                                <p>dodo</p>
                                <p>万千业务，简单有do</p>
                                <p>%s</p>''' % (appellation, content, url, self.write_date[:10]),
                'subject': '%s' % subject,
                'email_from': self.get_mail_server_name(),
                'email_to': '%s' % email_to,
                'email_cc': '%s' % email_cc,
                'auto_delete': False,
            }).send()


    # 新建时刷新豆腐块数字
    @api.model
    def create(self, vals):
        # if self.env['dtdream.project.bid.authorize.apply'].search([('rep_pro_name.id','=',vals.get("rep_pro_name"))]):
        #     raise  ValidationError("本项目已经创建授权!请重新选择项目名称.")
        if vals.get('rep_pro_name',False):
            vals['project_number'] = self.env['crm.lead'].search([('id', '=', vals.get('rep_pro_name',False))])[0].project_number
            vals['has_import_button'] = True
            result = super(dtdream_project_bid_authorize_apply, self).create(vals)
            old_business_count = len(self.env['dtdream.project.bid.authorize.apply'].search([('rep_pro_name.id', '=', result.rep_pro_name.id)]))
            self.env['crm.lead'].search([('id', '=', result.rep_pro_name.id)]).sudo().write(
                {'authorization_count': old_business_count, 'has_draft_authorization': True})
            return result
        else:
            res = super(dtdream_project_bid_authorize_apply, self).create(vals)
            self.env['crm.lead'].search([('id', '=', res.rep_pro_name.id)]).sudo().write(
                {'authorization_count': len(self.env['dtdream.project.bid.authorize.apply'].search([('rep_pro_name.id', '=', res.rep_pro_name.id)])), 'has_draft_authorization': True})
            return res



    @api.multi
    def unlink(self):
        for rec in self:
            if (rec.state == "0" and rec.create_uid.id == rec._uid) or rec.env.user.login == "admin" or rec.env.user.has_group( "dtdream_sale.group_dtdream_sale_high_manager"):
                old_business_count = len(self.env['dtdream.project.bid.authorize.apply'].search([('rep_pro_name.id', '=', rec.rep_pro_name.id)]))
                rec.env['crm.lead'].search([('id', '=', rec.rep_pro_name.id)]).sudo().write({'authorization_count': old_business_count - 1})
                rec.env['crm.lead'].search([('id', '=', rec.rep_pro_name.id)]).sudo().write(
                    {'has_draft_authorization': False})
                super(dtdream_project_bid_authorize_apply, rec).unlink()
            else:
                raise ValidationError("未提交申请的项目授权创建者才可以删除。")



    @api.multi
    def wkf_create(self):
        if not self._shenpi_text:
            self.write({'state':'0','shenpiren':None,'shenpiren01':None,'shenpiren02':None,'shenpiren03':None,'shenpiren04':None,'shenpiren05':None,'shenpiren06':None,'fuwu_shenpi_state':False,'fawu_shenpi_state':False,'system_shenpi_state':False,'office_shenpi_state':False})
            self.rep_pro_name.sudo().write({'has_draft_authorization': True})
        else :
            self.write({'state': '0', 'shenpiren': None, 'shenpiren01': None, 'shenpiren02': None, 'shenpiren03': None,'shenpiren04': None, 'shenpiren05': None,'shenpiren06':None,'fuwu_shenpi_state':False,'fawu_shenpi_state':False,'system_shenpi_state':False,'office_shenpi_state':False})
            self.rep_pro_name.sudo().write({'has_draft_authorization': True})
        self.shenpirens = None
        pass

    @api.multi
    def wkf_apply(self):
        if self.office_id.name == u'总部':
            if self.env["dtdream.system.line"].search([('system_id.id', '=', self.system_department_id.id)]):
                self.write({'state': '1', "shenpiren": self.env["dtdream.system.line"].search([('system_id.id', '=', self.system_department_id.id)])[0].system_director.id})
                self.dtdream_send_mail(u"{0}于{1}提交了项目授权申请,请您进行审核!".format(self.env['hr.employee'].search([('login', '=', self.create_uid.login)]).name,self.create_date[:10]),
                                       u"%s提交了项目授权申请,等待您审核" % self.env['hr.employee'].search([('login', '=', self.create_uid.login)]).name,
                                       email_to=self.shenpiren.work_email,
                                       appellation=u'{0},您好：'.format(self.shenpiren.name))
                self.shenpirens = [(4, self.shenpiren.id)]
                self.dtdream_send_mail(u"{0}于{1}发出请求,请您对项目授权进行审核!".format(
                    self.env['hr.employee'].search([('login', '=', self.shenpirens.login)]).name,
                    self.create_date[:10]),
                    u"%s发出请求,请您对项目授权进行审核" % self.env['hr.employee'].search(
                        [('login', '=', self.shenpirens.login)]).name,
                    email_to=self.shenpirens.work_email,
                    appellation=u'{0},您好：'.format(self.shenpirens.name))
            else :
                raise ValidationError("请先配置系统部部长！")
        else:
            if self.env["dtdream.office.line"].search([('office_id.id','=',self.office_id.id)]) and self.env["dtdream.system.line"].search([('system_id.id', '=', self.system_department_id.id)]) :
                self.write({'state': '1',
                            "shenpiren":self.env["dtdream.office.line"].search([('office_id.id','=',self.office_id.id)])[0].office_director.id,
                            "shenpiren01":self.env["dtdream.office.line"].search([('office_id.id','=',self.office_id.id)])[0].office_director.id,
                            "shenpiren02":self.env["dtdream.system.line"].search([('system_id.id', '=', self.system_department_id.id)]).system_director.id})
                self.dtdream_send_mail(u"{0}于{1}提交了项目授权申请,请您进行审核!".format(self.env['hr.employee'].search([('login', '=', self.create_uid.login)]).name,self.create_date[:10]),
                                       u"%s提交了项目授权申请,等待您审核" % self.env['hr.employee'].search([('login', '=', self.create_uid.login)]).name,
                                       email_to=self.shenpiren.work_email,
                                       appellation=u'{0},您好：'.format(self.shenpiren.name))
                self.shenpirens = [(6, 0, [self.shenpiren01.id, self.shenpiren02.id])]
                self.dtdream_send_mail(u"{0}于{1}发出请求,请您对项目授权进行审核!".format(
                    self.env['hr.employee'].search([('login', '=', self.shenpiren01.login)]).name,
                    self.create_date[:10]),
                    u"%s发出请求,请您对项目授权进行审核" % self.env['hr.employee'].search(
                        [('login', '=', self.shenpiren01.login)]).name,
                    email_to=self.shenpiren01.work_email,
                    appellation=u'{0},您好：'.format(self.shenpiren01.name))
                self.dtdream_send_mail(u"{0}于{1}发出请求,请您对项目授权进行审核!".format(
                    self.env['hr.employee'].search([('login', '=', self.shenpiren02.login)]).name,
                    self.create_date[:10]),
                    u"%s发出请求,请您对项目授权进行审核" % self.env['hr.employee'].search(
                        [('login', '=', self.shenpiren02.login)]).name,
                    email_to=self.shenpiren02.work_email,
                    appellation=u'{0},您好：'.format(self.shenpiren02.name))
            else:
                raise ValidationError("请先配置办事处主任/系统部部长!")

        pass
    @api.multi
    def wkf_examine(self):
        if self.office_id.name == u'总部':
            self.write({"shenpiren01": self.env["dtdream.system.line"].search(
                [('system_id.id', '=', self.system_department_id.id)])[0].system_director.id, 'state': '2',
                        'shenpiren': self.env["dtdream.project.authorize.config"].search([])[0].project_authorize_accessor.id})
            self.dtdream_send_mail(u"{0}于{1}发出请求,请您对项目授权进行审核!".format(
                self.env['hr.employee'].search([('login', '=', self.shenpiren01.login)]).name,
                self.create_date[:10]),
                u"%s发出请求,请您对项目授权进行审核" % self.env['hr.employee'].search(
                    [('login', '=', self.shenpirens.login)]).name,
                email_to=self.shenpirens.work_email,
                appellation=u'{0},您好：'.format(self.shenpirens.name))
            self.system_shenpi_state = True
            self.office_shenpi_state = True
            self.shenpirens = [(6, 0, [self.shenpiren.id])]
        else:

            if self._uid == self.shenpiren01.user_id.id:
                self.office_shenpi_state = True
                self.shenpirens = [(6,0,[self.shenpiren02.id])]
            if self._uid == self.shenpiren02.user_id.id:
                self.system_shenpi_state = True
                self.shenpirens = [(6, 0, [self.shenpiren01.id])]
            if self.system_shenpi_state and self.office_shenpi_state:
                self.write(
                    {'state': '2', 'shenpiren': self.env["dtdream.project.authorize.config"].search([])[0].project_authorize_accessor.id})
                self.shenpirens = [(6, 0, [self.shenpiren.id])]
                pass
                self.dtdream_send_mail(u"{0}于{1}发出请求,请您对项目授权进行审核!".format(
                    self.env['hr.employee'].search([('login', '=', self.shenpirens.login)]).name,
                    self.create_date[:10]),
                                       u"%s发出请求,请您对项目授权进行审核" % self.env['hr.employee'].search(
                                           [('login', '=', self.shenpirens.login)]).name,
                                       email_to=self.shenpirens.work_email,
                                       appellation=u'{0},您好：'.format(self.shenpirens.name))

        pass
    @api.multi
    def wkf_standar(self):

        if self.is_normal:
            if self.env["dtdream.project.authorize.config"].search([])[0].approver:
                shenpidic = {"shenpiren": self.shenpiren.id if self.shenpiren else None, "time": datetime.now(),
                             "shenpi_text_id": self.id, 'state': "规范性审核",'res':"公司标准模板"}
                self.env["dtdream.shenpi.text"].create(shenpidic)
                self.write({'shenpiren02':self.env["dtdream.project.authorize.config"].search([])[0].project_authorize_accessor.id,'state': '3','shenpiren':self.env["dtdream.project.authorize.config"].search([])[0].approver.id})
                self.shenpirens = [(6,0,[self.shenpiren.id])]
                pass
                self.dtdream_send_mail(u"{0}于{1}发出请求,请您对项目授权进行审核!".format(
                    self.env['hr.employee'].search([('login', '=', self.shenpiren02.login)]).name,
                    self.create_date[:10]),
                    u"%s发出请求,请您对项目授权进行审核" % self.env['hr.employee'].search(
                        [('login', '=', self.shenpiren02.login)]).name,
                    email_to=self.shenpiren.work_email,
                    appellation=u'{0},您好：'.format(self.shenpiren.name))
            else :
                raise ValidationError("请先配置营销管理部!")
        else :
            if self.env["dtdream.project.authorize.config"].search([])[0].fuwu_fawu_config:
            # if self.env["dtdream.project.authorize.config"].search([])[0].project_authorize_service and self.env["dtdream.project.authorize.config"].search([])[0].fawu.id:
                shenpidic = {"shenpiren": self.shenpiren.id if self.shenpiren else None, "time": datetime.now(),
                             "shenpi_text_id": self.id, 'state': "规范性审核", 'res': "非公司标准模板"}

                self.env["dtdream.shenpi.text"].create(shenpidic)
                self.write({
                            'state': '6',
                            'shenpiren':self.env["dtdream.project.authorize.config"].search([])[0].fuwu_fawu_config.id,
                            })
                self.shenpirens = [(6,0,[self.shenpiren.id])]
                pass
                self.dtdream_send_mail(u"{0}于{1}提交了项目授权,请您对项目授权进行审核!".format(
                    self.env['hr.employee'].search([('login', '=', self.shenpiren.login)]).name,
                    self.create_date[:10]),
                    u"%s发出请求,请您对项目授权进行审核" % self.env['hr.employee'].search(
                        [('login', '=', self.shenpiren.login)]).name,
                    email_to=self.shenpiren.work_email,
                    appellation=u'{0},您好：'.format(self.shenpiren.name))

            else :
                raise ValidationError("请先配置服务部/法务审批人!")
        return

    #
    # self.write({'shenpiren02': self.env["dtdream.project.authorize.config"].search([])[0].project_authorize_accessor.id,
    #             'state': '6',
    #             'shenpiren': self.env["dtdream.project.authorize.config"].search([])[0].project_authorize_service.id,
    #             'shenpiren06': self.env["dtdream.project.authorize.config"].search([])[0].fawu.id,
    #             'shenpiren05': self.env["dtdream.project.authorize.config"].search([])[0].project_authorize_service.id,
    #             })
    # self.shenpirens = [(6, 0, [self.shenpiren06.id, self.shenpiren05.id])]
    # pass
    # self.dtdream_send_mail(u"{0}于{1}提交了项目授权,请您对项目授权进行审核!".format(
    #     self.env['hr.employee'].search([('login', '=', self.shenpiren05.login)]).name,
    #     self.create_date[:10]),
    #     u"%s发出请求,请您对项目授权进行审核" % self.env['hr.employee'].search(
    #         [('login', '=', self.shenpiren02.login)]).name,
    #     email_to=self.shenpiren.work_email,
    #     appellation=u'{0},您好：'.format(self.shenpiren.name))
    # self.dtdream_send_mail(u"{0}于{1}提交了项目授权,请您对项目授权进行审核!".format(
    #     self.env['hr.employee'].search([('login', '=', self.shenpiren06.login)]).name,
    #     self.create_date[:10]),
    #     u"%s发出请求,请您对项目授权进行审核" % self.env['hr.employee'].search(
    #         [('login', '=', self.shenpiren02.login)]).name,
    #     email_to=self.shenpiren.work_email,
    #     appellation=u'{0},您好：'.format(self.shenpiren.name))
    # 售后服务函非标
    @api.multi
    def wkf_not_standar_config(self):
        self.write({'state':'5'})
        self.shenpirens = [(6,0,[self.shenpiren05.id,self.shenpiren06.id])]
        self.dtdream_send_mail(u"{0}于{1}提交了项目授权,请您对项目授权进行审核!".format(
            self.env['hr.employee'].search([('login', '=', self.shenpiren05.login)]).name,
            self.create_date[:10]),
            u"%s发出请求,请您对项目授权进行审核" % self.env['hr.employee'].search(
                [('login', '=', self.shenpiren05.login)]).name,
            email_to=self.shenpiren05.work_email,
            appellation=u'{0},您好：'.format(self.shenpiren05.name))
        self.dtdream_send_mail(u"{0}于{1}提交了项目授权,请您对项目授权进行审核!".format(
            self.env['hr.employee'].search([('login', '=', self.shenpiren06.login)]).name,
            self.create_date[:10]),
            u"%s发出请求,请您对项目授权进行审核" % self.env['hr.employee'].search(
                [('login', '=', self.shenpiren06.login)]).name,
            email_to=self.shenpiren06.work_email,
            appellation=u'{0},您好：'.format(self.shenpiren06.name))

    @api.multi
    def wkf_not_standar(self):
        if self._uid == self.shenpiren05.user_id.id:
            self.fuwu_shenpi_state = True
            self.shenpirens = [(6,0,[self.shenpiren06.id])]
        if self._uid == self.shenpiren06.user_id.id:
            self.fawu_shenpi_state = True
            self.shenpirens = [(6, 0, [self.shenpiren05.id])]
        if self.fawu_shenpi_state and self.fuwu_shenpi_state:
            self.write({'state':'3','shenpiren':self.env["dtdream.project.authorize.config"].search([])[0].approver.id})
            self.shenpirens = [(6,0,[self.shenpiren.id])]
            pass
            self.dtdream_send_mail(u"{0}于{1}提交了项目授权,请您对项目授权进行审核!".format(
                self.env['hr.employee'].search([('login', '=', self.shenpiren05.login)]).name,
                self.create_date[:10]),
                u"%s发出请求,请您对项目授权进行审核" % self.env['hr.employee'].search(
                    [('login', '=', self.shenpiren05.login)]).name,
                email_to=self.shenpiren.work_email,
                appellation=u'{0},您好：'.format(self.shenpiren.name))

    @api.multi
    def wkf_approve(self):
        self.write({'shenpiren03': self.env["dtdream.project.authorize.config"].search([])[0].approver.id, 'state': '4','shenpiren': self.env["dtdream.project.authorize.config"].search([])[0].project_authorize_accessor.id})
        self.shenpirens = [(6,0,[self.shenpiren.id])]
        pass
        self.dtdream_send_mail(u"{0}于{1}提交了项目授权,请您对项目授权进行审核!".format(
            self.env['hr.employee'].search([('login', '=', self.shenpiren03.login)]).name,
            self.create_date[:10]),
            u"%s发出请求,请您对项目授权进行审核" % self.env['hr.employee'].search(
                [('login', '=', self.shenpiren03.login)]).name,
            email_to=self.shenpiren.work_email,
            appellation=u'{0},您好：'.format(self.shenpiren.name))

    @api.multi
    def wkf_done(self):
        self.write({'shenpiren':None,'shenpiren04':self.env["dtdream.project.authorize.config"].search([])[0].project_authorize_accessor.id,'state': 'done'})
        self.shenpirens = None
        pass
    #判断是否为目前审批人
    @api.one
    def _compute_is_current(self):
        if self.state == '0':
            self.is_current = True if self.env.context.get("uid") == self.create_uid else False
        elif self.state == '1':
            if self.office_id.name == u'总部':
                if self.env["dtdream.system.line"].search([('system_id.id', '=', self.system_department_id.id)]):
                    self.is_current = True if self.env.context.get("uid") == self.env["dtdream.system.line"].search([('system_id.id','=',self.system_department_id.id)]).system_director.id else False
                else :
                    raise ValidationError("请先配置系统部主任!")
            else:
                if self.env["dtdream.office.line"].search([('office_id.id', '=', self.office_id.id)]):
                    
                    self.is_current = True if self.env.context.get("uid") == self.env["dtdream.office.line"].search([('office_id.id','=',self.office_id.id)])[0].office_director.id else False
                else :
                    raise ValidationError("请先配置办事处主任!")
        elif self.state == '2':
            if self.env["dtdream.project.authorize.config"].search([]):
                self.is_current = True if self.env.context.get("uid") == self.env["dtdream.project.authorize.config"].search([])[0].project_authorize_accessor.id else False
            else:
                raise ValidationError("请先配置项目授权接口人!")
        elif self.state == '5':
            if self.env["dtdream.project.authorize.config"].search([])[0].project_authorize_service and self.env["dtdream.project.authorize.config"].search([])[0].fawu:
                if self.fawu_shenpi_state == False:
                    self.is_current = True if self.env.context.get("uid") == \
                                              self.env["dtdream.project.authorize.config"].search(
                                                  [])[0].fawu.id else False
                if self.fuwu_shenpi_state == False:
                    self.is_current = True if self.env.context.get("uid") == self.env["dtdream.project.authorize.config"].search(
                        [])[0].project_authorize_service.id else False
            else:
                raise ValidationError("请先配置服务部!")
        elif self.state == '3':
            if self.env["dtdream.project.authorize.config"].search([])[0].approver:
                
                self.is_current = True if self.env.context.get("uid") == self.env["dtdream.project.authorize.config"].search([])[0].approver.id else False
            else:
                raise ValidationError("请先配置营销管理部!")
        elif self.state == '4':
            if self.env["dtdream.project.authorize.config"].search([]):
                
                self.is_current = True if self.env.context.get("uid") == self.env["dtdream.project.authorize.config"].search([])[0].project_authorize_accessor.id else False
            else:
                raise ValidationError("请先配置项目授权接口人!")
        return

    @api.one
    def _compute_present_shenpiren(self):
        if self.state == '0':
            self.present_shenpiren = True if self.env.context.get("uid") == self.create_uid.id else False
        elif self.state == '5':
            if not self.fawu_shenpi_state and self.env.context.get("uid") in [self.shenpiren06.user_id.id if self.shenpiren06 else -1]:
                self.present_shenpiren = True
            elif not self.fuwu_shenpi_state and self.env.context.get("uid") in [self.shenpiren05.user_id.id if self.shenpiren05 else -1]:
                self.present_shenpiren = True
            else :
                self.present_shenpiren = False

        else :
            self.present_shenpiren = True if self._uid in [ p.user_id.id for p in self.shenpirens] else False




    @api.onchange("rep_pro_name")
    def _onchange_rep_pro_name(self):
        if self.env.context.get('active_id'):
            self.rep_pro_name = self.env['crm.lead'].search([('id','=', self.env.context.get('active_id'))])[0].id
        report = self.env['dtdream.sale.business.report'].search([('rep_pro_name.id', '=', self.rep_pro_name.id)],order='create_date desc',limit=1)
        if report:
            self.business_advanced_report = report
            self.project_number = report.project_number
            # self.rep_pro_name = report.rep_pro_name
            self.office_id = report.office_id
            self.system_department_id = report.system_department_id
            self.sale_apply_id = report.rep_pro_name.sale_apply_id

    @api.one
    @api.depends('rep_pro_name')
    def _compute_report(self):
        self.business_advanced_report = self.env['dtdream.sale.business.report'].search([('rep_pro_name.id', '=', self.sudo().rep_pro_name.id)],order='create_date desc',limit=1)
        self.office_id = self.sudo().rep_pro_name.office_id
        self.project_number = self.sudo().rep_pro_name.project_number
        self.system_department_id = self.sudo().rep_pro_name.system_department_id
        self.sale_apply_id = self.sudo().rep_pro_name.sale_apply_id

    @api.constrains("authorization")
    def check_length(self):
        if not self.authorization:
            raise ValidationError("请至少添加一条授权渠道。")
    def employee_normal_name(self,employee=None):
        if employee:
            return "{0}.{1} {2}".format(employee.name,employee.full_name,employee.job_number)
        else :
            return " "
    @api.one
    def _compute_shenpiren_name(self):
        if self.state != '5':
            self.shenpiren_name = self.employee_normal_name(self.shenpiren) if self.shenpiren else ''
        else :
            self.shenpiren_name = "{0[0]}.{0[1]} {0[2]} {1[0]}.{1[1]} {1[2]}".format([self.shenpiren05.name,self.shenpiren05.full_name,self.shenpiren05.job_number] if self.fuwu_shenpi_state==False else ['','',''] ,[self.shenpiren06.name,self.shenpiren06.full_name,self.shenpiren06.job_number] if self.fawu_shenpi_state == False  else ['','',''])
        return
    @api.one
    def _compute_fuwufawu_shenpi(self):
        if self.state == '5':
            if self.env.context.get('uid') in [self.shenpiren05.user_id.id if self.shenpiren05 else -1] and not self.fuwu_shenpi_state:
                self.is_fuwufawu_shenpi = True
            elif self.env.context.get('uid') in [self.shenpiren06.user_id.id if self.shenpiren06 else -1] and not self.fawu_shenpi_state:
                self.is_fuwufawu_shenpi = True
            else:
                self.is_fuwufawu_shenpi = False
        else :
            self.is_fuwufawu_shenpi = False

    @api.depends('rep_pro_name')
    def _compute_rep_pro_name_str(self):
        for rec in self:
            rec.rep_pro_name_str = rec.sudo().rep_pro_name.name

    system_shenpi_state = fields.Boolean(string="系统部审批状态",default=False)
    office_shenpi_state = fields.Boolean(string="办事处审批状态", default=False)
    shenpirens = fields.Many2many("hr.employee", 'auth_shenpirens',string="当前审批")
    history_shenpirens = fields.Many2many("hr.employee", 'auth_history_shenpirens',string="历史审批人")
    present_shenpiren = fields.Boolean(string="判断审批人",compute=_compute_present_shenpiren)
    shenpiren = fields.Many2one("hr.employee",string="当前审批人")
    shenpiren_name = fields.Char(string="当前审批人名字",compute=_compute_shenpiren_name)
    name = fields.Char(default="项目授权申请")
    is_normal = fields.Boolean(string='是否为标准模块',default=True)
    shenpiren01 = fields.Many2one("hr.employee",string="第1审批人")#办事处审批人
    shenpiren02 = fields.Many2one("hr.employee", string="第2审批人")#系统部审批人
    shenpiren03 = fields.Many2one("hr.employee", string="第3审批人")
    shenpiren04 = fields.Many2one("hr.employee", string="第4审批人")
    shenpiren05 = fields.Many2one("hr.employee",string="第5审批人")#服务部审批人
    shenpiren06 = fields.Many2one("hr.employee",string="第6审批人")#法务部审批人
    project_number = fields.Char(string = '项目编号',compute=_compute_report)
    rep_pro_name = fields.Many2one('crm.lead', string="项目名称", required=True,track_visibility='onchange')
    rep_pro_name_str = fields.Char(compute=_compute_rep_pro_name_str,string="项目名称")
    office_id = fields.Many2one("dtdream.office", string="办事处", compute=_compute_report)
    system_department_id = fields.Many2one("dtdream.industry", string="系统部",compute=_compute_report )
    sale_apply_id = fields.Many2one("hr.employee", string="营销责任人", compute=_compute_report)
    business_advanced_report = fields.Many2one("dtdream.sale.business.report", string='商务提前报备',compute=_compute_report)
    bidding_rep_pro_name = fields.Char(required=True,string = '投标项目名称',track_visibility='onchange')
    bidding_number = fields.Char(required=True,string = '招标编号',track_visibility='onchange')
    bidding_company = fields.Char(required=True,string = '招标单位',track_visibility='onchange')
    is_current = fields.Integer(required=True,string="是否当前审批人",default=0)
    shouhou_export_button = fields.Char(string="导出项目售后服务承诺函", default="导出项目售后服务承诺函")
    shouquan_export_button = fields.Char(string="导出项目授权函", default="导出项目授权函")
    fuwu_shenpi_state=fields.Boolean(default=False,string="是否服务部审批完成")
    fawu_shenpi_state=fields.Boolean(default=False,string="是否法务部审批完成")
    shenpi_text = fields.One2many("dtdream.shenpi.text","shenpi_text_id",string="审批历史")
    _shenpi_text = fields.Text(string="审批缓存",default=None)
    state = fields.Selection(
        [('-2','创建'),
         ('0', '草稿'),
         ('1', '办事处与系统部审批'),
         ('2', '规范性审核'),
         ('6', '配置服务与法务审批人'),
         ('5', '服务与法务审批'),
         ('3', '营销管理部审批'),
         ('-1', '驳回'),
         ('4', '盖章完成'),

         ('done','完成项目授权')]
        , string="状态", default="0", track_visibility='onchange')
    yearnum = fields.Integer("承诺服务年限",required=True,track_visibility='onchange')
    is_fuwufawu_shenpi = fields.Boolean('服务法务审批',compute=_compute_fuwufawu_shenpi)
    bidding_time = fields.Date("招投标时间", required=True, default=lambda self: datetime.now(), track_visibility='onchange')
    authorization = fields.One2many("dtdream.authorization", "authorization_id", string='授权渠道',track_visibility='onchange')
    attachment_ids = fields.One2many('dtdream.authorization.attachment', 'contract_id', string='文件上传', required=1)

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        cr = self.env["dtdream.project.bid.authorize.apply"].search([("rep_pro_name", "=", self.env.context.get('active_id'))])
        res = super(dtdream_project_bid_authorize_apply, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=False)
        if res['type'] == "form":
            if len(cr):
                doc = etree.XML(res['arch'])
                doc.xpath("//form")[0].set("create", "false")
                res['arch'] = etree.tostring(doc)
        # 隐藏除我的申请外三个菜单下的新建按钮
        active_id = self._context.get('active_id', None)
        if res['type'] == "form":
            doc = etree.XML(res['arch'])
            if len(cr) or not active_id:
                doc.xpath("//form")[0].set("create", "false")
            res['arch'] = etree.tostring(doc)
        if res['type'] == "tree":
            if not active_id:
                doc = etree.XML(res['arch'])
                doc.xpath("//tree")[0].set("create", "false")
                res['arch'] = etree.tostring(doc)
        if self._context.get('params',None):
            if self.env['ir.actions.actions'].search([('id','=',self._context.get('params',None).get('action',None))])[0].name == u"我的申请":
                if res['type'] == "tree":
                    doc = etree.XML(res['arch'])
                    if len(cr) or not active_id:
                        doc.xpath("//tree")[0].set("create", "true")
                    res['arch'] = etree.tostring(doc)
                if res['type'] == "form":
                    doc = etree.XML(res['arch'])
                    if len(cr) or not active_id:
                        doc.xpath("//form")[0].set("create", "true")
                    res['arch'] = etree.tostring(doc)
        return res