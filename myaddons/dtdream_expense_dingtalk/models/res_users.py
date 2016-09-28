# -*- coding: utf-8 -*-

from openerp import models, fields, api,exceptions,_
from openerp.exceptions import except_orm, Warning, RedirectWarning
import openerp.addons.decimal_precision as dp
import openerp
from openerp import SUPERUSER_ID


import logging
_logger = logging.getLogger(__name__)


class res_users(models.Model):
    _inherit = 'res.users'

    dd_userid=fields.Char(u'钉钉UserID')

    @api.v7
    def check_credentials(self, cr, uid, password):
        _logger.info("wx_userid:"+ str(password))
        try:

            return super(res_users, self).check_credentials(cr, uid, password)
        except exceptions.AccessDenied:
            res = self.search(cr, SUPERUSER_ID, [('id', '=', uid), ('dd_userid', '=', password)])
            if not res:
                raise





