
odoo.define('dtdream_demand_manage.ui.dashboard', function (require) {
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
    var applyData= [];
    var affairData= [];
    var doneData=[];


    var RemandDashboardView = KanbanView.extend({

        display_name: 'IT需求',

        icon: 'fa-dashboard',

        view_type: "remand_dashboard",

        searchview_hidden: true,

        events: {
            'click .panel': 'on_dashboard_action_clicked',
        },

        render: function () {
            var super_render = this._super;
            var self = this;
            var report_dashboard = QWeb.render('dtdream_demand_manage.RemandDashboardView', {});
            super_render.call(self);
            $(report_dashboard).prependTo(self.$el);
            self.$el.find('.oe_view_nocontent').hide();
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
            var additional_context = {'dashboard': true};

            /**
             *  打开菜单栏
             */
            new Model("ir.model.data")
                .call("xmlid_to_res_id", [action_name])
                .then(function (data) {
                    if (data) {
                        self.do_action(data, additional_context);
                    }
                });
         }

    });

    core.view_registry.add('remand_dashboard', RemandDashboardView);

    return RemandDashboardView

});
