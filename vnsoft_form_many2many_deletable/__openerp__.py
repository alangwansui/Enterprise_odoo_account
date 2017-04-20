# -*- coding: utf-8 -*-
#
{
    'name': 'vnsoft_form_many2many_deletable',
    'version': '0.1',
    'category': 'web',
    'sequence': 89,
    'summary': 'Hide',
    'description': """
针对one2many中many部分的记录，自定义删除条件控制，不符合条件的记录行后面将不显示删除图标。
实现步骤如下：
1.在many记录的模型中增加一个函数字段，名称固定为'deletable'，类型为boolean，为False时不允许删除
2.在view中增加字段deletable，可以设置invisible为true隐藏其栏位
源码中的purchase.py，view_purchase.xml为测试内容，可以参考实现方式。

    """,
    'author': 'VnSoft',
    'website': 'http://blog.csdn.net/vnsoft',
    # 'images': ['images/Sale_order_line_to_invoice.jpeg','images/sale_order.jpeg','images/sales_analysis.jpeg'],
    'depends': ['base', 'web'],
    'data': [],
    'qweb': ['vnsoft.xml'],
    'demo': [],
    'test': [],
    'js': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}