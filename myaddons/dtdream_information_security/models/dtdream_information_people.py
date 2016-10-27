# -*- coding: utf-8 -*-

from openerp import models, fields, api
from datetime import datetime
from openerp.exceptions import ValidationError
from lxml import etree
from dateutil.relativedelta import relativedelta


#特殊权签设置
class dtdream_information_people(models.Model):
    _name = 'dtdream.information.people'
    name =fields.Char(default="特殊权签设置")
    juemi_shenpi = fields.Many2one("hr.employee",string="绝密信息审批人",required=True)

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        cr = self.env["dtdream.specific.people"].search([])
        res = super(dtdream_information_people, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=False)
        if res['type'] == "form":
            if cr:
                doc = etree.XML(res['arch'])
                doc.xpath("//form")[0].set("create", "false")
                res['arch'] = etree.tostring(doc)
        return res