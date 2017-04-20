odoo.define('dtdream_qua_man.ppt_export', function (require) {
//"use strict";

var core = require('web.core');
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
            if (self.fields_view.name=="view.dtdream.qua.man.tree"){
                var model1 = new Model('dtdream.qualification.management').call('if_in_hr_rz', []).done(function(res){
                    if (self.options.sidebar && res) {
                        var button = $("<button type='button' class='btn btn-primary btn-sm '>PPT批量导出</button>")
                        .click(self.proxy('ppt_order'));
                        if (document.getElementsByClassName('o_list_buttons').length !=0){
                            $(document.getElementsByClassName('o_list_buttons')).append(button)
                        }else{
                            $(document.getElementsByClassName('o_cp_buttons')).append(button)
                        }
                    };
                });
            }
        },
        ppt_order:function(){
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
                data={'active_ids':active_ids}
                $.ajax({
                    type: 'POST',
                    url: "/dtdream_qualification_management/ppt_export",
                    contentType: "application/json; charset=utf-8",
                    data: JSON.stringify(data),
                    dataType: "json",
                    success: function(data){
                        window.open("../dtdream_qualification_management/static/RZ_PPT.zip")
                    }
                    })

                return self.rpc("/web/action/load", {action_id: "dtdream_qualification_management.act_dtdream_qua_man_manager"}).then(function(result) {
                    result.views = [[result.view_id[0], "list"],[false,"form"]];
                    return self.do_action(result,{clear_breadcrumbs: true});
                });



//                    $.blockUI();
//                    self.session.get_file({
//                    url: '/dtdream_qualification_management/ppt_export',
//                    data:{active_ids: active_ids},
//                    complete: $.unblockUI,
//                });

            }else{
                alert("请选中数据")
            }
        }
    });
});
