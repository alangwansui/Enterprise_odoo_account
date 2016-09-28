$(function () {
    odoo.define('dtdream_expense.dingtalk', function (require) {
        var Dingtalk = require('dtdream_expense_dingtalk.ui');
        // var Dingtalk=require('project_timeshee.ui')
        var app = new Dingtalk();
        app.appendTo($('.nav'));
        $.init();

        // $(document).on('infinite', '.infinite-scroll', function (ev) {
        //     // 如果正在加载，则退出
        //     $('.next_report_page').trigger('click');
        // });
    });

});