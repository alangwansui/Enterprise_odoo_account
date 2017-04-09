odoo.define('dtdream_export.export', function (require) {
"use strict";
var data = require('web.data');
var core = require('web.core');
var csrf_token = core['csrf_token'];
var Model = require('web.Model');
var _t = core._t;
var FormView = require('web.FormView');
var rec_id;
FormView.include({

    events: _.defaults({
        'click .dtdream_shouhou_export': 'export_shouhou_click',
        'click .dtdream_shouquan_export': 'export_shouquan_click',
    }, FormView.prototype.events),

    export_shouhou_click: function(kwargs) {
        var self = this;
//        rows = $('.o_list_view>tbody>tr');
//        active_ids=[];
//        $.each(rows, function () {
//            $row = $(this);
//            if ($row.attr('data-id')){
//                checked = $row.find('td input[type=checkbox]')[0].checked;
//                if(checked){
//                    active_ids.push($row.attr('data-id'));
//                }
//
//            }
//        });
        var id = parseInt(window.location.href.split('=')[1].split('&')[0]);
        $.blockUI();
        self.session.get_file({
            url: '/dtdream_authorization/dtdream_shouhou_export',
            data:{data: [id]},
            complete: $.unblockUI,
        });
    },


    export_shouquan_click: function(kwargs) {
        var self = this;
//        rows = $('.o_list_view>tbody>tr');
//        active_ids=[];
//        $.each(rows, function () {
//            $row = $(this);
//            if ($row.attr('data-id')){
//                checked = $row.find('td input[type=checkbox]')[0].checked;
//                if(checked){
//                    active_ids.push($row.attr('data-id'));
//                }
//
//            }
//        });
        var id = parseInt(window.location.href.split('=')[1].split('&')[0]);
        $.blockUI();
        self.session.get_file({
            url: '/dtdream_authorization/dtdream_shouquan_export',
            data:{data: [id]},
            complete: $.unblockUI,
        });
    },

});
})


