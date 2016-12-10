odoo.define('dtdream_sale.web.GroupByMenu', function (require) {
"use strict";

var GroupByMenu = require('web.GroupByMenu');
var Widget = require('web.Widget');
var core = require('web.core');
var search_inputs = require('web.search_inputs');
var Model = require('web.DataModel');
var QWeb = core.qweb;
var FormView = require('web.FormView');
FormView.include({

    events: _.defaults({
        'click .opp_stage button': 'opp_stage_click',
        'click .btn btn-sm btn-primary' : 'change_stage_id'
    }, FormView.prototype.events),

    change_stage_id:function(){
        alert(1)
    },
    opp_stage_click: function(kwargs) {
        var self = this;
        var stage_name = window.event.target.innerHTML.trim();
        if (stage_name == "丢单"){
            alert('请点击左侧“丢单”按钮进行操作')
            return;
            return self.rpc("/web/action/load", {action_id: "crm.crm_lead_lost_action"}).then(function(result) {
                result.views = [[false,"form"]];
                result.context = self.dataset.context
                result.context.default_lead_id = self.datarecord.id
                return self.do_action(result);
            });
        }
        var other_stages = ["项目启动","技术和商务交流","项目招投标","机会点"]
        if (other_stages.includes(stage_name)){
            new Model('crm.lead').call('action_set_other_stage',[stage_name,self.datarecord.id]).then(function(result){
                self.reload()
            })
        }
        if (stage_name == "中标"){
            alert('请点击左侧“中标”按钮进行操作')
            return;
            new Model('crm.lead').call('crm_lead_won_action',[self.datarecord.id]).then(function(result) {
                result.views = [[result.view_id,"form"]];
                result.context = self.dataset.context
                self.do_action(result);
            })
        }
    },

})

return GroupByMenu.include({
    start: function () {
        var self = this;
        self._super.apply(this,arguments);
        var divider = this.$menu.find('.divider');
        this.fields_def.then(function () {
            if (this.data && JSON.parse(this.data).params.model == "crm.lead"){
                this.dtdream_sale = new Model('crm.lead');
                this.dtdream_sale.call('if_hide',[]).done(function (rec) {
                    if (rec){
                        self.$add_group.hide();
                        divider.hide();
                    }
                })
            }
        });
    },
});

});