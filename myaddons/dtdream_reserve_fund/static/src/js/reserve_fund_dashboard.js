/**
 * @class ReserveFundDashboard
 * @classdesc 备用金Dashboard
 */
odoo.define('dtdream_reserve_fund.ui.dashboard', function (require) {
    "use strict";

    var core = require('web.core');
    var formats = require('web.formats');
    var Model = require('web.Model');
    var session = require('web.session');
    var KanbanView = require('web_kanban.KanbanView');

    var QWeb = core.qweb;

    var _t = core._t;
    var _lt = core._lt;


    /**
     * @class ReserveFundReportDashboardView
     * @classdesc 备用金看板
     * @augments KanbanView
     */
    var ReserveFundReportDashboardView = KanbanView.extend({
        display_name: '备用金',

        icon: 'fa-dashboard',

        view_type: "reserve_fund_dashboard",

        searchview_hidden: true,

        events: {
            'click .panel': 'on_dashboard_action_clicked',
        },

        /**
         * @memberOf ReserveFundReportDashboardView
         * @description 从服务端获取数据
         * @returns {*|jQuery.Deferred}
         */
        fetch_data: function () {
            // Overwrite this function with useful data
            return new Model('dtdream.reserve.fund.dashboard')
                .call('retrieve_reserve_fund_dashboard', []);
        },
         /**
         * @memberOf ExpenseReportDashboardView
         * @description 显示看板视图内容
         * @returns {*|Promise|Promise.<TResult>}
         */
        render: function () {
            var super_render = this._super;
            var self = this;

            return this.fetch_data().then(function (result) {
                var report_dashboard = QWeb.render('dtdream_reserve_fund.ReserveFundReportDashboard', {
                    'receipts_is_draft': result.receipts_is_draft,
                    'receipts_approvaling_by_me': result.receipts_approvaling_by_me,
                    'receipts_approvaled_by_me': result.receipts_approvaled_by_me,
                    'receipts_not_off':result.receipts_not_off,
                    'receipts_out_time':result.receipts_out_time,
                });
                super_render.call(self);

                $(report_dashboard).prependTo(self.$el);
                self.$el.find('.oe_view_nocontent').hide();
            });
        },

        /**
         * @memberOf ReserveFundReportDashboardView
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

            new Model("ir.model.data")
                .call("xmlid_to_res_id", [action_name])
                .then(function (data) {
                    if (data) {
                        self.do_action(data, additional_context);
                    }
                });
        },
    });

    core.view_registry.add('reserve_fund_dashboard', ReserveFundReportDashboardView);

    return ReserveFundReportDashboardView

});
