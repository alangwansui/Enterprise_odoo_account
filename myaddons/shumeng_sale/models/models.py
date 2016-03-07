# -*- coding: utf-8 -*-

from openerp import models, fields, api

class shumeng_sale(models.Model):
    _inherit = 'crm.lead'

    @api.onchange("s_xitongbu")
    def onchange_xitongbu(self):
        if self.s_xitongbu:
            #self.s_hangye = self.env['shumeng.hangye'].search([('parent_id','=',self.s_xitongbu.id)])
            return {
                'domain': {
                    "s_hangye":[('parent_id','=',self.s_xitongbu.id)]
                }
            }

    @api.onchange("s_hangye")
    def onchange_hangye(self):
        if self.s_hangye:
            self.s_xitongbu = self.s_hangye.parent_id


    s_xiangmubianhao = fields.Char(string="项目编号", default="New")
    s_xiangmumingcheng = fields.Char(string="项目名称")
    s_xitongbu = fields.Many2one("shumeng.hangye", string="系统部")
    s_hangye = fields.Many2one("shumeng.hangye", string="行业")
    s_zihangye = fields.Many2one("shumeng.hangye", string="子行业")
    s_banshichu = fields.Many2one("shumeng.banshichu", string="办事处")


    @api.model
    def create(self, vals):
        if vals.get('s_xiangmubianhao', 'New') == 'New':
            vals['s_xiangmubianhao'] = self.env['ir.sequence'].next_by_code('shumeng.xiangmu') or 'New'

        result = super(shumeng_sale, self).create(vals)
        return result


class shumeng_hangye(models.Model):
    _name = 'shumeng.hangye'

    name = fields.Char("行业名称")
    parent_id = fields.Many2one("shumeng.hangye", string="上级")
    #xitongbu_id = fields.Many2one("shumeng.xitongbu", string="系统部")

class shumeng_xitongbu(models.Model):
    _name = 'shumeng.xitongbu'

    name = fields.Char("名称")

class shumeng_banshichu(models.Model):
    _name = 'shumeng.banshichu'

    name = fields.Char("名称")



class shumeng_sale_order(models.Model):
    _inherit = 'sale.order'

    partner_id = fields.Many2one('res.partner', string='Customer', required=True, change_default=True, index=True, track_visibility='always')
    state = fields.Selection([
        ('draft', '商务报备'),
        ('s1','规范性审核'),
        ('s2','商务审核'),
        ('sent', 'Quotation Sent'),
        ('sale', 'Sale Order'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
        ], string='状态', readonly=True, copy=False, index=True, track_visibility='onchange', default='draft')

    @api.multi
    def wkf_draft(self):
        # 注意state字段是没有默认值的
        self.write({'state':'draft'})

    @api.multi
    def wkf_wait(self):
        
        self.write({'state':'done'})
            
    @api.multi
    def wkf_wait2(self):
        self.write({'state':'wait2'})


    @api.multi
    def wkf_done(self):
        self.write({'state':'approve'})

    @api.multi
    def wkf_refuse(self):
        self.write({'state':'refuse'})

class ResUsers(models.Model):
    _inherit = "res.users"

    s_hangye = fields.Char(string="行业")