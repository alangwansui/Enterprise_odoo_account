# -*- coding: utf-8 -*-

from openerp import models, fields, api
import calendar
import hashlib
import re
from openerp.osv import expression
from Crypto.Cipher import AES
from binascii import b2a_hex, a2b_hex

class dtdream_wage(models.Model):
    _name = 'dtdream.wage'
    _description = u"工资详情"

    job_code = fields.Char(string="工号",required=True)
    name = fields.Char(string="姓名",required=True)
    nick_name = fields.Char(string="花名",required=True)
    entry_day = fields.Date(string="入职日期")
    department = fields.Char(string="一级部门")
    nashui_place = fields.Char(string="纳税地")
    work_place = fields.Char(string="工作地")
    basic_wage = fields.Char(string="基本工资",required=True)
    gangweijintie = fields.Char(string="岗位津贴",default=0)
    bingjiakoukuan = fields.Float(string="病假扣款")
    shijiakoukuang = fields.Float(string="事假扣款")
    chanjiakoukuan = fields.Float(string="产假扣款")
    yingfashouru = fields.Float(string="应发合计")
    shangyuehuoshibuzhu = fields.Float(string="上月交通伙食补助")
    sysnjtbxzbz=fields.Float(string="上月市内交通报销转补助")
    bfsyjbgzhgwjt = fields.Float(string="补发上月基本工资和岗位津贴")
    shangyuewaipaijintie=fields.Float(string="上月外派津贴")
    nianxiujiaduixian = fields.Float(string="年休假兑现")
    shuihoudaikoujiashubaoxianfei = fields.Float(string="税后代扣家属保险费")
    shuihoudaikoudangfei = fields.Float(string="税后代扣党费")
    shuihoudaikouzichan = fields.Float(string="税后代扣资产")
    sijijiabanfei = fields.Float(string="司机加班费")
    zhuanlijiang = fields.Float(string="专利奖")
    neibutuijianjiang = fields.Float(string="内部推荐奖")
    xinxianquanjiang = fields.Float(string="信息安全奖")
    kouyanglaoxian = fields.Float(string="扣个人养老险")
    kouyiliaoxian = fields.Float(string="扣个人医疗险")
    koushiyexian = fields.Float(string="扣个人失业险")
    kougongjijin = fields.Float(string="扣个人公积金")
    bukouyanglaoxian = fields.Float(string="补扣个人养老险")
    bukouyiliaoxian= fields.Float(string="补扣个人医疗险")
    bukoushiyexian = fields.Float(string="补扣个人失业险")
    bugongjijin = fields.Float(string="补扣个人公积金")
    shuiqianshouru = fields.Char(string="税前收入",required=True)
    kousuodeshui = fields.Float(string="扣个人所得税")
    shifashouru = fields.Char(string="实发收入",required=True)
    faxinyue = fields.Date(string="发薪月")

    warning_digit = {
        'title': u"提示",
        'message': u"只可输入数字!"
    }
    #加密
    def gz_encrypt(self,text):
        accessKeyID = "1zFWrgiAjDipR3Ge"
        accessKeySecret = "9c1ydKIbXfEMM43u"
        obj = AES.new(accessKeyID, AES.MODE_CBC, accessKeySecret)
        message = text
        length = 16
        count = len(message)
        if count < length:
            add = length - count
            message = message + ('\0' * add)
        elif count > length:
            add = (length - (count % length))
            message = message + ('\0' * add)
        ciphertext = obj.encrypt(message)
        return b2a_hex(ciphertext)

    #解密
    def gz_decrypt(self,text):
        accessKeyID = "1zFWrgiAjDipR3Ge"
        accessKeySecret = "9c1ydKIbXfEMM43u"
        obj2 = AES.new(accessKeyID, AES.MODE_CBC, accessKeySecret)
        result = obj2.decrypt(a2b_hex(text))
        return result.rstrip('\0')

    @api.model
    def create(self, vals):
        if vals['shifashouru']:
            vals['shifashouru'] = self.gz_encrypt(vals['shifashouru'])
        if vals['shuiqianshouru']:
            vals['shuiqianshouru'] = self.gz_encrypt(vals['shuiqianshouru'])
        if vals['gangweijintie']:
            vals['gangweijintie'] = self.gz_encrypt(vals['gangweijintie'])
        if vals['basic_wage']:
            vals['basic_wage'] = self.gz_encrypt(vals['basic_wage'])
        return super(dtdream_wage, self).create(vals)

    @api.multi
    def write(self, vals):
        if vals.get('shifashouru'):
            vals['shifashouru'] = self.gz_encrypt(vals['shifashouru'])
        if vals.get('shuiqianshouru'):
            vals['shuiqianshouru'] = self.gz_encrypt(vals['shuiqianshouru'])
        if vals.get('gangweijintie'):
            vals['gangweijintie'] = self.gz_encrypt(vals['gangweijintie'])
        if vals.get('basic_wage'):
            vals['basic_wage'] = self.gz_encrypt(vals['basic_wage'])
        return super(dtdream_wage, self).write(vals)

    @api.onchange('shifashouru')
    @api.constrains('shifashouru')
    def _check_shifashouru(self):
        p = re.compile(r'(^[0-9]*$)|(^[0-9]+(\.[0-9]+)?$)')
        if self.shifashouru:
            shifashouru = self.shifashouru.encode("utf-8")
            if not p.search(shifashouru):
                return {"warning": self.warning_digit}



    @api.onchange('shuiqianshouru')
    @api.constrains('shuiqianshouru')
    def _check_shuiqianshouru(self):
        p = re.compile(r'(^[0-9]*$)|(^[0-9]+(\.[0-9]+)?$)')
        if self.shuiqianshouru:
            shuiqianshouru = self.shuiqianshouru.encode("utf-8")
            if not p.search(shuiqianshouru):
                return {"warning": self.warning_digit}

    @api.onchange('gangweijintie')
    @api.constrains('gangweijintie')
    def _check_gangweijintie(self):
        p = re.compile(r'(^[0-9]*$)|(^[0-9]+(\.[0-9]+)?$)')
        if self.gangweijintie:
            gangweijintie = self.gangweijintie.encode("utf-8")
            if not p.search(gangweijintie):
                return {"warning": self.warning_digit}

    @api.onchange('basic_wage')
    @api.constrains('basic_wage')
    def _check_basic_wage(self):
        p = re.compile(r'(^[0-9]*$)|(^[0-9]+(\.[0-9]+)?$)')
        if self.basic_wage:
            basic_wage = self.basic_wage.encode("utf-8")
            if not p.search(basic_wage):
                return {"warning": self.warning_digit}

    @api.multi
    def read(self,fields=None, context=None, load='_classic_read'):
        result = super(dtdream_wage, self).read(fields=fields, load=load)
        for rec in result:
            rec['shifashouru'] = self.gz_decrypt(rec['shifashouru'])
            rec['shuiqianshouru'] = self.gz_decrypt(rec['shuiqianshouru'])
            rec['gangweijintie'] = self.gz_decrypt(rec['gangweijintie'])
            rec['basic_wage'] = self.gz_decrypt(rec['basic_wage'])
        return result

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        params = self._context.get('params', {})
        action = params.get('action', None)
        if action:
            domain = expression.AND([[], domain])
        result =  super(dtdream_wage, self).search_read(domain=domain, fields=fields, offset=offset,limit=limit, order=order)
        p = re.compile(r'(^[0-9]*$)|(^[0-9]+(\.[0-9]+)?$)')
        for rec in result:
            if not p.search(rec['shifashouru']):
                rec['shifashouru'] = self.gz_decrypt(rec['shifashouru'])
            if not p.search(rec['shuiqianshouru']):
                rec['shuiqianshouru'] = self.gz_decrypt(rec['shuiqianshouru'])
            if not p.search(rec['gangweijintie']):
                rec['gangweijintie'] = self.gz_decrypt(rec['gangweijintie'])
            if not p.search(rec['basic_wage']):
                rec['basic_wage'] = self.gz_decrypt(rec['basic_wage'])
        return result

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, context=None, orderby=False, lazy=True):
        params = self._context.get('params', {})
        action = params.get('action', None)
        if action:
            domain = expression.AND([[], domain])
        result = super(dtdream_wage, self).read_group(domain, fields, groupby, offset=offset, limit=limit,orderby=orderby, lazy=lazy)
        p = re.compile(r'(^[0-9]*$)|(^[0-9]+(\.[0-9]+)?$)')
        for rec in result:
            if not p.search(rec['shifashouru']):
                rec['shifashouru'] = self.gz_decrypt(rec['shifashouru'])
            if not p.search(rec['shuiqianshouru']):
                rec['shuiqianshouru'] = self.gz_decrypt(rec['shuiqianshouru'])
            if not p.search(rec['gangweijintie']):
                rec['gangweijintie'] = self.gz_decrypt(rec['gangweijintie'])
            if not p.search(rec['basic_wage']):
                rec['basic_wage'] = self.gz_decrypt(rec['basic_wage'])
        return result



    @api.model
    def get_wage_list_by_user(self,userName=None,startMonth=None,endMonth=None):
        lists=[]
        tlists=[]
        total_benyueyingfa=0
        total_koushebaogjj=0
        total_shuiqianshouru=0
        total_kougeren=0
        total_shifa=0
        if startMonth:
            start = startMonth+'-01'
            if endMonth:
                day = calendar.monthrange(int(endMonth.split('-')[0]), int(endMonth.split('-')[1]))[1]
                end = endMonth + '-' + str(day)
                lists = self.env["dtdream.wage"].sudo().search([('job_code','=',userName),('faxinyue', '>=', start), ('faxinyue', '<=', end)])
            else:
                lists = self.env["dtdream.wage"].sudo().search([('job_code','=',userName),('faxinyue', '>=', start)])
        else:
            if endMonth:
                day = calendar.monthrange(int(endMonth.split('-')[0]),int(endMonth.split('-')[1]))[1]
                end = endMonth + '-' + str(day)
                lists = self.env["dtdream.wage"].sudo().search([('job_code','=',userName),('faxinyue', '<=', end)])

        for list in lists:
            t ={
                'id':list.id,
                'month': list.faxinyue[:7],
                'benyueyingfa': list.yingfashouru,
                'koushebaogjj': list.kougongjijin,
                'shuiqianshouru': self.gz_decrypt(list.shuiqianshouru),
                'kougeren':list.kousuodeshui ,
                'shifa': self.gz_decrypt(list.shifashouru),
            }
            tlists.append(t)
            total_benyueyingfa+=list.yingfashouru
            total_koushebaogjj +=list.kougongjijin
            total_shuiqianshouru +=int(self.gz_decrypt(list.shuiqianshouru))
            total_kougeren +=list.kousuodeshui
            total_shifa +=int(self.gz_decrypt(list.shifashouru))

        res = {
            "lists": tlists,
            'total_benyueyingfa': total_benyueyingfa,
            'total_koushebaogjj': total_koushebaogjj,
            'total_shuiqianshouru': total_shuiqianshouru,
            'total_kougeren': total_kougeren,
            'total_shifa': total_shifa,
        }
        return res

    @api.model
    def get_wage_phone_list_by_user(self,userName=None,startMonth=None,endMonth=None):
        lists = []
        tlists = []
        if startMonth:
            start = startMonth + '-01'
            if endMonth:
                day = calendar.monthrange(int(endMonth.split('-')[0]), int(endMonth.split('-')[1]))[1]
                end = endMonth + '-'+str(day)
                lists = self.env["dtdream.wage"].sudo().search([('job_code','=',userName),('faxinyue', '>=', start), ('faxinyue', '<=', end)])
            else:
                lists = self.env["dtdream.wage"].sudo().search([('job_code','=',userName),('faxinyue', '>=', start)])
        else:
            if endMonth:
                day = calendar.monthrange(int(endMonth.split('-')[0]), int(endMonth.split('-')[1]))[1]
                end = endMonth + '-' + str(day)
                lists = self.env["dtdream.wage"].sudo().search([('job_code','=',userName),('faxinyue', '<=', end)])

        for list in lists:
            t = {
                'id': list.id,
                'month': list.faxinyue[:7],
                'benyueyingfa': list.yingfashouru,
                'koushebaogjj': list.kougongjijin,
                'shuiqianshouru': self.gz_decrypt(list.shuiqianshouru),
                'kougeren': list.kousuodeshui,
                'shifa': self.gz_decrypt(list.shifashouru),
            }
            tlists.append(t)

        res = {
            "lists": tlists
        }
        return res

    @api.model
    def get_wage_list_detail_by_month(self,userName=None, month=None):
        list = self.env["dtdream.wage"].sudo().search([('job_code','=',userName),('faxinyue', 'like', (month + '%'))])[0]
        res={
            'faxinyue':list.faxinyue[:7],
            'basic_wage':self.gz_decrypt(list.basic_wage),
            'gangweijintie':self.gz_decrypt(list.gangweijintie),
            'bfsyjbgzhgwjt':list.bfsyjbgzhgwjt,
            'shijiakoukuang':list.shijiakoukuang,
            'bingjiakoukuan':list.bingjiakoukuan,
            'chanjiakoukuan':list.chanjiakoukuan,
            'shangyuehuoshibuzhu':list.shangyuehuoshibuzhu,
            'sysnjtbxzbz':list.sysnjtbxzbz,
            'shangyuewaipaijintie':list.shangyuewaipaijintie,
            'sijijiabanfei':list.sijijiabanfei,
            'zhuanlijiang':list.zhuanlijiang,
            'neibutuijianjiang':list.neibutuijianjiang,
            'xinxianquanjiang':list.xinxianquanjiang,
            'nianxiujiaduixian':list.nianxiujiaduixian,
            'yingfashouru':list.yingfashouru,
            'kouyanglaoxian':list.kouyanglaoxian,
            'kouyiliaoxian':list.kouyiliaoxian,
            'koushiyexian':list.koushiyexian,
            'kougongjijin':list.kougongjijin,
            'bukouyanglaoxian':list.bukouyanglaoxian,
            'bukouyiliaoxian':list.bukouyiliaoxian,
            'bukoushiyexian':list.bukoushiyexian,
            'bugongjijin':list.bugongjijin,
            'shuiqianshouru':self.gz_decrypt(list.shuiqianshouru),
            'kousuodeshui':list.kousuodeshui,
            'shuihoudaikoujiashubaoxianfei':list.shuihoudaikoujiashubaoxianfei,
            'shuihoudaikoudangfei':list.shuihoudaikoudangfei,
            'shuihoudaikouzichan':list.shuihoudaikouzichan,
            'shifashouru':self.gz_decrypt(list.shifashouru)
        }
        lists=[]
        lists.append(res)
        return {"lists":lists}

    @api.model
    def get_pay_phone_list_detail_by_month(self, userName=None, month=None):
        list = self.env["dtdream.wage"].sudo().search([('job_code','=',userName),('faxinyue', 'like',(month+'%'))])[0]
        res = {
            'faxinyue': list.faxinyue[:7],
            'basic_wage': self.gz_decrypt(list.basic_wage),
            'gangweijintie': self.gz_decrypt(list.gangweijintie),
            'bfsyjbgzhgwjt': list.bfsyjbgzhgwjt,
            'shijiakoukuang': list.shijiakoukuang,
            'bingjiakoukuan': list.bingjiakoukuan,
            'chanjiakoukuan': list.chanjiakoukuan,
            'shangyuehuoshibuzhu': list.shangyuehuoshibuzhu,
            'sysnjtbxzbz': list.sysnjtbxzbz,
            'shangyuewaipaijintie': list.shangyuewaipaijintie,
            'sijijiabanfei': list.sijijiabanfei,
            'zhuanlijiang': list.zhuanlijiang,
            'neibutuijianjiang': list.neibutuijianjiang,
            'xinxianquanjiang': list.xinxianquanjiang,
            'nianxiujiaduixian': list.nianxiujiaduixian,
            'yingfashouru': list.yingfashouru,
            'kouyanglaoxian': list.kouyanglaoxian,
            'kouyiliaoxian': list.kouyiliaoxian,
            'koushiyexian': list.koushiyexian,
            'kougongjijin': list.kougongjijin,
            'bukouyanglaoxian': list.bukouyanglaoxian,
            'bukouyiliaoxian': list.bukouyiliaoxian,
            'bukoushiyexian': list.bukoushiyexian,
            'bugongjijin': list.bugongjijin,
            'shuiqianshouru': self.gz_decrypt(list.shuiqianshouru),
            'kousuodeshui': list.kousuodeshui,
            'shuihoudaikoujiashubaoxianfei': list.shuihoudaikoujiashubaoxianfei,
            'shuihoudaikoudangfei': list.shuihoudaikoudangfei,
            'shuihoudaikouzichan': list.shuihoudaikouzichan,
            'shifashouru': self.gz_decrypt(list.shifashouru)
        }
        lists = []
        lists.append(res)
        return {"lists": lists}

