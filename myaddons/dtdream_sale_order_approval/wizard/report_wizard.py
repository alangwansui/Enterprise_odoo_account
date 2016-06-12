# -*- coding: utf-8 -*-

from openerp import models, fields, api
from datetime import datetime

class OrderWizard(models.TransientModel):
    _name = 'dtdream.order.wizard'

    liyou = fields.Text("意见", required=True)

    @api.one
    def btn_confirm(self):
        current_order = self.env['dtdream.sale.order.approval'].browse(self._context['active_id'])
        state_name =dict(self.env['dtdream.sale.order.approval']._columns['state'].selection)[current_order.state]
        shenpiren_name = self.env['hr.employee'].search([('login','=',self.env.user.login)]).name
        self.env['report.handle.approve.record'].create({"shenpiren_version":current_order.shenpiren_version,"name":state_name,"result":"驳回","shenpiren":shenpiren_name, "liyou":self.liyou,"order_handle_id":self._context['active_id']})
        current_order.write({'approveds':[(4,self.env['hr.employee'].search([('login','=',self.env.user.login)]).id)]})
        if current_order.state in ('1','2','3'):
            current_order.write({'product_approveds':[(4,self.env['hr.employee'].search([('login','=',self.env.user.login)]).id)]})
        else :
            current_order.write({'business_approveds':[(4,self.env['hr.employee'].search([('login','=',self.env.user.login)]).id)]})
        current_order.write({'warn_text':""})
        current_order.signal_workflow('btn_reject')

class OrderApproveWizard(models.TransientModel):
    _name = 'dtdream.order.approve.wizard'

    liyou = fields.Text("意见")

    @api.one
    def btn_confirm(self):
        current_order = self.env['dtdream.sale.order.approval'].browse(self._context['active_id'])
        state_name =dict(self.env['dtdream.sale.order.approval']._columns['state'].selection)[current_order.state]
        shenpiren_name = self.env['hr.employee'].search([('login','=',self.env.user.login)]).name
        self.env['report.handle.approve.record'].create({"shenpiren_version":current_order.shenpiren_version,"name":state_name,"result":"通过","shenpiren":shenpiren_name, "liyou":self.liyou,"order_handle_id":self._context['active_id']})
        if len(current_order.shenpiren)>1:
            current_order.write({'shenpiren':[(3,self.env['hr.employee'].search([('login','=',self.env.user.login)]).id)]})
        elif current_order.state=="3" or current_order.state=="5":
            current_order.pro_zongbu_finish = "1"
        current_order.write({'approveds':[(4,self.env['hr.employee'].search([('login','=',self.env.user.login)]).id)]})
        if current_order.state in ('1','2','3'):
            current_order.write({'product_approveds':[(4,self.env['hr.employee'].search([('login','=',self.env.user.login)]).id)]})
        else :
            current_order.write({'business_approveds':[(4,self.env['hr.employee'].search([('login','=',self.env.user.login)]).id)]})
        current_order.write({'warn_text':""})
        current_order.signal_workflow('btn_approve')