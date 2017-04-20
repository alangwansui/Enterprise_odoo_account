# -*- coding: utf-8 -*-

from openerp import models, fields, api
from datetime import datetime

from openerp.exceptions import ValidationError


class dtdream_reserve_fund(models.Model):
    _name = 'dtdream.reserve.fund'
    _description = u'备用金管理'
    _inherit =['mail.thread']

    name = fields.Char(string='备用金单号')
    type = fields.Selection([(u'行政类', '行政类'),
                             (u'专项类', '专项类'),
                             (u'常用备用金', '常用备用金'),
                             (u'公有云项目类', '公有云项目类'),
                             (u'其他', '其他')], string='备用金类型')

    state = fields.Selection([(u'草稿', '草稿'),
                              (u'主管审批', '主管审批'),
                              (u'第一权签人审批', '第一权签人审批'),
                              (u'第二权签人审批', '第二权签人审批'),
                              (u'总裁审批', '总裁审批'),
                              (u'接口会计审批', '接口会计审批'),
                              (u'出纳', '出纳'),
                              (u'已付款', '已付款')], string='状态', default=u'草稿')

    applicant = fields.Many2one('hr.employee', string='申请人',
                                default=lambda self: self.env['hr.employee'].search([('user_id', '=', self.env.user.id)]))

    current_handler = fields.Many2many('hr.employee', string='当前处理人')
    his_handler = fields.Many2many('hr.employee', 'dtdream_reserve_approved', 'employee_id', 'reserve_id',
                                   string='历史审批人')
    his_state = fields.Char(string='经过的状态', default='')

    def compute_if_applicant(self):
        if self.env.user.id == self.applicant.user_id.id or self.env.user.id == self.create_uid.id:
            self.is_applicant = True
        else:
            self.is_applicant = False
    is_applicant = fields.Boolean(string='是否申请人', compute=compute_if_applicant)

    def compute_if_handler(self):
        self.is_handlers = False
        if self.env['hr.employee'].search([('user_id', '=', self.env.user.id)]) in self.current_handler:
            self.is_handlers = True

    is_handlers = fields.Boolean(string='是否处理人', compute=compute_if_handler)

    @api.constrains('applicant')
    @api.onchange('applicant')
    def get_applicant_info(self):
        self.department_id = self.applicant.department_id
        self.dep_code = self.applicant.department_id.code
        if self.pay_to_who == u'付款给员工':
            self.payee_name = self.applicant.full_name
            self.bank_address = self.applicant.bankaddr
            self.bank_card_number = self.applicant.bankcardno

    @api.onchange('applicant')
    def compute_some_domain(self):
        return {
            'domain': {
                'contract_name': [('applicant', '=', self.applicant.id), ('state', '=', '9')],
                'special_approval_id': [('applicant', '=', self.applicant.id), ('state', '=', 'state_05')]
            }
        }

    @api.constrains('pay_to_who')
    @api.onchange('pay_to_who')
    def check_account_info(self):
        if self.pay_to_who == u'付款给员工':
            self.payee_name = self.applicant.full_name
            self.bank_address = self.applicant.bankaddr
            self.bank_card_number = self.applicant.bankcardno
        if self.reserve_fund_record:
            for rec in self.reserve_fund_record:
                rec.re_compute_total_amount()

    department_id = fields.Many2one('hr.department', string='部门')
    dep_code = fields.Char(string='部门编码')
    illustration = fields.Text(string='情况说明')
    pay_to_who = fields.Selection([(u'付款给员工', '付款给员工'),
                                   (u'付款给供应商', '付款给供应商')],
                                  string='支付类别',
                                  default=u'付款给员工')
    payee_name = fields.Char(string='收款人姓名')
    bank_address = fields.Char(string='开户行')
    bank_card_number = fields.Char(string='银行卡号')

    @api.depends('reserve_fund_record')
    def compute_total_amount(self):
        total = 0
        for record in self.reserve_fund_record:
            total += record.estimate_amount
        self.total_amount = total

    total_amount = fields.Float(string='总金额', compute=compute_total_amount, store=True)
    reserve_fund_record = fields.One2many('dtdream.reserve.fund.record', 'reserve_fund_id', string='费用明细')
    contract_name = fields.Many2one('dtdream.contract', string='合同名称')

    @api.depends('contract_name')
    def get_contract_info(self):
        if self.contract_name:
            self.contract_id = self.contract_name.contract_id
            self.contract_type = self.contract_name.contract_type.name
            self.contract_money = self.contract_name.money
            self.contract_state = dict(self.env['dtdream.contract']._columns['state'].selection)[self.contract_name.state]
    contract_id = fields.Char(string='合同编号', compute=get_contract_info, store=True)
    contract_type = fields.Char(string='合同类型', compute=get_contract_info, store=True)
    contract_money = fields.Float(string='合同金额', compute=get_contract_info, store=True)
    contract_state = fields.Char(string='审批状态', compute=get_contract_info, store=True)
    special_approval_id = fields.Many2one('dtdream.special.approval', string="专项编号")
    reject_state = fields.Char(string='驳回状态')
    done_time = fields.Datetime(string='付款日期')
    if_off = fields.Boolean(string='是否已核销', compute="check_if_off", store=True)
    amount_off = fields.Float(string='已核销金额(元)', track_visibility='onchange')
    amount_on = fields.Float(string='未核销金额(元)', compute="check_if_off", store=True)
    batch = fields.Char(string='批次')
    jiekou_approve_time = fields.Datetime(string="接口会计审批时间")
    is_out_time = fields.Boolean(string='是否超期', default=False)

    @api.constrains('amount_off')
    def check_if_off(self):
        if self.amount_off > self.total_amount:
            raise ValidationError("核销金额不能大于备用金金额！")
        elif self.amount_off < 0:
            raise ValidationError("核销金额不能小于0！")
        elif self.amount_off == self.total_amount:
            self.if_off = True
        else:
            self.if_off = False
        self.amount_on = self.total_amount - self.amount_off

    @api.depends('special_approval_id')
    def get_special_info(self):
        # 获取专项信息
        my_list = []
        if self.special_approval_id.fee_ids:
            for rec in self.special_approval_id.fee_ids:
                new_record = self.env['reserve.fund.zhuanx.record'].create({
                    'fee_type': dict(rec._columns['fee_type'].selection)[rec.fee_type],
                    'fee_amount': rec.money,
                    'fee_description': rec.remark
                })
                my_list.append(new_record.id)
            self.special_approval_fee_ids = [(6, 0, my_list)]

    special_approval_fee_ids = fields.Many2many('reserve.fund.zhuanx.record',
                                                string='专项费用明细',
                                                compute=get_special_info,
                                                store=True)

    def get_handlers(self, one_or_two):
        # 根据备用金类型获取权签人
        reserve_type = self.type
        signer_list = []
        if reserve_type == u'专项类':
            results = self.env['dtdream.reserve.fund.signer'].search(
                    ['&', '|',
                     ('type', '=', '所有'),
                     ('type', '=', reserve_type),
                     (one_or_two, '=', self.department_id.id)])
        else:
            results = self.env['dtdream.reserve.fund.signer'].search(
                    ['&', '|', '|',
                     ('type', '=', '所有'),
                     ('type', '=', reserve_type),
                     ('type', '=', '非专项类'),
                     (one_or_two, '=', self.department_id.id)])
        if not results:
            raise ValidationError("部门权签人没有配置，请联系管理员配置！")
        else:
            for result in results:
                if result.name.id != self.department_id.manager_id.id:
                    signer_list.append(result.name.id)
            return signer_list

    def check_reserve_fund_record(self):
        if not self.reserve_fund_record:
            raise ValidationError("请添加明细！")
        else:
            for rec in self.reserve_fund_record:
                if rec.estimate_amount <= 0:
                    raise ValidationError("预估金额必须大于0！")
                if rec.pay_to_who != self.pay_to_who:
                    raise ValidationError("请选择“支付类别”和备用金“支付类别”相同的消费明细！")
        if not self.department_id.manager_id:
            raise ValidationError("您的部门主管没有配置，请联系管理员配置！")
        self.get_handlers('dtdream_reserve_fund_id1')

        self.message_post(body=u"%s 提交" % (self.name))
        return True

    def compute_his_state(self):
        # 计算该单据经过哪些状态,用于驳回时候选择节点
        if not self.his_state:
            self.his_state = self.state
        elif self.state not in self.his_state:
            self.his_state += (','+self.state)

    def send_email_to_handler(self):
        base_url = self.env['ir.config_parameter'].search([('key', '=', 'web.base.url')]).value
        action = self.env['ir.actions.act_window'].sudo().search([('res_model', '=', 'dtdream.reserve.fund'),
                                                                  ('name', '=', '待我审批')]).id
        link = '/web?#id=%s&view_type=form&model=dtdream.reserve.fund&action=%s' % (self.id, action)
        url = base_url+link
        people_email_list = ''
        for person in self.current_handler:
            people_email_list += person.work_email+';'
        self.env['mail.mail'].create({
                'subject': u'【dodo提醒】%s提交了单号为：%s 的备用金申请，请您审批！'
                           % (self.applicant.name, self.name),
                'body_html': u'''
                <p>您好，</p>
                <p>%s提交的备用金申请等待您的审批！</p>
                <p> 请<a href="%s">点击此处</a>进入审批:</p>
                <p>dodo</p>
                <p>万千业务，简单有do</p>
                <p>%s</p>
                ''' % (self.applicant.name, url, datetime.today().strftime('%Y-%m-%d')),
                'email_from': self.env['ir.mail_server'].search([], limit=1).smtp_user,
                'email_to': people_email_list,
            }).send()
        return url

    @api.multi
    def btn_urge(self):
        for record in self:
            message = u"申请人发送了邮催。"
            record.message_post(body=message)
            record.send_email_to_handler()

    @api.model
    def create(self, vals):
        # 计算单号
        if ('name' not in vals) or (vals.get('name') in ('/', False)):
            vals['name'] = self.env['ir.sequence'].next_by_code('dtdream.reserve.fund')
        result = super(dtdream_reserve_fund, self).create(vals)
        return result

    @api.multi
    def wkf_draft(self):
        self.state = u'草稿'
        self.compute_his_state()
        self.current_handler = ''

    @api.multi
    def wkf_manager(self):
        self.state = u'主管审批'
        self.compute_his_state()
        if not self.department_id.manager_id:
            raise ValidationError("部门主管没有配置，请联系管理员进行配置！")
        else:
            if self.applicant.id == self.department_id.manager_id.id:
                self.current_handler = self.department_id.parent_id.manager_id
            else:
                self.current_handler = self.department_id.manager_id
            self.send_email_to_handler()

    @api.multi
    def wkf_first_sign(self):
        self.state = u'第一权签人审批'
        self.compute_his_state()
        signer_list = self.get_handlers('dtdream_reserve_fund_id1')
        self.current_handler = [(6, 0, signer_list)]
        self.send_email_to_handler()

    @api.multi
    def wkf_second_sign(self):
        self.state = u'第二权签人审批'
        self.compute_his_state()
        signer_list = self.get_handlers('dtdream_reserve_fund_id2')
        self.current_handler = [(6, 0, signer_list)]
        self.send_email_to_handler()

    @api.multi
    def wkf_president(self):
        self.state = u'总裁审批'
        self.compute_his_state()
        presidents = self.env['dtdream.reserve.position'].search([('name', '=', '总裁')])
        if not presidents:
            raise ValidationError("公司总裁没有配置，请联系管理员配置！")
        else:
            president = presidents[0].employee
            self.current_handler = president
            self.send_email_to_handler()

    @api.multi
    def wkf_interface_account(self):
        self.state = u'接口会计审批'
        self.compute_his_state()
        interfaces = self.env['dtdream.reserve.position'].search([('name', '=', '接口会计')])
        if not interfaces:
            raise ValidationError("接口会计没有配置，请联系管理员配置！")
        else:
            interface = interfaces[0].employee
            self.current_handler = interface
            self.send_email_to_handler()

    @api.multi
    def wkf_cashier(self):
        self.state = u'出纳'
        self.write({'jiekou_approve_time': datetime.now()})
        self.compute_his_state()
        cashiers = self.env['dtdream.reserve.position'].search([('name', '=', '出纳会计')])
        if not cashiers:
            raise ValidationError("出纳会计没有配置，请联系管理员配置！")
        else:
            cashier = cashiers[0].employee
            self.current_handler = cashier
            self.send_email_to_handler()

    @api.multi
    def wkf_done(self):
        self.state = u'已付款'
        self.current_handler = ''
        self.done_time = datetime.today()

    def is_right_type(self, sign_type):
        if self.type == sign_type or sign_type == '所有':
            return True
        elif self.type != '专项类' and sign_type == '非专项类':
            return True
        else:
            return False

    def condition_draft_who(self):
        first_signers = self.department_id.reserve_first_signer
        second_signers = self.department_id.reserve_second_signer
        result = ''
        president = self.env['dtdream.reserve.position'].search([('name', '=', u'总裁')])[0].employee
        if self.applicant.id == president.id:
            result = 'interface'
        elif self.applicant.id == self.department_id.manager_id.id:
            if self.department_id.parent_id:
                if len(first_signers) == 1\
                        and first_signers[0].name.id == self.department_id.manager_id.id\
                        and self.is_right_type(first_signers[0].type)\
                        and not second_signers:
                    if self.total_amount <= self.department_id.reserve_first_amount:
                        result = 'manager'
                    else:
                        result = 'president'
                elif len(first_signers) == 1\
                        and first_signers[0].name.id == self.department_id.manager_id.id\
                        and self.is_right_type(first_signers[0].type)\
                        and second_signers:
                    result = 'seccond'
                else:
                    result = 'first'
            else:
                result = 'president'
        else:
            result = 'manager'
        return result

    def condition_manager_who(self):
        first_signers = self.department_id.reserve_first_signer
        second_signers = self.department_id.reserve_second_signer
        for signer in first_signers:
            if self.department_id.manager_id.id == signer.name.id and self.is_right_type(signer.type):
                if self.total_amount <= self.department_id.reserve_first_amount:
                    return 'interface'
                else:
                    if second_signers:
                        return 'second'
                    else:
                        return 'president'
        return 'first'

    def condition_first_who(self):
        second_signers = self.department_id.reserve_second_signer
        if self.total_amount <= self.department_id.reserve_first_amount:
            return 'interface'
        else:
            if second_signers:
                return 'second'
            else:
                return 'president'

    def condition_second_who(self):
        if self.total_amount <= self.department_id.reserve_second_amount:
            return 'interface'
        else:
            return 'president'

    @api.model
    def if_in_jiekoukuaiji(self):
        return self.env.user.has_group("dtdream_reserve_fund.group_dtdream_reserve_interface")

    @api.model
    def compute_out_time(self):
        records = self.search([('is_out_time', '=', False),
                               ('state', '=', '已付款'),
                               ('pay_to_who', '=', '付款给员工')])
        for record in records:
            time_delta = datetime.today() - datetime(int(record.done_time[:4]),
                                                     int(record.done_time[5:7]),
                                                     int(record.done_time[8:10]))
            if record.type == u'常用备用金':
                if time_delta.days > 365:
                    record.is_out_time = True
            else:
                if time_delta.days > 60:
                    record.is_out_time = True



