# -*- coding: utf-8 -*-
from openerp import models, fields, api
from .. import config


# 模块处理人的model
class dtdream_feedback_configuration(models.Model):
    _name = 'dtdream.feedback.configuration'

    name = fields.Char(string=u'模块', required=True)
    manager = fields.Many2one('hr.employee', string=u'模块处理人', required=True)


# 意见反馈的model
class dtdream_feedback_advice(models.Model):
    _name = 'dtdream.feedback.advice'
    _inherit = ['mail.thread']

    adviceMan = fields.Many2one('hr.employee', string=u'反馈人', required=True)
    advice = fields.Text(string=u'反馈意见', required=True)
    adviceTime = fields.Datetime(string=u'反馈时间', required=True, readonly=True)
    name = fields.Many2one('dtdream.feedback.configuration', string=u'问题模块', required=True)
    answer = fields.Text(string=u'回复反馈')
    answerTime = fields.Datetime(string=u'回复时间', readonly=True)
    state = fields.Selection([
        ('draft', u'草稿'),
        ('confirm', u'已查收'),
        ('answer', u'已回复')
    ], string=u'意见状态', readonly=True)

    # 计算是否是意见处理人
    @api.one
    def _compute_is_manager(self):
        user = self.env['hr.employee'].search([('user_id', '=', self.env.uid)])
        if user == self.name.manager:
            self.is_manager = True
        else:
            self.is_manager = False

    # 判断是否是处理人
    is_manager = fields.Boolean(string=u'是否是处理人', compute=_compute_is_manager, readonly=True)

    _defaults = {
        'adviceMan': lambda self, cr, uid, context: self.get_employee(cr, uid, context),
        'adviceTime': fields.Datetime.now(),
        'state': 'draft',
        'name': lambda self, cr, uid, context: self.get_name(cr, uid, context)
    }

    # 获取当前用户
    def get_employee(self, cr, uid, context={}):
        obj = self.pool.get('hr.employee')
        ids = obj.search(cr, uid, [('user_id', '=', uid)], context=context)
        # res = obj.read(cr, uid, ids, ['id', 'name'], context=context)
        return ids[0] if ids else 0

    # 获取默认所选模块
    def get_name(self, cr, uid, context={}):
        obj = self.pool.get('dtdream.feedback.configuration')
        modelName = config.config.config['_default_name']
        ids = obj.search(cr, uid, [('name', '=', modelName)], context=context)
        return ids[0] if ids else 0

    # 获取邮件服务器用户邮箱作为默认发送邮箱
    def get_mail_server_name(self):
        return self.env['ir.mail_server'].sudo().search([], limit=1).smtp_user

    # 向意见反馈人发送意见接收邮件
    def confirm_send_email(self):
        self.env['mail.mail'].create({
            'body_html': u'''<p>您的吐槽已经被捕捉，我们会马不停蹄地解决这个重大bug。</p>
                                 <p>感谢您那善于发现的眼睛。</p>
                                <p>dodo</p>
                                 <p>万千业务，简单有do</p>''',
            'subject': u'您的吐槽已被签收啦',
            'email_to': '%s' % self.adviceMan.work_email,
            'auto_delete': False,
            'email_from': self.get_mail_server_name(),
        }).send()

    # 向模块意见接收人发送意见接收邮件
    def send_to_manager(self):
        self.env['mail.mail'].create({
            'body_html': u'''<p>有关于dodo的意见已被查收</p>
                                 <p>请前往意见反馈模块查看详情。</p>
                                <p>dodo</p>
                                 <p>万千业务，简单有do</p>''',
            'subject': u'有新的dodo吐槽已被签收啦',
            'email_to': '%s' % self.name.manager.work_email,
            'auto_delete': False,
            'email_from': self.get_mail_server_name(),
        }).send()

    # 向意见反馈人发送意见处理邮件
    def answer_send_email(self):
        self.env['mail.mail'].create({
            'body_html': u'''<p>%s</p>
                                 <p>感谢您那善于发现的眼睛。</p>
                                <p>dodo</p>
                                 <p>万千业务，简单有do</p>''' % self.answer,
            'subject': u'您的吐槽已被回复啦',
            'email_to': '%s' % self.adviceMan.work_email,
            'auto_delete': False,
            'email_from': self.get_mail_server_name(),
        }).send()

    def feedback_answer(self, cr, uid, ids, context={}):
        self.write(cr, uid, ids, {'answerTime': fields.Datetime.now()}, context=context)
        obj = self.pool.get('ir.ui.view')
        viewID = obj.search(cr, uid, [('name', '=', 'view.dtdream.feedback.answer.form')], context=context)
        return {
            'name': u"意见反馈回复",
            'view_mode': 'form',
            'view_id': viewID[0],
            'view_type': 'form',
            'res_model': 'dtdream.feedback.advice',
            'res_id': ids[0],
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'domain': '[]',
            'context': context
        }

    # 工作流状态draft的处理
    @api.multi
    def wkf_draft(self):
        self.write({'state': 'draft'})

    # 工作流状态confirm的处理
    @api.multi
    def wkf_confirm(self):
        self.write({'state': 'confirm'})
        self.message_post(body=u"""<table class="zxtable" border="1" style="border-collapse: collapse;">
                                                       <tr><th style="padding:10px">反馈人</th><th style="padding:10px">%s</th></tr>
                                                       <tr><td style="padding:10px">反馈时间</td><td style="padding:10px">%s</td></tr>
                                                       </table>""" % (self.adviceMan, self.adviceTime))
        self.confirm_send_email()
        self.send_to_manager()

    # 工作流状态answer的处理
    @api.multi
    def wkf_answer(self):
        self.write({'state': 'answer'})
        self.message_post(body=u"""<table class="zxtable" border="1" style="border-collapse: collapse;">
                                               <tr><th style="padding:10px">回复人</th><th style="padding:10px">%s</th></tr>
                                               <tr><td style="padding:10px">回复时间</td><td style="padding:10px">%s</td></tr>
                                               </table>""" % (self.name.manager, self.answerTime))
        self.answer_send_email()


