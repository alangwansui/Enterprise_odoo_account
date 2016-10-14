odoo.define('dtdream_budget.test', function (require) {
"use strict";

var core = require('web.core');
var Model = require('web.Model');
var _t = core._t;
var FormView = require('web.FormView');

FormView.include({
    events: _.defaults({
        'keyup input.budget_int_cls': 'test_click2',
    }, FormView.prototype.events),

    test_click2: function(ev) {
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
