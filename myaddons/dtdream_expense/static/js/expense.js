odoo.define('dtdream_expense.int_out_range', function (require) {
//"use strict";

var core = require('web.core');
var Model = require('web.Model');
var _t = core._t;
var FormView = require('web.FormView');
var ListView = require('web.ListView');
var Model = require('web.Model');
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

ListView.include({
        render_sidebar: function (arguments) {

            var self = this;
            if (!arguments[0]){
                arguments = [arguments];
            }
            this._super.apply(this, arguments);
            var model1 = new Model('dtdream.expense.report').call('if_in_jiekoukuaiji', []).done(function(res){
                if (self.options.sidebar && self.fields_view.model=='dtdream.expense.report' && res && self.fields_view.name=="dtdream.expense.jiekoukuaiji.export.tree.view") {
                self.sidebar.add_items('other', _.compact([
                { label: '数据导出', callback: self.dtdream_expense_export }
                ]));
            };
            });


        },

        dtdream_expense_export: function () {
             //Select the first list of the current (form) view
             //or assume the main view is a list view and use that
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
            $.blockUI();
            self.session.get_file({
                url: '/dtdream_expense/dtdream_expense_export',
                data:{data: active_ids},
                complete: $.unblockUI,

            });
            return self.rpc("/web/action/load", {action_id: "dtdream_expense.action_dtdream_expense_jiekoukuaiji_export"}).then(function(result) {
                result.views = [[result.view_id[0], "list"],[false,"form"]];
                return self.do_action(result,{clear_breadcrumbs: true});
            });

        }
    // function dtdream_expense_export end
    });


});
