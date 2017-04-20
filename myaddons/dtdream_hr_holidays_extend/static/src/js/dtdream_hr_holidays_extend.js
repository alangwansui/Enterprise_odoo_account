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

    render_sidebar: function (arguments) {

            var self = this;
            if (!arguments[0]){
                arguments = [arguments];
            }
            this._super.apply(this, arguments);
            if (self.fields_view.name=="view.holiday.nianxiujia.all.tree"){
                var model1 = new Model('hr.holidays').call('if_in_hr', []).done(function(res){
                    if (self.options.sidebar && res) {
                        var button = $("<button type='button' class='btn btn-primary btn-sm' style='margin-right: 10px;'>数据导出</button>")
                    .click(self.proxy('generate_purchase_order'));
                    var button1 = $("<button type='button' class='btn btn-primary btn-sm'>结算</button>")
                    .click(self.proxy('nianxiujia_jiesuan'));
                $(document.getElementsByClassName('o_cp_buttons')).append(button)
                $(document.getElementsByClassName('o_cp_buttons')).append(button1)
                    };
                });
            }

        },
        generate_purchase_order:function(){
            var self = this;
            rows = $('.o_list_view>tbody>tr');
            active_ids=[];
            $.each(rows, function () {
                $row = $(this);
                if ($row.attr('data-id')){
                    checked = $row.find('td input[type=checkbox]')[0].checked;
                    if(checked){
                        active_ids.push($row.attr('data-id'));
                    }
                }
            });
            if(active_ids.length>0){
                $.blockUI();
                self.session.get_file({
                    url: '/dtdream_hr_holidays_extend/annual_leave_data_proofreading_export',
                    data:{active_ids: active_ids},
                    complete: $.unblockUI,
                });

                return self.rpc("/web/action/load", {action_id: "hr_holidays.open_nianxiujiayue_all"}).then(function(result) {
                    result.views = [[result.view_id[0], "list"],[false,"form"]];
                    return self.do_action(result,{clear_breadcrumbs: true});
                });
            }else{
                alert("请选中数据")
            }
        },

        nianxiujia_jiesuan:function(){
            var self = this;
            rows = $('.o_list_view>tbody>tr');
            active_ids=[];
            $.each(rows, function () {
                $row = $(this);
                if ($row.attr('data-id')){
                    checked = $row.find('td input[type=checkbox]')[0].checked;
                    if(checked){
                        active_ids.push($row.attr('data-id'));
                    }
                }
            });
            if(active_ids.length>0){
                new Model('hr.holidays').call('nianxiujia_jiesuan', [active_ids]).done(function(res){
                    return self.rpc("/web/action/load", {action_id: "hr_holidays.open_nianxiujiayue_all"}).then(function(result) {
                        result.views = [[result.view_id[0], "list"],[false,"form"]];
                        return self.do_action(result,{clear_breadcrumbs: true});
                    });
                })
            }
        }
    });
});
