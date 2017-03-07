# -*- coding: utf-8 -*-

from openerp import models, fields


class dtdream_hotel_zone(models.Model):
    _name = 'dtdream.hotel.zone'

    name = fields.Char(string='区域名称', size=5)
