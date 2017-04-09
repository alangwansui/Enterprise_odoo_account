# -*- coding: utf-8 -*-

from openerp.http import request,serialize_exception

from openerp.addons.web.controllers.main import ExcelExport
from cStringIO import StringIO
from openerp import http
from openerp.http import request
import base64
from docx.enum.text import WD_ALIGN_PARAGRAPH
try:
    import cPickle as pickle
except ImportError:
    import pickle

class Mymodule(ExcelExport):
    @http.route('/mymodule/mymodule/', auth='public')
    def index(self,**kw):
        fruits = http.request.env['dtdream_project_bid_authorize_apply.fruits']
        return http.request.render("dtdream_project_bid_authorize_apply.index",
                {'fruits': fruits.search([])})

    @http.route('/dtdream_authorization/dtdream_shouquan_export', type='http', auth='public')
    def dtdream_auth_export(self,data,token):
        active_ids = data.split(',')

        excel_values = []
        excel_values.append(
            [u'授权渠道', u'项目编号', u'项目名称', u'办事处', u'系统部门', u'营销责任人', u'商务提前报备', u'投标项目名称', u'招标编号', u'招标单位', u'招投标时间'])
        dtdream_authorization_apply = request.env['dtdream.project.bid.authorize.apply'].search([('id', '=', int(active_ids[0]))])
        from docx import Document
        from docx.shared import Inches
        from docx.shared import RGBColor
        import sys
        reload(sys)
        sys.setdefaultencoding('utf-8')
        document = Document()
        auth = dtdream_authorization_apply
        project_name = auth.bidding_rep_pro_name
        bidding_number = auth.bidding_number
        h = document.add_heading(u'', level=1)
        r = h.add_run(u'杭州数梦工场科技有限公司项目授权函\n')
        h.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r.font.size = Inches(0.3)
        r.font.color.rgb = RGBColor(0x00, 0x00, 0x00)
        p1 = u"致："

        p = document.add_paragraph(p1, style='Body Text')
        r = p.add_run(auth.bidding_company.center(20))
        r.underline = True
        r.bold = True

        p2 = u"\t杭州数梦工场科技有限公司（“授权方”），主要营业地点设在杭州市西湖区云栖小镇山景路中大银座9栋，因--（招标编号：-- ）投标邀请需要，兹授权--办理以下事宜：".split(u'--')
        p = document.add_paragraph(p2[0])
        r=p.add_run(project_name.center(20))
        r.underline=True
        r.bold=True
        p.add_run(p2[1])
        p.add_run(bidding_number)
        p.add_run(p2[2])
        r=p.add_run(auth.authorization.content.center(20))
        r.underline=True
        r.bold=True
        p.add_run(p2[3])

        p3 = u"\t(1)"
        p32 = u"  全权办理和履行投标所要求的各项事宜。\n"
        p33 = U"\t(2)"
        p34 = u"  按照项目需求提供授权方相关产品的销售、技术服务和技术咨询。\n"
        p = document.add_paragraph(p3)
        r = p.add_run(p32)
        r.underline = True
        r.bold = True
        p.add_run(p33)
        r=p.add_run(p34)
        r.underline = True
        r.bold = True

        p4 = u'\t被授权方须在授权方授权范围内办理和履行投标所要求的各项事宜。授权方与被授权方是独立的合同方，被授权方对其行为向第三方负责并独立承担相应的法律责任。'
        document.add_paragraph(p4)
        date = auth.bidding_time.split(u'-')
        table = document.add_table(rows=2, cols=2)
        tb_cells = table.rows[0].cells
        tb_cells[0].text = u''
        tb_cells[1].text = u'制造厂名称（公章） \n杭州数梦工场科技有限公司'
        tb_cells = table.rows[1].cells
        tb_cells[0].text = u''
        tb_cells[1].text = u'日期：{0[0]}年{0[1]}月{0[2]}日'.format(date)
        document.add_page_break()
        fp = StringIO()
        document.save(fp)
        fp.seek(0)
        data = fp.read()
        fp.close()
        zf = StringIO(base64.decodestring(auth.attachment_ids.attachment))
        data = zf.read().replace('单位名称','数梦工厂')
        zf.close()
        doc = Document('test.docx')
        paragraphs = doc.paragraphs
        replace_content = ['招标项目名称']
        replace_content_dict = {'招标项目名称':'替换内容'}
        fp = StringIO()
        flag = True
        for p in paragraphs:
            for run in p.runs:
                for rc in replace_content:
                    if rc in run.text:
                        print rc
                        print run.text

        paragraphs[2]._p.r_lst[0].xml.replace('杭州', '北京')

        doc.save(fp)
        fp.seek(0)
        data = fp.read()
        fp.close()
        return request.make_response(
            data,
            headers=[
                ('Content-Disposition', 'attachment; filename="%s"'
                 % 'authorization.doc'),
                ('Content-Type', self.content_type)
            ],
            cookies={'fileToken': token}
        )

    @http.route('/dtdream_authorization/dtdream_shouhou_export', type='http', auth='public')
    def dtdream_authorization_export(self, data, token):
        active_ids = data.split(',')
        excel_header = []
        excel_values = []
        excel_values.append([u'授权渠道',u'项目编号', u'项目名称', u'办事处', u'系统部门', u'营销责任人', u'商务提前报备', u'投标项目名称', u'招标编号', u'招标单位', u'招投标时间'])
        dtdream_authorization_apply = request.env['dtdream.project.bid.authorize.apply'].search(
            [('id', '=', int(active_ids[0]))])
        if dtdream_authorization_apply.authorization:
            for auth_way in dtdream_authorization_apply.authorization:
                excel_values.append([auth_way.content, dtdream_authorization_apply.project_number if dtdream_authorization_apply.project_number else u'',
                                    dtdream_authorization_apply.rep_pro_name.name if dtdream_authorization_apply.rep_pro_name.name else u'',
                                    dtdream_authorization_apply.office_id.name if dtdream_authorization_apply.office_id.name else u'',
                                    dtdream_authorization_apply.system_department_id.name if dtdream_authorization_apply.system_department_id.name else u'',
                                    dtdream_authorization_apply.sale_apply_id.full_name if dtdream_authorization_apply.sale_apply_id.full_name else u'',
                                     dtdream_authorization_apply.business_advanced_report.name if dtdream_authorization_apply.business_advanced_report else u'',
                                    dtdream_authorization_apply.bidding_rep_pro_name if dtdream_authorization_apply.bidding_rep_pro_name else u'',
                                    dtdream_authorization_apply.bidding_number if dtdream_authorization_apply.bidding_number else u'',
                                    dtdream_authorization_apply.bidding_company if dtdream_authorization_apply.bidding_company else u'',
                                    dtdream_authorization_apply.bidding_time if dtdream_authorization_apply.bidding_time else u''])
        else :
            excel_values.append([u'',
                                 dtdream_authorization_apply.project_number if dtdream_authorization_apply.project_number else u'',
                                 dtdream_authorization_apply.rep_pro_name.name if dtdream_authorization_apply.rep_pro_name.name else u'',
                                 dtdream_authorization_apply.office_id.name if dtdream_authorization_apply.office_id.name else u'',
                                 dtdream_authorization_apply.system_department_id.name if dtdream_authorization_apply.system_department_id.name else u'',
                                 dtdream_authorization_apply.sale_apply_id.full_name if dtdream_authorization_apply.sale_apply_id.full_name else u'',
                                 dtdream_authorization_apply.business_advanced_report.name if dtdream_authorization_apply.business_advanced_report else u'',
                                 dtdream_authorization_apply.bidding_rep_pro_name if dtdream_authorization_apply.bidding_rep_pro_name else u'',
                                 dtdream_authorization_apply.bidding_number if dtdream_authorization_apply.bidding_number else u'',
                                 dtdream_authorization_apply.bidding_company if dtdream_authorization_apply.bidding_company else u'',
                                 dtdream_authorization_apply.bidding_time if dtdream_authorization_apply.bidding_time else u''])

        from docx import Document
        from docx.shared import Inches
        from docx.shared import RGBColor
        document = Document()
        auth=dtdream_authorization_apply
        project_name = auth.bidding_rep_pro_name
        bidding_number = auth.bidding_number
        h=document.add_heading(u'', level=1)
        r=h.add_run(u'杭州数梦工场科技有限公司售后服务承诺\n')
        h.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r.font.size=Inches(0.3)
        r.font.color.rgb = RGBColor(0x00, 0x00, 0x00)
        p1 =u"\t杭州数梦工场科技有限公司（简称数梦工场）深知客户业务创新和业务效率提升的重要性，我们提出“全栈式、零距离”的服务理念。数梦工场本着用户至上的原则，凭借经验丰富的技术服务团队、功能最全的飞天云平台、技术最领先的大数据平台、无可比拟的地域优势，承诺给"
        p12=u"及此项目合作伙伴提供场景化的服务解决方案。\n"
        p = document.add_paragraph(p1,style='Body Text')
        r = p.add_run(project_name.center(20))
        r.underline = True
        r.bold=True
        p.add_run(p12)
        p2=u"\t数梦工场设有7×24小时的远程支援中心，提供全天候无间断的远程技术服务，可随时接收故障的反馈和申报，数梦工场将根据故障报告内容对问题进行分级，在规定的时间内对申报的问题进行第一时间的响应及解决。\n"
        p = document.add_paragraph(p2)
        p3=u"\t根据"
        p32=u"（招标编号："
        p33=U")项目的需要，"
        p34=u"数梦工场承诺对本项目涉及的软件设备提供：--7×24小时远程技术支持服务--。在软件设备出现故障时，本项目的合作伙伴及客户均可以得到数梦工场快捷的技术支持。--在--3年--内，用户将得到所购设备最新的主机及云平台软件的维护性版本并享有与原有软件相同的许可权利，如软件补丁、更新软件及其配套文档资料。\n".split(u'--')
        p = document.add_paragraph(p3)
        r = p.add_run(project_name.rjust(15))
        r.underline = True
        r.bold = True
        r=p.add_run(p32)
        r.underline=True
        r = p.add_run(bidding_number.ljust(20))
        r.underline = True
        r.bold = True
        p.add_run(p33)
        r= p.add_run(p34[0])
        r.bold=True
        r=p.add_run(p34[1])
        r.bold=True
        r.underline=True
        r=p.add_run(p34[2])
        r.bold=True
        p.add_run(p34[3])
        r=p.add_run(p34[4])
        r.underline=True
        p.add_run(p34[5])
        date = auth.bidding_time.split(u'-')
        p4 = u"杭州数梦工场科技有限公司\n{0[0]}年{0[1]}月{0[2]}日".format(date)
        p = document.add_paragraph(p4)
        p.paragraph_format.alignment =  WD_ALIGN_PARAGRAPH.RIGHT
        # p.add_run('bold').bold = True
        # p.add_run(' and some ')
        # p.add_run('italic.').italic = True

        # document.add_heading('Heading, level 1', level=1)
        # document.add_paragraph('Intense quote', style='IntenseQuote')
        #
        # document.add_paragraph(
        #     'first item in unordered list', style='ListBullet'
        # )
        # document.add_paragraph(
        #     'first item in ordered list', style='ListNumber'
        # )
        document.add_page_break()
        docfile = dtdream_authorization_apply.attachment_ids.attachment
        # docx = pickle.dumps(docfile)
        # f= open('logo.png', 'wb')
        # pickle.dump(docx, f)
        # f.close()
        fp = StringIO()
        document.save(fp)
        fp.seek(0)
        data = fp.read()
        fp.close()
        return request.make_response(
            data,
            headers=[
                ('Content-Disposition', 'attachment; filename="%s"'
                 % self.filename("dtdream_authorization_export")),
                ('Content-Type', self.content_type)
            ],
            cookies={'fileToken':token}
        )
        # return request.make_response(
        #     self.from_data(excel_header, excel_values),
        #     headers=[
        #         ('Content-Disposition', 'attachment; filename="%s"'
        #          % self.filename("dtdream_authorization_export")),
        #         ('Content-Type', self.content_type)
        #     ],
        #     cookies={'fileToken': token}
        # )

