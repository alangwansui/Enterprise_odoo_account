odoo.define('dtdream_expense.int_out_range', function (require) {
"use strict";

var core = require('web.core');
var Model = require('web.Model');
var _t = core._t;
var FormView = require('web.FormView');

FormView.include({
    events: _.defaults({
        'keyup input.expense_int_cls': 'expense_int_click',
    }, FormView.prototype.events),

    expense_int_click: function(ev) {
        try{
            if (parseInt(document.activeElement.value.replace(",",""))>2147483647)
            {
                document.activeElement.value="";
                alert("整数类型字段值不能大于2147483647");
            }

        }
        catch (err){

        }


    },
});

});
