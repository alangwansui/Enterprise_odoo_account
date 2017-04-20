# -*- coding: utf-8 -*-
from openerp import http
from openerp.http import request
from pptx import Presentation
import StringIO
import zipfile
import base64
import os
from openerp.addons.web.controllers.main import ExcelExport

class DtdreamQualificationManagement(ExcelExport):
    # @http.route('/dtdream_qualification_management/ppt_export', auth='public')
    # def ppt_export(self,active_ids,token):
    #     import sys
    #     reload(sys)
    #     sys.setdefaultencoding('utf-8')
    #     ids = []
    #     for id in active_ids.split(','):
    #         ids.append(int(id))
    #     qualifications = request.env['dtdream.qualification.management'].browse(ids)
    #     NZip = zipfile.ZipFile('RZ_PPT.zip', 'w')
    #     for qualification in qualifications:
    #         if qualification.attachment:
    #             if qualification.attachment_name.split('.')[-1] =='pptx' or qualification.attachment_name.split('.')[-1] =='ppt':
    #                 prs = Presentation(StringIO.StringIO(base64.b64decode(qualification.attachment)))
    #                 prs.save(qualification.attachment_name)
    #                 NZip.write(qualification.attachment_name)
    #                 os.remove(qualification.attachment_name)
    #     NZip.close()
    #
    #     f = open('RZ_PPT.zip')
    #     data = f.read()
    #     f.close()
    #     return request.make_response(
    #         data,
    #         headers=[
    #             ('Content-Disposition', 'attachment; filename="%s"'
    #              % 'RZ_PPT.zip'),
    #             ('Content-Type', self.content_type)
    #         ],
    #         cookies={'fileToken': token} 
    #     )


    @http.route('/dtdream_qualification_management/ppt_export', type='json', auth="user", methods=['POST'], csrf=False)
    def ppt_export(self, **kw):
        ids = []
        active_ids = request.jsonrequest['active_ids']
        for id in active_ids:
            ids.append(int(id))
        qualifications = request.env['dtdream.qualification.management'].browse(ids)
        dir  = os.path.dirname(os.path.dirname(__file__))
        newZip = zipfile.ZipFile(r'%s/static/RZ_PPT.zip'%dir, 'w',zipfile.ZIP_DEFLATED)
        for qualification in qualifications:
            if qualification.attachment:
                if qualification.attachment_name.split('.')[-1] =='pptx' or qualification.attachment_name.split('.')[-1] =='ppt':
                    prs = Presentation(StringIO.StringIO(base64.b64decode(qualification.attachment)))
                    prs.save(qualification.batchnumber+' '+qualification.name.name+'.pptx')
                    newZip.write(qualification.batchnumber+' '+qualification.name.name+'.pptx')
                    os.remove(qualification.batchnumber+' '+qualification.name.name+'.pptx')
        newZip.close()

        return True

