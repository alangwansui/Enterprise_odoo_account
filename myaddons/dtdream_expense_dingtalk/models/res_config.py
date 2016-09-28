# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning
import openerp.addons.decimal_precision as dp
import logging
_logger = logging.getLogger(__name__)

class expense_config_settings(models.TransientModel):
    _name = 'dtdream.expense.config.settings'
    _inherit = 'res.config.settings'
    _description = u'报销单设置'

    agentId=fields.Char(u'AgentID')
    agentUrl=fields.Char(u'URL')
    corpId=fields.Char(u'CorpID')
    corpSecret=fields.Char(u'CorpSecret')

    @api.multi
    def set_agentId(self):
        self.env['ir.config_parameter'].set_param('dtdream.expense.agentId', self[0].agentId)

    @api.multi
    def set_agentUrl(self):
        self.env['ir.config_parameter'].set_param('dtdream.expense.agentUrl', self[0].agentUrl)

    @api.multi
    def set_corpId(self):
        self.env['ir.config_parameter'].set_param('dtdream.dingtalk.corpId', self[0].corpId)

    @api.multi
    def set_corpSecret(self):
        self.env['ir.config_parameter'].set_param('dtdream.dingtalk.corpSecret', self[0].corpSecret)

    @api.multi
    def get_default_agentId(self):

        params = self.env['ir.config_parameter']

        agentId = params.get_param('dtdream.expense.agentId', default='')
        _logger.info("fuck...")
        _logger.info("agentId:"+str(agentId))
        return {'agentId': agentId}

    @api.multi
    def get_default_agentUrl(self):
        params = self.env['ir.config_parameter']

        agentUrl = params.get_param('dtdream.expense.agentUrl', default='')
        _logger.info("agentURL:"+ str(agentUrl));
        return {'agentUrl': agentUrl}

    @api.multi
    def get_default_corpId(self):
        params = self.env['ir.config_parameter']

        corpId = params.get_param('dtdream.dingtalk.corpId', default='')
        return {'corpId': corpId}

    @api.multi
    def get_default_corpSecret(self):
        params = self.env['ir.config_parameter']

        corpSecret = params.get_param('dtdream.dingtalk.corpSecret', default='')
        return {'corpSecret': corpSecret}


