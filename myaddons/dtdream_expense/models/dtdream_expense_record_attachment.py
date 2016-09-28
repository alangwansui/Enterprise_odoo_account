# -*- coding: utf-8 -*-

from openerp import models, fields, api,exceptions,tools
from datetime import datetime,time
from openerp .exceptions import ValidationError,Warning
import time


import logging
_logger = logging.getLogger(__name__)


class dtdream_expense_record_attachment(models.Model):

    _name = "dtdream.expense.record.attachment"
    _inherit = ['mail.thread']

    record_id=fields.Many2one('dtdream.expense.record',u'费用明细')
    attachment = fields.Binary(store=True, string="附件", track_visibility='onchange')

    image = fields.Binary("附件", attachment=True)