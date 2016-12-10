odoo.define('dtdream_customer_recce.test', function (require) {
"use strict";

var core = require('web.core');
var Model = require('web.Model');
var _t = core._t;
var FormView = require('web.FormView');
var form_common = require('web.form_common');

FormView.include({
    events: _.defaults({
        'click select[name=customer_level]': 'test_click2',
        'click  label.customer_level_tooltip':'tooltip_show',
    }, FormView.prototype.events),

    test_click2: function(ev) {
    var anArray = ['"VIP"','"S"','"A+"','"A"' ];
        var list = $("select[name=customer_level]").find("option")
        for( var i=0;i<list.length;i++){
            if (!anArray.includes(list[i].value)){
                $(list[i]).remove()
            }
        }
    },
    tooltip_show: function(){
        var pop = new form_common.FormViewDialog(self, {
                       'type': 'ir.actions.act_window',
                        'view_type': 'form',
                        'view_mode': 'form',
                        'res_model': 'dtdream.customer.receptiontool.wizard',
                        'res_id': '',
                        'context':'',
                    }).open();
         $('.modal-footer').hide()
    }

});

});
