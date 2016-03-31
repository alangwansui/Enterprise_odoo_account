# -*- coding: utf-8 -*-
import openerp
from openerp import models, fields, api
from datetime import datetime
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from dateutil.relativedelta import relativedelta
from openerp.exceptions import ValidationError

# class dtdream_hr_holidays_extend_new_menu(models.Model):
#     _name="dtdream.hr.holidays.extend.new.menu"
#     related_user=fields.Many2one("res.users")
#     shenpiren1=fields.Many2one('hr.employee',string="第一审批人",required=True)
#     shenpiren2=fields.Many2one('hr.employee',string="第二审批人")
#     shenpiren3=fields.Many2one('hr.employee',string="第三审批人")
#     shenpiren4=fields.Many2one('hr.employee',string="第四审批人")
#     shenpiren5=fields.Many2one('hr.employee',string="第五审批人")
#     number=fields.Integer(default=lambda self:len(self.search([('create_uid','=',self.env.user.id)])))
#
#     @api.multi
#     @api.constrains("number")
#     def chuangjian_number(self):
#         print self.number
#         if self.number > 0:
#             raise ValidationError('您已经有审批人配置，请编辑原有记录。')


class dtdream_hr_holidays_extend(models.Model):
    # _name = "dtdream.hr.holidays.extend"
    _inherit = "hr.holidays"
    shenqingren=fields.Char( string="申请人",default=lambda self:self.env['hr.employee'].search([('login','=',self.env.user.login)]).name,readonly=1)
    gonghao=fields.Char(string="工号",default=lambda self:self.env['hr.employee'].search([('login','=',self.env.user.login)]).job_number,readonly=1)
    bumen=fields.Char(string="部门",default=lambda self:self.env['hr.employee'].search([('login','=',self.env.user.login)]).department_id.name,readonly=1)
    create_time= fields.Datetime(string='申请时间',default=datetime.today()- relativedelta(hours=8),readonly=1)

    shenpiren1=fields.Many2one('hr.employee',string="第一审批人",
                               )
    shenpiren2=fields.Many2one('hr.employee',string="第二审批人")
    shenpiren3=fields.Many2one('hr.employee',string="第三审批人")
    shenpiren4=fields.Many2one('hr.employee',string="第四审批人")
    shenpiren5=fields.Many2one('hr.employee',string="第五审批人")

    # current_shenpiren_id=fields.Integer(default=lambda self:self.shenpiren.search([('create_uid','=',self.env.user.id)]).shenpiren1,string='当前审批人员工id')
    current_shenpiren_id=fields.Integer()

    list=fields.Boolean(default=True)
    state=fields.Selection([('draft', '草稿'), ('cancel', 'Cancelled'),('confirm', '一级审批'),
                            ('confirm2', '二级审批'),('confirm3', '三级审批'),('confirm4', '四级审批'),
                            ('confirm5', '五级审批'), ('refuse', 'Refused'), ('validate1', 'Second Approval'), ('validate', 'Approved')],
                           'Status', readonly=True, track_visibility='onchange', copy=False,default='draft')


    @api.constrains(shenpiren1)
    def un(self):
        print self.env['hr.department'].search([('id','=',self.department_id.id)])


    @api.one
    def _compute_is_shenpiren(self):
        if self.current_shenpiren_id==self.env['hr.employee'].search([('login','=',self.env.user.login)]).id:
            self.is_shenpiren=True
        else:
            self.is_shenpiren=False

    is_shenpiren=fields.Boolean(compute=_compute_is_shenpiren,string="是否审批人")


    def _check_state_access_right(self, cr, uid, vals, context=None):#重写hr_holidays里面的 _check_state_access_right，将权限开放到base.group_user
        if vals.get('state') and vals['state'] not in ['draft', 'confirm', 'confirm2' ,'confirm3','confirm4','confirm5', 'cancel'] and not self.pool['res.users'].has_group(cr, uid, 'base.group_user'):
            return False
        return True


    def holidays_confirm(self, cr, uid, ids, context=None):
        print "holidays_confirm"
        print cr
        print uid
        print ids
        return self.write(cr, uid, ids, {'state': 'confirm'})

    def holidays_confirm2(self, cr, uid, ids, context=None):
        print "holidays_confirm2"
        print cr
        print uid
        print ids
        return self.write(cr, uid, ids, {'state': 'confirm2'})

    def holidays_confirm3(self, cr, uid, ids, context=None):
        print "holidays_confirm3"
        print cr
        print uid
        print ids
        return self.write(cr, uid, ids, {'state': 'confirm3'})

    def holidays_confirm4(self, cr, uid, ids, context=None):
        print "holidays_confirm4"
        print cr
        print uid
        print ids
        print set(ids)
        return self.write(cr, uid, ids, {'state': 'confirm4'})

    def holidays_confirm5(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'confirm5'})

    def holidays_reset(self, cr, uid, ids, context=None):#重写该方法，开放重置按钮权限
        self.write(cr, openerp.SUPERUSER_ID, ids, {
            'state': 'draft',
            'manager_id': False,
            'manager_id2': False,
        })
        to_unlink = []
        for record in self.browse(cr, uid, ids, context=context):
            for record2 in record.linked_request_ids:
                self.holidays_reset(cr, uid, [record2.id], context=context)
                to_unlink.append(record2.id)
        if to_unlink:
            self.unlink(cr, uid, to_unlink, context=context)
        return True


    def holidays_validate(self, cr, uid, ids, context=None):
        obj_emp = self.pool.get('hr.employee')
        ids2 = obj_emp.search(cr, uid, [('user_id', '=', uid)])
        manager = ids2 and ids2[0] or False
        self.write(cr, uid, ids, {'state': 'validate'}, context=context)
        data_holiday = self.browse(cr, uid, ids)
        for record in data_holiday:
            if record.double_validation:
                self.write(cr, uid, [record.id], {'manager_id2': manager})
            else:
                self.write(cr, openerp.SUPERUSER_ID, [record.id], {'manager_id': manager})
                print "2222222222222222222222"
            if record.holiday_type == 'employee' and record.type == 'remove':
                meeting_obj = self.pool.get('calendar.event')
                meeting_vals = {
                    'name': record.display_name,
                    'categ_ids': record.holiday_status_id.categ_id and [(6,0,[record.holiday_status_id.categ_id.id])] or [],
                    'duration': record.number_of_days_temp * 8,
                    'description': record.notes,
                    'user_id': record.user_id.id,
                    'start': record.date_from,
                    'stop': record.date_to,
                    'allday': False,
                    'state': 'open',            # to block that meeting date in the calendar
                    'class': 'confidential'
                }
                #Add the partner_id (if exist) as an attendee
                if record.user_id and record.user_id.partner_id:
                    meeting_vals['partner_ids'] = [(4,record.user_id.partner_id.id)]

                ctx_no_email = dict(context or {}, no_email=True)
                meeting_id = meeting_obj.create(cr, uid, meeting_vals, context=ctx_no_email)
                print "33333333333333333333333333333"
                self._create_resource_leave(cr, openerp.SUPERUSER_ID, [record], context=context)
                print "44444444444444444444444444444444444"
                self.write(cr, openerp.SUPERUSER_ID, ids, {'meeting_id': meeting_id})
                print "5555555555555555555"
            elif record.holiday_type == 'category':
                emp_ids = record.category_id.employee_ids.ids
                leave_ids = []
                batch_context = dict(context, mail_notify_force_send=False)
                for emp in obj_emp.browse(cr, uid, emp_ids, context=context):
                    vals = {
                        'name': record.name,
                        'type': record.type,
                        'holiday_type': 'employee',
                        'holiday_status_id': record.holiday_status_id.id,
                        'date_from': record.date_from,
                        'date_to': record.date_to,
                        'notes': record.notes,
                        'number_of_days_temp': record.number_of_days_temp,
                        'parent_id': record.id,
                        'employee_id': emp.id
                    }
                    leave_ids.append(self.create(cr, uid, vals, context=batch_context))
                for leave_id in leave_ids:
                    # TODO is it necessary to interleave the calls?
                    for sig in ('confirm', 'validate', 'second_validate'):
                        self.signal_workflow(cr, uid, [leave_id], sig)
        return True




