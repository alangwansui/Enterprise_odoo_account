# -*- coding: utf-8 -*-
import openerp
from openerp import models, fields, api, exceptions

class dtdream_ecard(models.Model):
    _name = 'dtdream_ecard.dtdream_ecard'
    _description = u"电子名片"

    # {"content": "操作成功",
    #  "detail": {"cmpy": "数梦工场", "mobile_phone": "13967192098", "empno": "0217", "idx": "601", "address": "杭州滨江白金海岸",
    #             "email": "zhouwm@dtdream.com", "name": "周文明", "org": "数据开发部", "face_idx": "-1", "full_name": "狄仁杰"},
    #  "title": "操作结果", "type": "1"}

    name = fields.Many2one('hr.employee', string="创建人", required=True,
                           default=lambda self: self.env["hr.employee"].search([("user_id", "=", self.env.user.id)]))
    ecard_name = fields.Many2one('hr.employee', string=u"名片名称", help=u"名片名称", required=True,
                                 default=lambda self: self.env["hr.employee"].search([("user_id", "=", self.env.user.id)]))

    ecard_index = fields.Char(string=u"名片编号", defualt=0)
    ecard_url = fields.Char(string=u"名片地址", defualt="http://www.dtdream.com")

    emp_no = fields.Char(string=u"员工工号")
    emp_name = fields.Char(string=u"员工姓名")
    emp_alias_name = fields.Char(string=u"员工花名")

    emp_email = fields.Char(string=u"员工邮箱", required=True)
    emp_phone = fields.Char(string=u"员工手机", required=True)
    emp_duty = fields.Char(string=u"员工职务", required=True)

    # @api.depends("ecard_name")
    # def _compute_index(self):
    #     for r in self:
    #         r.ecard_index = self.search_count([('emp_no', '=', r.emp_no)])
    #
    # @api.depends("ecard_index")
    # def _compute_url(self):
    #     for r in self:
    #         if r.ecard_index == 0:
    #             sss = r.ecard_index
    #         else:
    #             sss = r.emp_no + "-" + r.ecard_index
    #         r.ecard_url = "http://www.dtdream.com/pub/e_card/%s.html" % (sss)
    # @api.depends('ecard_name')
    # def _compute_emp_email(self):
    #     for r in self:
    #         r.emp_email = r.ecard_name.work_email
    #
    # @api.depends('ecard_name')
    # def _compute_emp_phone(self):
    #     for r in self:
    #         r.emp_phone= r.ecard_name.mobile_phone
    # @api.depends("ecard_name")
    # def _compute_emp_no(self):
    #     for r in self:
    #         r.emp_no = r.ecard_name.job_number
    #
    # @api.depends('ecard_name')
    # def _compute_emp_name(self):
    #     for r in self:
    #         r.emp_name = r.ecard_name.full_name
    #
    # @api.depends('ecard_name')
    # def _compute_emp_alias_name(self):
    #     for r in self:
    #         r.emp_alias_name = r.ecard_name.nick_name

    @api.multi
    def unlink(self):
        raise exceptions.ValidationError('没有权限删除')

    @api.multi
    def write(self, vals):
        if not self:
            return True

        if 'ecard_name' in vals and self.ecard_name.id != vals['ecard_name']:
            raise exceptions.ValidationError('名片名称不可以修改')

        if self.ecard_url == False:
            if self.ecard_index == "0":
                sss = self.emp_no
            else:
                sss = self.emp_no + "-" + self.emp_no
            self._get_ecard_url(sss, vals)

        return super(dtdream_ecard, self).write(vals)


    @api.model
    def create(self, vals):

        if ('ecard_index' not in vals) or (vals.get('ecard_index') in ('/', False)):
            emp = self.env["hr.employee"].search([("id", "=", vals['ecard_name'])])
            vals['ecard_index'] = str(self.search_count([('emp_no', '=', emp.job_number)]))
            vals['emp_no'] = emp.job_number
            vals['emp_name'] = emp.full_name
            vals['emp_alias_name'] = emp.nick_name

        if vals['ecard_index'] == "0":
            sss = emp.job_number
        else:
            sss = emp.job_number + "-" + vals['ecard_index']

        self._get_ecard_url(sss, vals)

        result = super(dtdream_ecard, self).create(vals)

        return result

    def _get_ecard_url(self, sss, vals):
        try:
            import json
            import requests
            headers = {"Content-Type": "application/json"}
            data = {
                "key": "6adc91a4-c6c9-4cf6-9a34-01879eef5fe4",
                "sn": sss
            }
            ecard_server = openerp.tools.config['ecard_url']
            url = ecard_server + "/key"
            r = requests.post(url, data=json.dumps(data), headers=headers)
            if r.status_code == 200:
                info = json.JSONDecoder().decode(r.text)
                vals['ecard_url'] = ecard_server + "/%s.html" % (info['data']['key'])
        except Exception, e:
            pass
