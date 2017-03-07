# -*- coding: utf-8 -*-

import openerp
from openerp import models, fields, api
from  . import dtdream_confluence_space as confluence_space

class dtdream_security_list_confluence(models.Model):
    _name = "dtdream.security.list.confluence"
    _description = u"权限申请列表"
    security_conf= fields.Many2one("dtdream.information.purview",string="摘要")


    @api.multi
    def get_space(self):
        spaces = self.env['dtdream.confluence.space'].search([])
        return [(r['key'], r['name']) for r in spaces]

    conf = fields.Many2one("dtdream.information.type",string="所属",domain=[('type','=','confluence')])
    space = fields.Many2one("dtdream.confluence.space",string="空间",required=True)
    description = fields.Char(string="描述")
    read_right = fields.Boolean(string="读权限",default=True)
    write_right = fields.Boolean(string="写权限")

    @api.onchange('conf')
    def _chang_conf(self):
        domain = {}
        # tt = self.env['dtdream.information.type'].sudo().search(['type','=','confluence'])[0]
        # if tt:
        domain['space'] = [('type','!=',False)]
        return {'domain': domain}

    @api.constrains('write_right')
    @api.onchange('write_right')
    def _constrains_write_right(self):
        for rec in self:
            if rec.write_right:
                rec.read_right=True

