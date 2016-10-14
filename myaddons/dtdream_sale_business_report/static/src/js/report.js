odoo.define('dtdream_report.test', function (require) {
"use strict";
var data = require('web.data');
var core = require('web.core');
var Model = require('web.Model');
var _t = core._t;
var FormView = require('web.FormView');
FormView.include({
    // Stores all the parameters of the action.
    load_record: function(record) {
        this._super.apply(this, arguments);
        var timer = window.setInterval(function(){
            if($('.apply_dis_sale_report th:eq(6)').length != 0){
                if (record.is_bus_shenpiren == false && record.is_pro_shenpiren == true){
                    if(!$('.apply_dis_sale_report th:eq(6)').is(":hidden")){
                        $('.apply_dis_sale_report th:eq(6)').hide();
                        $('.apply_dis_sale_report td[data-field="apply_discount"]').hide();
                        clearInterval(timer);
                    }
                }
                else
                    clearInterval(timer);
            }
        },300)
    },
});
})
