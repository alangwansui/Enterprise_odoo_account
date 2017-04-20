# -*- coding: utf-8 -*-

from openerp import models, fields, api

class dtdream_sale_sign_customer(models.Model):
    _name = 'dtdream.sale.sign.customer'

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        return super(dtdream_sale_sign_customer, self).search_read(domain=domain, fields=fields, offset=offset,
                                                           limit=limit, order=order)

    name = fields.Char(default="签单客户")
    customer_code = fields.Char(string="客户编码")
    customer_name = fields.Char(string="客户名称")
    customer_contacts = fields.One2many('dtdream.sale.contact.person','customer_contact_id',string="联系人")
    description = fields.Text(string="备注")

class dtdream_sale_contact_person(models.Model):
    _name = 'dtdream.sale.contact.person'

    name = fields.Char(default="联系人")
    contact_name = fields.Char(string="联系人")
    contact_phone = fields.Char(string="联系电话")
    contact_email = fields.Char(string="Email")
    description = fields.Text(string="备注")
    customer_contact_id = fields.Many2one('dtdream.sale.sign.customer',string="对应签单客户")