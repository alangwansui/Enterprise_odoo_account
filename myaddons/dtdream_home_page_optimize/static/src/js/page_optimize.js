odoo.define('dtdream_home_page_optimize.home_page', function (require) {
    "use strict";

    var core = require('web.core');
    var Widget = require('web.Widget');
    var Model = require('web.Model');
    var AppSwitcher = require('web.AppSwitcher');
    var utils = require('web.utils');

    var home_page = Widget.extend({
        template: "home_page",
        events: {
            'click .o_action_app': 'on_app_clic',
        },

        //on_app_click: function (ev) {
        //    ev.preventDefault();
        //    this.trigger_up('app_clicked', {
        //        menu_id: $(ev.currentTarget).data('menu'),
        //        action_id: $(ev.currentTarget).data(
        // 'action-id'),
        //    });
        //},

        on_app_clic: function(ev){
         console.log(1111111111111111111111111111);
        }
    })

    return home_page;
})
//$(document).ready(function(){
//  $(".o_action_app").click(function(){
//       var self = this;
//        return self.rpc("/web/action/load", {action_id: "account.action_account_operation_template"}).then(function(result) {
//            result.views = [[false, "form"], [false, "list"]];
//            return self.do_action(result);
//        });;
//  });
//});

