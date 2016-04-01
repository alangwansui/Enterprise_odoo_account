odoo.define('account_reports_followup.FollowupReportWidget', function (require) {
'use strict';

var FollowupReportWidget = require('account_reports.FollowupReportWidget');
var Model = require('web.Model');
var account_report_followup_generic = require('account_reports.account_report_followup_generic');
var session = require('web.session');
var framework = require('web.framework');
var crash_manager = require('web.crash_manager');

account_report_followup_generic.include({
    _prepare_html_fetching: function() {
        var self = this;
        return new Model('res.partner').call('get_partners_in_need_of_action_and_update').then(function (results) {
            self.partners_data = results;
            if (self.partner_done) {
                if (Object.keys(results).length === 0 && !self.followup_all) { // If no more partners, display the 'finished' screen (from the followup_all mode)
                    var report_context = {partner_done: self.partner_done, followup_all: true};
                    self.restart(report_context);
                }
                self.partner_id = Object.keys(results)[0];
                self.partners_number = Object.keys(results).length;
                return self._get_context();
            }
            else {
                return self._get_context();
            }
        });
    },
    _create_context: function() {
        var self = this;
        var create_vals = this.followup_all ? {valuemax: self.partners_number} : (self.partners_data[self.partner_id] ? {partner_id: self.partner_id, level: self.partners_data[self.partner_id][0]} : {partner_id: self.partner_id});
        return self.context_model.call('create', [create_vals]).then(function (result) { // Eventually, create the report
            self.context_id = result;
            return self._do_fetch_html();
        });
    },
});

FollowupReportWidget.include({
    events: _.defaults({
        'click .changeTrust': 'changeTrust',
        'click .followup-action': 'doManualAction',
    }, FollowupReportWidget.prototype.events),
    onKeyPress: function(e) {
        var self = this;
        var report_name = $("div.o_account_reports_page").data("report-name");
        if ((e.which === 13 || e.which === 10) && (e.ctrlKey || e.metaKey) && report_name === 'followup_report') {
            e.preventDefault();
            return new Model('account.report.context.followup.all').call('search', [[['create_uid', '=', session.uid]]]).then(function(result) {
                return new Model('account.report.context.followup.all').query(['partner_filter'])
                .filter([['id', '=', result[0]]]).first().then(function (result) {
                    if (result['partner_filter'] == 'action') {
                        var email_context_list = [];
                        self.$("*[data-primary='1'].followup-email").each(function() { // List all the followups where sending an email is needed
                            email_context_list.push($(this).data('context'));
                        });
                        var letter_partner_list = [];
                        self.$("*[data-primary='1'].followup-letter").each(function() {
                            letter_partner_list.push($(this).data('partner'));
                        });
                        var action_context_list = [];
                        self.$("*[data-primary='1'].followup-action").each(function() { // List all the followups where action is needed
                            action_context_list.push($(this).data('context'));
                        });
                        framework.blockUI();
                        var complete = function() {
                            framework.unblockUI();
                            var report_context = {partner_done: 'all', email_context_list: email_context_list, action_context_list: action_context_list}; // Restart the report giving the list for the emails and actions
                            self.getParent().restart(report_context);
                        }
                        session.get_file({
                            url: '/account_reports/followup_report/' + letter_partner_list + '/',
                            complete: complete,
                            error: crash_manager.rpc_error.bind(crash_manager),
                        });
                    }
                });
            })
        }
    },
    changeTrust: function(e) {
        var partner_id = $(e.target).parents('span.dropdown').data("partner");
        var newTrust = $(e.target).data("new-trust");
        if (!newTrust) {
            newTrust = $(e.target).parents('a.changeTrust').data("new-trust");
        }
        var color = 'grey';
        switch(newTrust) {
            case 'good':
                color = 'green';
                break;
            case 'bad':
                color = 'red';
                break;
        }
        return new Model('res.partner').call('write', [[parseInt(partner_id, 10)], {'trust': newTrust}]).then(function () {
            $(e.target).parents('span.dropdown').find('i.oe-account_followup-trust').attr('style', 'color: ' + color + '; font-size: 0.8em;');
        });
    },
    doManualAction: function(e) {
        e.stopPropagation();
        e.preventDefault();
        var context_id = $(e.target).parents("div.o_account_reports_page").data("context");
        return new Model('account.report.context.followup').call('do_manual_action', [[parseInt(context_id, 10)]]).then (function () {
            if ($(e.target).data('primary') === 1) {
                $(e.target).parents('#action-buttons').addClass('o_account_reports_followup_clicked');
                $(e.target).toggleClass('btn-primary btn-default');
                $(e.target).data('primary', '0');
            }
        });
    },
});
});
