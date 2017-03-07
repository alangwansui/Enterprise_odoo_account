odoo.define('dtdream_hr_performance.test', function (require) {
"use strict";

var core = require('web.core');
var Model = require('web.Model');
var ListView = require('web.ListView');

ListView.include({
        add_button_import: function () {
            var self = this;
            var button = $('<button type="button" class="btn btn-sm btn-default dtimport">导入</button>');
            var root = self.$el.parents();
            button.bind('click',function(){
                self.do_action({
                    'type': 'ir.actions.act_window',
                    'res_model': 'dtimport.hr.performance',
                    'name': "导入",
                    'view_mode': 'form',
                    'view_type': 'form',
                    'views': [[false, 'form']],
                    'target': 'new'},{
                    on_close: function () {
                        self.reload();
                    }
                });
            });
            if ($(".dtimport").length == 0){
                button.appendTo(root.find('.o_list_buttons'));
            }
            $('.o_list_button_import').remove();
        },
    });

});
