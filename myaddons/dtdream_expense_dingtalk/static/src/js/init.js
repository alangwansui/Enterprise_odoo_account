$(function () {
    odoo.define('dtdream_expense.dingtalk', function (require) {
        var Dingtalk = require('dtdream_expense_dingtalk.ui');
        var app = new Dingtalk();
        app.appendTo($('.nav'));
        $.init();
    });
});