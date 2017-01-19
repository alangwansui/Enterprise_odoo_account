# -*- coding: utf-8 -*-

from openerp import models, fields, api
class dtdream_security_list_git(models.Model):
    _name = "dtdream.security.list.git"
    _description = "权限申请列表"

    security_git= fields.Many2one("dtdream.information.purview")

    git = fields.Many2one("dtdream.information.type", string="所属", domain=[('type', '=', 'git')],required=True)
    space = fields.Many2one("dtdream.git.space",string="项目",required=True)
    description = fields.Char(string="描述")
    read_right = fields.Boolean(string="读权限", default=True)
    write_right = fields.Boolean(string="写权限")

    @api.onchange('git')
    def _chang_conf(self):
        domain = {}
        domain['space'] = [('type', '=', self.git.id)]
        return {'domain': domain}