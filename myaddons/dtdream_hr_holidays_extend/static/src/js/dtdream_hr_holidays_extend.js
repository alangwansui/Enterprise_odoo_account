odoo.define('dtdream_hr_holidays_extend.int_out_range', function (require) {
//"use strict";

var core = require('web.core');
var Model = require('web.Model');
var _t = core._t;
var FormView = require('web.FormView');
var ListView = require('web.ListView');
var Model = require('web.Model');
var QWeb = core.qweb;

    ListView.include({
//        render_buttons: function($node) {
//            var self = this;
//            if (self.fields_view.name=="view.holiday.nianxiujia.tree"){
//                if (!this.$buttons) {
//                    this.$buttons = $(QWeb.render("ListView.buttons", {'widget': this}));
//
//                    this.$buttons.find('.o_list_button_add').click(this.proxy('do_add_record'));
//
//                    $node = $node || this.options.$buttons;
//                    this.$buttons.appendTo($node);
//                    var self = this;
//        this._super.apply(this, arguments);
//        this.on('list_view_loaded', this, function() {
//            if(self.__parentedParent.$el.find('.oe_generate_po').length == 0){
//                var button = $("<button type='button' class='oe_button oe_highlight oe_generate_po'>Generate PO</button>")
//                    .click(this.proxy('generate_purchase_order'));
//                self.__parentedParent.$el.find('.oe_list_buttons').append(button);
//            }
//        });
//                }
//            }
//        },

    render_sidebar: function (arguments) {

            var self = this;
            if (!arguments[0]){
                arguments = [arguments];
            }
            this._super.apply(this, arguments);
            if (self.fields_view.name=="view.holiday.nianxiujia.all.tree"){
                var model1 = new Model('dtdream.expense.report').call('if_in_jiekoukuaiji', []).done(function(res){
                    if (self.options.sidebar && !res) {
                        var button = $("<button type='button' class='btn btn-primary btn-sm'>数据导出</button>")
                    .click(self.proxy('generate_purchase_order'));
                $(document.getElementsByClassName('o_cp_buttons')).append(button)
                    };
                });
            }

        },
        generate_purchase_order:function(){
            var self = this;
            $.blockUI();
            self.session.get_file({
                url: '/dtdream_hr_holidays_extend/annual_leave_data_proofreading_export',
                data:{data: {}},
                complete: $.unblockUI,

            });
            return self.rpc("/web/action/load", {action_id: "hr_holidays.open_nianxiujiayue_all"}).then(function(result) {
                result.views = [[result.view_id[0], "list"],[false,"form"]];
                return self.do_action(result,{clear_breadcrumbs: true});
            });
        }

    });
});
