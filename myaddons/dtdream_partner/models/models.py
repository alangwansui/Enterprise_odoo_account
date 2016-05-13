# -*- coding: utf-8 -*-

from openerp import models, fields, api
import datetime

# 继承客户模型，修改字段
class dtdream_partner(models.Model):
    _inherit = ["res.partner"]

    title = fields.Many2one('res.partner.title', string='称谓')
    user_id = fields.Many2one('res.users', string='创建人',default=lambda self: self.env.user.id, help='The internal user that is in charge of communicating with this contact if any.')
    partner_code = fields.Char(string='客户编号',default='New',store=True,readonly=True)
    compare_partner_name = fields.Char(string="客户名称",store=True)
    system_department_id = fields.Many2one("dtdream.industry", string="系统部",required=True)
    industry_id = fields.Many2one('dtdream.industry',string='行业')
    office_id = fields.Many2one('dtdream.office', string='办事处')
    partner_sale_apply_id = fields.Many2one('hr.employee', string='营销责任人')
    partner_important = fields.Selection([
        ('SS', 'SS'),
        ('S', 'S'),
        ('A','A'),
        ('B','B'),
        ('C','C'),
        ('D','D'),
    ], string='客户重要级')
    type = fields.Selection([('contact', 'Contact')])
    company_type = fields.Selection(
            selection=[('person', 'Individual'),
                       ('company', 'Company')],
            string='Company Type',help="",default='company')

    @api.onchange("name","customer","company_type")
    def _onchange_name(self):
        if self.company_type == "company":
            self.is_company = True
        else:
            self.is_company = False
        if self.company_type == "company" and self.customer == True:
            self.compare_partner_name = self.name
        else:
            self.compare_partner_name=""

    _sql_constraints = [
        ('name_unique', 'UNIQUE(compare_partner_name)', "名称不能重复！"),
    ]

    @api.onchange("system_department_id")
    def onchange_system_department(self):
        if self.system_department_id:
            if self.industry_id.parent_id != self.system_department_id:
                self.industry_id = ""
            return {
                'domain': {
                    "industry_id":[('parent_id','=',self.system_department_id.id)]
                }
            }

    @api.onchange("industry_id")
    def onchange_industry_id(self):
        if self.industry_id:
            self.system_department_id = self.industry_id.parent_id
            
    @api.model
    def create(self, vals):
        if vals.get('partner_code', 'New') == 'New' and vals.get('company_type') == 'company' and vals.get('customer') == True:
            o_id = vals.get('office_id')
            i_id = vals.get('industry_id')
            office_rec = self.env['dtdream.office'].search([('id','=',o_id)])
            industry_rec = self.env['dtdream.industry'].search([('id','=',i_id)])

            # 办事处编号A1+行业编号（A02）+建立时间（201603）+两位流水号+客户级别（SS/S/A/B/C/D）
            vals['partner_code'] = ''.join([office_rec.code,industry_rec.code,self.env['ir.sequence'].next_by_code('partner.code'),vals.get('partner_important')]) or 'New'

        result = super(dtdream_partner, self).create(vals)
        return result

    @api.one
    def copy(self, default=None):
        default = dict(default or {})
        default['compare_partner_name'] = ('%s (copy)') % self.compare_partner_name
        return super(dtdream_partner, self).copy(default)

class dtdream_res_user(models.Model):
    _inherit = "res.users"

    def create(self, cr, uid, vals, context=None):
        user_id = super(dtdream_res_user, self).create(cr, uid, vals, context=context)
        user = self.browse(cr, uid, user_id, context=context)
        user.partner_id.active = user.active
        user.partner_id.write({'company_type':'person'})
        if user.partner_id.company_id:
            user.partner_id.write({'company_id': user.company_id.id})
        return user_id

class dtdream_res_partner_title(models.Model):
    _inherit = 'res.partner.title'

    name = fields.Char(string='称谓', required=True, translate=True)