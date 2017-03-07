# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.exceptions import ValidationError
from lxml import etree


class dtdream_hotels_management(models.Model):
    _name = 'dtdream.hotels.management'

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(dtdream_hotels_management, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=False)
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
        return super(dtdream_hotels_management, self).unlink()

    def compute_hotel_usetimes(self):
        for rec in self:
            cr = rec.env['dtdream.customer.reception'].search([('hotels_name', '=', rec.id)])
            rec.use_times = len(cr) if cr else 0

    @api.multi
    def name_get(self):
        super(dtdream_hotels_management, self).name_get()
        data = []
        for rec in self:
            name = ''
            name += rec.name + ('-' + {'5': u'五星', '4': u'四星', '3': u'三星', '2': u'二星'}.get(rec.star, u''))
            data.append((rec.id, name))
        return data

    name = fields.Char(string='酒店名称', size=16)
    star = fields.Selection([('5', '五星'), ('4', '四星'), ('3', '三星'), ('2', '二星'), ('1', '其它'), ('0', '员工宿舍')], string='星级')
    type = fields.Selection([('0', '住宿'), ('1', '住宿,餐饮')], string='类型')
    addr = fields.Char(string='地址', size=48)
    contact = fields.Char(string='联系人', size=8)
    tel = fields.Char(string='预订电话', size=48)
    expense_up = fields.Selection([('1', '是'), ('0', '否')], string='是否可以挂账')
    mark = fields.Text(string='备注')
    infor = fields.Text(string='说明')
    tips = fields.Text(string='攻略')
    use_times = fields.Integer(string='关联次数', compute=compute_hotel_usetimes)
    parent_id = fields.Many2one('dtdream.hotel.zone', string='区域')
    room = fields.One2many('dtdream.hotel.room', 'hotel_id', string='住宿')
    dinner = fields.One2many('dtdream.hotel.dinner', 'hotel_id', string='餐饮')

    @api.multi
    def act_dtdream_hotels_relation(self):
        action = {
                'name': '客户接待',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'dtdream.customer.reception',
                'domain': [('hotels_name', '=', self.id)],
                'context': self._context,
                }
        return action


class dtdream_hotel_room(models.Model):
    _name = 'dtdream.hotel.room'

    name = fields.Char(string='房型', size=16)
    price = fields.Integer(string='房价(元)')
    mark = fields.Text(string='备注')
    hotel_id = fields.Many2one(string='酒店')


class dtdream_hotel_dinner(models.Model):
    _name = 'dtdream.hotel.dinner'
    _rec_name = 'price'

    price = fields.Char(string='人均(元)', size=16)
    tastes = fields.Char(string='菜系', size=8)
    mark = fields.Text(string='备注')
    hotel_id = fields.Many2one(string='酒店')


