# -*- coding: utf-8 -*-

from openerp import models, fields, api


class dtdream_customer_car_info(models.Model):
    _name = 'dtdream.customer_car_info'

    licence = fields.Char(string='车牌号', size=8)
    driver_name = fields.Char(string='司机姓名', size=8)
    driver_tel = fields.Char(string='联系方式', size=23)
    car_type = fields.Selection([('0', '小车'), ('1', '商务车'), ('2', '巴士')], string='车型')
    customer_reception_id = fields.Many2one('dtdream.customer.reception')

