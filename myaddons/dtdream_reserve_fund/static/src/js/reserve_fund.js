/**
 * Created by 0569 on 2017/4/12.
 */
odoo.define('dtdream_reserve_fund.extra_function',function(require){
    //"use strict";


    var Model = require('web.Model')
    var ListView = require('web.ListView')
    var FormView = require('web.FormView')
    FormView.include({
        to_edit_mode: function() {
            this._super.apply(this, arguments);
            if (this.model.indexOf("dtdream.reserve.fund")>-1 && this.datarecord.id){
                this.do_onchange(this.fields['applicant'],this.fields['pay_to_who']);
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
            if (self.fields_view.name=="dtdream.reserve.interface.tree"){
                var model1 = new Model('dtdream.reserve.fund').call('if_in_jiekoukuaiji', []).done(function(res){
                    if (self.options.sidebar && res) {
                        self.sidebar.add_items('other', _.compact([
                            { label: '接口会计导出', callback: self.dtdream_reserve_export }
                        ]));
                    };
                });
            }

        },

        dtdream_reserve_export: function () {
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
                url: '/dtdream_reserve_fund/dtdream_reserve_export',
                data:{data: active_ids},
                complete: $.unblockUI,

            });
            return self.rpc("/web/action/load", {action_id: "dtdream_reserve_fund.action_interface_export"}).then(function(result) {
                result.views = [[result.view_id[0], "list"],[false,"form"]];
                return self.do_action(result,{clear_breadcrumbs: true});
            });

        }
    // function dtdream_reserve_export end
    });
})