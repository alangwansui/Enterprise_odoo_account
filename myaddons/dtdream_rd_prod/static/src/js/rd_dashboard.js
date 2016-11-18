
odoo.define('dtdream_rd_prod.ui.dashboard', function (require) {
    "use strict";

    var core = require('web.core');
    var formats = require('web.formats');
    var Model = require('web.Model');
    var session = require('web.session');
    var KanbanView = require('web_kanban.KanbanView');
    var form_common = require('web.form_common');

    var QWeb = core.qweb;

    var _t = core._t;
    var _lt = core._lt;


    var RdDashboardView = KanbanView.extend({

        display_name: '研发',

        icon: 'fa-dashboard',

        view_type: "rd_dashboard",

        searchview_hidden: true,

        events: {
            'click .panel': 'on_dashboard_action_clicked',
        },

        fetch_data: function () {
            // Overwrite this function with useful data
            return new Model('dtdream.rd.dashboard')
                .call('retrieve_sales_dashboard', []);
        },

        render: function () {
            var super_render = this._super;
            var self = this;

            return this.fetch_data().then(function (result) {
                var report_dashboard = QWeb.render('dtdream_rd_prod.RdDashboardView', {

                    "submit_product":result.submit_product,
                    "wait_product":result.wait_product,
                    "my_product": result.my_product,

                    "submit_version": result.submit_version,
                    "wait_version": result.wait_version,
                    "my_version": result.my_version,

                    "submit_exception": result.submit_exception,
                    "wait_exception": result.wait_exception,
                    "my_exception": result.my_exception,

                    "submit_replanning": result.submit_replanning,
                    "wait_replanning": result.wait_replanning,
                    "my_replanning": result.my_replanning


                });
                super_render.call(self);

                $(report_dashboard).prependTo(self.$el);
                self.$el.find('.oe_view_nocontent').hide();
            });
        },
        /**
         * @description 跳转界面
         * @param ev
         */
        on_dashboard_action_clicked: function (ev) {
            ev.preventDefault();
            ev.stopPropagation();

            var self = this;
            var $action = $(ev.currentTarget);
            var action_name = $action.attr('name');
            var action_extra = $action.data('extra');
            var additional_context = {}


            /**
             *  打开菜单栏
             */

            new Model("ir.model.data")
                .call("xmlid_to_res_id", [action_name])
                .then(function (data) {
                    if (data) {
                        self.do_action(data);
                    }
                });

            /**
             *  打开单条记录
             */
            //return self.rpc("/web/action/load", {action_id: "dtdream_rd_prod.act_dtdream_prod_appr"}).then(function(result) {
            //    result.views = [[false, "form"], [false, "list"]];
            //    result.res_id=23
            //    return self.do_action(result);
            //});


            /**
             *  弹出框
             */

            //var pop = new form_common.FormViewDialog(self, {
            //           'type': 'ir.actions.act_window',
            //            'view_type': 'form',
            //            'view_mode': 'form',
            //            'res_model': 'dtdream_prod_appr',
            //            'res_id': 23,
            //            'context':'',
            //        }).open();


        },
    });

    core.view_registry.add('rd_dashboard', RdDashboardView);

    return RdDashboardView

});
