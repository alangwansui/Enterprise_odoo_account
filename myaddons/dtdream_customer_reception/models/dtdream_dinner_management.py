# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.exceptions import ValidationError
from lxml import etree


class dtdream_dinner_management(models.Model):
    _name = 'dtdream.dinner.management'

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(dtdream_dinner_management, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=False)
        hotel_manage = self.env['dtdream.customer.reception.config'].search([], limit=1).hotel_manage.user_id
        doc = etree.XML(res['arch'])
        if res['type'] == "form" and hotel_manage != self.env.user:
            doc.xpath("//form")[0].set("create", "false")
            doc.xpath("//form")[0].set("edit", "false")
        if res['type'] == "kanban" and hotel_manage != self.env.user:
            doc.xpath("//kanban")[0].set("create", "false")
            doc.xpath("//kanban")[0].set("edit", "false")
        res['arch'] = etree.tostring(doc)
        return res

    @api.multi
    def unlink(self):
        hotel_manage = self.env['dtdream.customer.reception.config'].search([], limit=1).hotel_manage.user_id
        if hotel_manage != self.env.user:
            raise ValidationError("您没有删除该记录的权限!")
        return super(dtdream_dinner_management, self).unlink()

    def compute_dinner_usetimes(self):
        for rec in self:
            cr = rec.env['dtdream.customer.reception'].search([('hotels_name_r', '=', rec.id)])
            rec.use_times = len(cr) if cr else 0

    name = fields.Char(string='餐厅', size=32)
    addr = fields.Char(string='地址', size=32)
    parent_id = fields.Many2one('dtdream.dinner.zone', string='区域')
    tel = fields.Char(string='电话', size=48)
    price = fields.Char(string='人均(元)', size=32)
    contact = fields.Char(string='联系人', size=8)
    info = fields.Text(string='简介')
    dinner = fields.One2many('dtdream.special.dishes', 'dinner_id', string='特色菜')
    use_times = fields.Integer(string='关联次数', compute=compute_dinner_usetimes)
    mark = fields.Text(string='备注')

    @api.multi
    def act_dtdream_dinner_relation(self):
        action = {
                'name': '客户接待',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'dtdream.customer.reception',
                'domain': [('hotels_name_r', '=', self.id)],
                'context': self._context,
                }
        return action


class dtdream_dinner_zone(models.Model):
    _name = 'dtdream.dinner.zone'

    name = fields.Char(string='餐饮区域', size=16)


class dtdream_special_dishes(models.Model):
    _name = 'dtdream.special.dishes'

    name = fields.Char(string='菜名', size=16)
    price = fields.Integer(string='价格')
    mark = fields.Text(string='备注')
    dinner_id = fields.Many2one('dtdream.dinner.management')




