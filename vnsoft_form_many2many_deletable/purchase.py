# -*- coding: utf-8 -*-

from openerp import SUPERUSER_ID, workflow
from datetime import datetime
from dateutil.relativedelta import relativedelta
from operator import attrgetter
from openerp.tools.safe_eval import safe_eval as eval
from openerp.osv import fields, osv

class purchase_order_line(osv.osv):
    _inherit = "purchase.order.line"

    def _check_deletable(self,cr,uid,ids,args,field_name,context=None):
        res = dict.fromkeys(ids,True)
        for i in self.browse(cr,uid,ids,context=context):
            if i.price_unit>100:
                res[i.id] = False

        return res

    _columns={
        "deletable":fields.function(_check_deletable,type="boolean",string="Deletable"),
    }