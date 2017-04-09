# -*- coding: utf-8 -*-
from openerp import models, fields, api
from openerp.osv import osv

class dtdream_ad_it_man(models.Model):
    _name = 'dtdream.ad.it.man'
    _description = u'IT实施组'

    user = fields.Many2one(comodel_name='hr.employee', string=u'IT组成员', required=True)
    work = fields.Boolean(string=u"是否是处理人", required=True, default=False)
    is_create = fields.Boolean(string=u"是否是创建", required=True, default=False)

    @api.multi
    def name_get(self):
        data = []
        for r in self:
            data.append((r.id, r.user.nick_name))
        return data

    @api.model
    def create(self, vals):
        vals['is_create'] = True
        res = super(dtdream_ad_it_man, self).create(vals)
        user_id = self.env['hr.employee'].search([('id', '=', vals['user'])])[0].user_id
        self.env.ref("dtdream_ad_manager.group_ad_implement").sudo().write({'users': [(4, user_id.id)]})
        return res

    @api.multi
    def write(self, vals):
        vals['is_create'] = True
        res = super(dtdream_ad_it_man, self).write(vals)
        if not vals.has_key('user'):
            return res
        user_id = self.env['hr.employee'].search([('id', '=', vals['user'])])[0].user_id
        self.env.ref("dtdream_ad_manager.group_ad_implement").sudo().write({'users': [(4, user_id.id)]})
        return res

    @api.multi
    def unlink(self):
        array = [(3, u.user.user_id.id) for u in self]
        if (3, self.env.uid) in array:
            raise osv.except_osv(u'不能删除自己！')
        res = super(dtdream_ad_it_man, self).unlink()
        self.env.ref("dtdream_ad_manager.group_ad_implement").sudo().write({'users': array})
        return res

    @api.onchange('user')
    def domain_user(self):
        user_ids = [man.user.id for man in self.search([])]
        return {'domain': {'user': [('id', 'not in', user_ids)]}}



class dtdream_ad_apply_man(models.Model):
    _name = 'dtdream.ad.apply.man'
    _description = u'域群组申请组'

    user = fields.Many2one(comodel_name='hr.employee', string=u'申请组成员', required=True)

    @api.multi
    def name_get(self):
        data = []
        for r in self:
            data.append((r.id, r.user.nick_name))
        return data

    @api.model
    def create(self, vals):
        res = super(dtdream_ad_apply_man, self).create(vals)
        user_id = self.env['hr.employee'].search([('id', '=', vals['user'])])[0].user_id
        self.env.ref("dtdream_ad_manager.group_ad_apply").sudo().write({'users': [(4, user_id.id)]})
        return res

    @api.multi
    def write(self, vals):
        res = super(dtdream_ad_apply_man, self).write(vals)
        if not vals.has_key('user'):
            return res
        user_id = self.env['hr.employee'].search([('id', '=', vals['user'])])[0].user_id
        self.env.ref("dtdream_ad_manager.group_ad_apply").sudo().write({'users': [(4, user_id.id)]})
        return res

    @api.multi
    def unlink(self):
        array = [(3, u.user.user_id.id) for u in self]
        if (3, self.env.uid) in array:
            raise osv.except_osv(u'不能删除自己！')
        res = super(dtdream_ad_apply_man, self).unlink()
        self.env.ref("dtdream_ad_manager.group_ad_apply").sudo().write({'users': array})
        return res

    @api.onchange('user')
    def domain_user(self):
        user_ids = [man.user.id for man in self.search([])]
        return {'domain': {'user': [('id', 'not in', user_ids)]}}