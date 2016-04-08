odoo.define('account_reports.FollowupReportWidget', function (require) {
'use strict';

var core = require('web.core');
var Model = require('web.Model');
var ReportWidget = require('account_reports.ReportWidget');
var datepicker = require('web.datepicker');
var Dialog = require('web.Dialog');
var session = require('web.session');
var framework = require('web.framework');
var crash_manager = require('web.crash_manager');

var QWeb = core.qweb;

var FollowupReportWidget = ReportWidget.extend({
    events: _.defaults({
        'click .change_exp_date': 'displayExpNoteModal',
        'click .followup-email': 'sendFollowupEmail',
        'click .followup-letter': 'printFollowupLetter',
        'click .o_account_reports_followup_skip': 'skipPartner',
        'click .o_account_reports_followup_done': 'donePartner',
        'click .o_account_reports_followup-auto': 'enableAuto',
        "change *[name='blocked']": 'onChangeBlocked',
        'click .o_account_reports_followup-set-next-action': 'setNextAction',
    }, ReportWidget.prototype.events),
    enableAuto: function(e) { // Auto mode is enabled -> Next action is computed automatically when clicking on 'Done'
        var target_id;
        var self = this;
        if ($(e.target).is('.btn-default')) { // If auto mode wasn't alreayd enabled
            target_id = $(e.target).parents("div.o_account_reports_page").data('context');
            // change which button is highlighted
            $(e.target).toggleClass('btn-default btn-info');
            $(e.target).siblings().toggleClass('btn-default btn-info');
            $(e.target).parents("div.o_account_reports_page").find('.o_account_reports_followup-no-action').remove(); // Remove the alert stating that auto mode is disabled
        }
        else if ($(e.target).is('div.alert a')) { // If auto mode is enabled from the alert
            target_id = $("div.o_account_reports_page").data('context');
            // change which button is highlighted
            this.$("div.o_account_reports_page").find('div#followup-mode .o_account_reports_followup-auto').addClass('btn-info');
            this.$("div.o_account_reports_page").find('div#followup-mode .o_account_reports_followup-auto').removeClass('btn-default');
            this.$("div.o_account_reports_page").find('div#followup-mode .o_account_reports_followup-manual').addClass('btn-default');
            this.$("div.o_account_reports_page").find('div#followup-mode .o_account_reports_followup-manual').removeClass('btn-info');
            $(e.target).parents('.o_account_reports_followup-no-action').remove(); // Remove the alert
        }
        return new Model('account.report.context.followup').call('to_auto', [[parseInt(target_id)]]).then(function () {self.getParent().restart({});}); // Go to auto python-side
    },
    // Opens the modal to select a next action
    setNextAction: function(e) {
        e.stopPropagation();
        e.preventDefault();
        if ($(e.target).is('.o_account_reports_followup-manual.btn-default')){ // If manual mode isn't enabled yet
            $(e.target).toggleClass('btn-default btn-info'); // Change the highlighted buttons
            $(e.target).siblings().toggleClass('btn-default btn-info');
        }

        // Get the target and store it in a hidden field
        var target_id = $(e.target).parents("div.o_account_reports_page").data('context');
        var $content = $(QWeb.render("nextActionForm", {target_id: target_id}));
        var nextActionDatePicker = new datepicker.DateWidget(this);
        nextActionDatePicker.appendTo($content.find('div.o_account_reports_next_action_date_picker'));
        nextActionDatePicker.set_value(new Date());

        var changeDate = function (e) {
            var dt = new Date();
            switch($(e.target).data('time')) { // Depending on which button is clicked, change the date accordingly
                case 'one-week':
                    dt.setDate(dt.getDate() + 7);
                    break;
                case 'two-weeks':
                    dt.setDate(dt.getDate() + 14);
                    break;
                case 'one-month':
                    dt.setMonth(dt.getMonth() + 1);
                    break;
                case 'two-months':
                    dt.setMonth(dt.getMonth() + 2);
                    break;
            }
            nextActionDatePicker.set_value(dt);
        }
        $content.find('.o_account_reports_followup_next_action_date_button').bind('click', changeDate);
        
        var save = function () {
            var note = $content.find(".o_account_reports_next_action_note").val().replace(/\r?\n/g, '<br />').replace(/\s+/g, ' ');
            var date = nextActionDatePicker.get_value();
            var target_id = $content.find("#target_id").val();
            return new Model('account.report.context.followup').call('change_next_action', [[parseInt(target_id)], date, note])
        }
        new Dialog(this, {size: 'medium', $content: $content, buttons: [{text: 'Save', classes: 'btn-primary', close: true, click: save}, {text: 'Cancel', close: true}]}).open();
    },
    onChangeBlocked: function(e) { // When clicking on the 'blocked' checkbox
        e.stopPropagation();
        e.preventDefault();
        var checkbox = $(e.target).is(":checked");
        var target_id = $(e.target).parents('tr').data('id');
        if (checkbox) { // If the checkbox was checked, change the line colour to gray else back to white
            $(e.target).parents('tr').attr('bgcolor', 'LightGray');
        }
        else {
            $(e.target).parents('tr').attr('bgcolor', 'white');
        }
        return new Model('account.move.line').call('write_blocked', [[parseInt(target_id)], checkbox]); // Write the change in db
    },
    onKeyPress: function(e) {
        var self = this;
        var report_name = $("div.o_account_reports_page").data("report-name");
        if ((e.which === 13 || e.which === 10) && (e.ctrlKey || e.metaKey) && report_name === 'followup_report') { // on ctrl-enter
            e.preventDefault();
            return new Model('account.report.context.followup.all').call('search', [[['create_uid', '=', session.uid]]]).then(function(result) {
                return new Model('account.report.context.followup.all').query(['partner_filter'])
                .filter([['id', '=', result[0]]]).first().then(function (result) {
                    if (result['partner_filter'] == 'action') {
                        var letter_partner_list = [];
                        var email_context_list = [];
                        self.$("*[data-primary='1'].followup-email").each(function() { // List all the followups where sending an email is needed
                            email_context_list.push($(this).data('context'));
                        });
                        self.$("*[data-primary='1'].followup-letter").each(function() { // List all the followups where printing a pdf is needed
                            letter_partner_list.push($(this).data('partner'));
                        });
                        framework.blockUI();
                        var complete = function() {
                            framework.unblockUI();
                            var report_context = {partner_done: 'all', email_context_list: email_context_list}; // Restart the report giving the list for the emails
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
    donePartner: function(e) {
        var partner_id = $(e.target).data("partner");
        var self = this;
        return new Model('res.partner').call('update_next_action', [[parseInt(partner_id)]]).then(function () { // Update in db and restart report
            var report_context = {partner_done: partner_id};
            self.getParent().restart(report_context);
        });
    },
    skipPartner: function(e) {
        var partner_id = $(e.target).data("partner");
        var report_context = {partner_skipped: partner_id}; // Restart the report with the skipped partner
        this.getParent().restart(report_context);
    },
    printFollowupLetter: function(e) {
        e.stopPropagation();
        e.preventDefault();
        var url = $(e.target).data("target");
        framework.blockUI();
        session.get_file({
            url: url,
            complete: framework.unblockUI,
            error: crash_manager.rpc_error.bind(crash_manager),
        });
        if ($(e.target).data('primary') === 1) { // If letter printing was required
            $(e.target).parents('#action-buttons').addClass('o_account_reports_followup_clicked'); // Change the class to show the done button
            $(e.target).toggleClass('btn-primary btn-default'); // change the class of the print letter button
            $(e.target).data('primary', '0');
        }
    },
    sendFollowupEmail: function(e) {
        e.stopPropagation();
        e.preventDefault();
        var context_id = $(e.target).parents("div.o_account_reports_page").attr("data-context");
        return new Model('account.report.context.followup').call('send_email', [[parseInt(context_id)]]).then (function (result) { // send the email server side
            if (result === true) {
                $(e.target).parents("div.o_account_reports_page").prepend(QWeb.render("emailSent")); // If all went well, notify the user
                if ($(e.target).data('primary') === 1) { // same as for letter printing
                    $(e.target).parents('#action-buttons').addClass('o_account_reports_followup_clicked');
                    $(e.target).toggleClass('btn-primary btn-default');
                    $(e.target).data('primary', '0');
                }
            }
            else {
                $(e.target).parents("div.o_account_reports_page").prepend(QWeb.render("emailNotSent")); // If something went wrong
            }
        });
    },
    displayExpNoteModal: function(e) {
        e.stopPropagation();
        e.preventDefault();
        var self = this;
        var target_id = $(e.target).parents('tr').data('id');
        var title = $(e.target).parents("div.dropdown").find("span.unreconciled_aml").text();
        var $content = $(QWeb.render("paymentDateForm", {target_id: target_id}));
        var paymentDatePicker = new datepicker.DateWidget(this);
        paymentDatePicker.appendTo($content.find('div.o_account_reports_payment_date_picker'));
        var save = function () {
            var note = $content.find("#internalNote").val().replace(/\r?\n/g, '<br />').replace(/\s+/g, ' ');
            var date = paymentDatePicker.get_value();
            return new Model('account.move.line').call('write', [[parseInt($content.find("#target_id").val())], {expected_pay_date: date, internal_note: note}]).then(function () {
                return self.getParent().restart({});
            });
        }
        new Dialog(this, {title: title, size: 'medium', $content: $content, buttons: [{text: 'Save', classes: 'btn-primary', close: true, click: save}, {text: 'Cancel', close: true}]}).open();
    },
    start: function() {
        var res = this._super();
        core.bus.on("keypress", this, this.onKeyPress);

        // Start the date pickers
        this.nextActionDatePicker = new datepicker.DateWidget(this);
        var res2 = this.nextActionDatePicker.appendTo(this.$('div.o_account_reports_next_action_date_picker'));

        return $.when(res, res2);
    },

});

return FollowupReportWidget;
});
