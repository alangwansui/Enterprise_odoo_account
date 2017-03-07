odoo.define('dtdream_ad_manager.compute_name', function (require) {
"use strict";

var core = require('web.core');
var Model = require('web.Model');
var _t = core._t;
var FormView = require('web.FormView');

FormView.include({
     events: _.defaults({
        'change div.ad_department_input div input, input.ad_group_input, input.ad_label_input, select.ad_ext_select': 'change_name',
    }, FormView.prototype.events),

    change_name: function() {
        var array = ['DT'];
        var ad_department = $('div.ad_department_input').find('input').val();
        var ad_group = $('input.ad_group_input').val();
        var ad_label = $('input.ad_label_input').val();
        var ad_ext = $('select.ad_ext_select').val();
        if(ad_department)
            array.push(ad_department);
        else if(ad_group)
            array.push(ad_group);
        if(ad_label)
            array.push(ad_label);
        if(ad_ext !== 'false')
            array.push(ad_ext.slice(1,ad_ext.length-1));
        $('input.ad_name_input').val(array.join('-'));
    },
});

});