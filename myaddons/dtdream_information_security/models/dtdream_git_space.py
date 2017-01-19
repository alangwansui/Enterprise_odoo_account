# -*- coding: utf-8 -*-

import openerp
from openerp import models, fields, api
from openerp.dtdream.confluence import confluence as confluence
from openerp.dtdream.gitlab.gitlab import project as project

class dtdream_confluence_space(models.Model):
    _name = 'dtdream.git.space'
    name = fields.Char(string="名称")
    key = fields.Char(string="key")
    type = fields.Many2one("dtdream.information.type")

    @api.model
    def timing_get_git_space(self):
        gitconfigs = self.env['dtdream.information.type'].search([('type', '=', 'git')])
        for gitconfig in gitconfigs:
            try:
                projectServer = project.DTProject(url=gitconfig.url, token=gitconfig.token)
                gitprojects = projectServer.get_projects()
                spaces = self.env['dtdream.git.space'].search([('type','=',gitconfig.id)])
                keylist = [space['key'] for space in spaces]
                for gitproject in gitprojects:
                    key =gitproject['namespace_name']+'/'+gitproject['name']
                    if key not in keylist:
                        self.env['dtdream.git.space'].create(
                            {'name': gitproject['name'], 'key': key, 'type': gitconfig.id})
            except Exception, e:
                print gitconfig.name+u"配置错误"
                continue