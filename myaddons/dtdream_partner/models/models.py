# -*- coding: utf-8 -*-

from openerp import models, fields, api
import datetime  

# 继承客户模型，修改字段
class dtdream_partner(models.Model):
    _inherit = ["res.partner"]

    partner_code = fields.Char(string='客户编号',default='New',store=True,readonly=True)
    industry_id = fields.Many2one('dtdream.industry',string='行业',required=True)
    office_id = fields.Many2one('dtdream.office', string='办事处',required=True)
    partner_important = fields.Selection([
        ('SS', 'SS'),
        ('S', 'S'),
        ('A','A'),
        ('B','B'),
        ('C','C'),
        ('D','D'),
    ], string='客户重要级', required=True)
    partner_owner = fields.Many2one('res.users', string='营销责任人')

    @api.model
    def create(self, vals):
        if vals.get('partner_code', 'New') == 'New':

            o_id = vals.get('office_id')
            i_id = vals.get('industry_id')
            office_rec = self.env['dtdream.office'].search([('id','=',o_id)])
            industry_rec = self.env['dtdream.industry'].search([('id','=',i_id)])
            # year_month = datetime.datetime.now().strftime("%Y%m")

            # 办事处编号A1+行业编号（A02）+建立时间（201603）+两位流水号+客户级别（SS/S/A/B/C/D）
            vals['partner_code'] = ''.join([office_rec.code,industry_rec.code,self.env['ir.sequence'].next_by_code('partner.code'),vals.get('partner_important')]) or 'New'

        result = super(dtdream_partner, self).create(vals)
        return result
