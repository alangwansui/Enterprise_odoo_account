# -*- coding: utf-8 -*-
from openerp import models, fields, api

# 域群组申请信息
class dtdream_ad_group(models.Model):
    _name = 'dtdream.ad.group'
    _description = u'域群组信息'
    _inherit = ['mail.thread']

    name = fields.Char(string=u'域群组名称', required=True)
    work = fields.Boolean(string=u'是否有效', default=True)
    department = fields.Many2one('hr.department', string=u'域群组所属部门', required=True)
    time = fields.Datetime(string=u'创建时间', required=True)
    description = fields.Char(string=u'描述')
    remark = fields.Char(string=u'备注')
    users = fields.Many2many(comodel_name='hr.employee', relation='dtdream_ad_user_rel', string=u'域群组成员')
    admins = fields.Many2many(comodel_name='hr.employee', relation='dtdream_ad_admin_rel', string=u'管理员')
    expire_time = fields.Many2one('dtdream.expire.time', string=u'有效时长')

    @api.multi
    def _compute_is_admin(self):
        for r in self:
            users = [user.login for user in r.admins]
            if self.env.user.login in users:
                r.is_admin = True
            else:
                r.is_admin = False

    is_admin = fields.Boolean(string=u'是否是管理员', compute=_compute_is_admin)

    def test_act(self, cr, uid, ids, context):
        viewID = self.pool['ir.ui.view'].search(cr, uid, [('name', '=', 'view.dtdream.ad.apply.name.form')])
        gid = self.pool['ir.model.data'].get_object(cr, uid, 'dtdream_ad_manager', 'group_ad_implement')
        return {
            'name': u"域群组名称",
            'view_mode': 'form',
            'view_id': viewID[0],
            'view_type': 'form',
            'res_model': 'res.groups',
            'res_id': gid[0],
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'domain': '[]',
            'context': context
        }





