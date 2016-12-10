odoo.define('dtdream_demand.test', function (require) {
"use strict";

var core = require('web.core');
var Model = require('web.Model');
var _t = core._t;
var FormView = require('web.FormView');

FormView.include({
    events: _.defaults({
        'keyup input.demand_app_check': 'validate_check',
    }, FormView.prototype.events),

    validate_check: function(ev) {
        try{
            if (parseInt(document.activeElement.value.replace(",","")) < 0)
            {
                document.activeElement.value = 0;
                alert("预估工时不能为负数!");
            }

        }
        catch (err){

        }

    },

    load_record:function(record) {
        this._super.apply(this, arguments);
        var num = parseInt(record.state)|| 0;
        if (num == 0 || num == 99)
            num = 0;
        if (num != 0) {
            var timer = window.setInterval(function(){
                if ($('.dtdream_demand_notebook').length != 0) {
                    $('.manage_page.active').removeClass('active');
                    $('.manage_page:eq(' + (num-1) + ')').addClass('active');
                    $('.manage_page:eq(' + (num+4) + ')').addClass('active');
                    clearInterval(timer);
                    }
                }, 100);
            }
        },
    });
})