# -*- encoding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


{
    'name': '数梦会计科目表',
    'version': '1.0',
    'category': 'Localization/Account Charts',
    'website': 'http://.dtdream.com',
    'description': """

    科目类型\会计科目表模板\增值税\辅助核算类别\管理会计凭证簿\财务会计凭证簿

    添加中文省份数据

    增加小企业会计科目表

    """,
    'depends': ['l10n_cn'],
    'data': [
        'account_chart_template.xml',
        'account_chart_template.yml',
    ],
    'license': 'GPL-3',
    'installable': True,
}
