# -*- coding: utf-8 -*-

import openerp
from openerp import models, fields, api
from openerp.dtdream.confluence import confluence as confluence

class dtdream_confluence_space(models.Model):
    _name = 'dtdream.confluence.space'
    name = fields.Char(string="名称")
    key = fields.Char(string="key")
    type = fields.Many2one("dtdream.information.type")

    @api.model
    def timing_get_confluence_space(self):
        confluenceconfigs = self.env['dtdream.information.type'].search([('type','=','confluence')])
        for confluenceconfig in confluenceconfigs:
            ConfluenceServer = confluence.ConfluenceServer(ConfluenceURL=confluenceconfig.url, login=confluenceconfig.user,password=confluenceconfig.passw)
            confluenceSpace = ConfluenceServer.GetSpaces()
            spaces = self.env['dtdream.confluence.space'].search([('type','=',confluenceconfig.id)])
            keyList = [space['key'] for space in spaces]
            for space in confluenceSpace:
                if space['type'] == 'global' and space['key'] not in keyList:
                    self.env['dtdream.confluence.space'].create({'name': space['name'], 'key': space['key'],'type':confluenceconfig.id})

