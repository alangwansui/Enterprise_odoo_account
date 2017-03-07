# -*- coding: utf-8 -*-

from openerp import models, fields, api,exceptions,tools
from datetime import datetime,time
from openerp .exceptions import ValidationError,Warning
import time


import logging
_logger = logging.getLogger(__name__)


class dtdream_foreign_attachment(models.Model):

    _name = "dtdream.foreign.attachment"

    record_id=fields.Many2one('dtdream.foreign',u'对外披露')
    attachment = fields.Binary(store=True, string="附件")
    attachment_name = fields.Char(string='附件名')