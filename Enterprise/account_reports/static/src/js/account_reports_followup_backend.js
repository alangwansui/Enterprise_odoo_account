odoo.define('account_reports.account_report_followup_generic', function (require) {
'use strict';

var core = require('web.core');
var Model = require('web.Model');
var Pager = require('web.Pager');
var FollowupReportWidget = require('account_reports.FollowupReportWidget');
var account_report_generic = require('account_reports.account_report_generic');

var QWeb = core.qweb;

// we specialise the basic account report backend blabla to handle the simple followup report.
var account_report_followup_generic = account_report_generic.extend({
    // Stores all the parameters of the action.
    init: function(parent, action) {
        this._super.apply(this, arguments);
        this.partner_done = action.context.partner_done ? parseInt(action.context.partner_done, 10) : false;
        this.partner_id = action.context.active_id;
        this.followup_all = action.context.followup_all;
        this.odoo_context = action.context;
        // set the pager if necessary
        if (this.followup_all && !this.given_context.page) {
            this.given_context.page = 1;
            this.page = 1;
        }
    },
    // Sets the html of the page, then creates a report widget and sets it on the page.
    set_html: function() {
        var self = this;
        var def = $.when();
        if (!this.followup_report_widget) {
            this.followup_report_widget = new FollowupReportWidget(this, this.report_context, new Model('account.report.context.followup'), this.odoo_context);
            def = this.followup_report_widget.appendTo(this.$el);
        }
        def.then(function () {
            self.followup_report_widget.$el.html(self.html);
        });
    },
    /* When the report has to be reloaded with a new context (the user has chosen new options).
       Fetches the html again with the new options then sets the report widget. */
    restart: function(given_context) {
        if (this.page) {
            given_context.page = this.page;
        }
        this._super.apply(this, arguments);
    },
    // Creates a new context
    _create_context: function() {
        var self = this;
        var create_vals = this.followup_all ? {valuemax: self.partners_number} : {partner_id: self.partner_id};
        return self.context_model.call('create', [create_vals]).then(function (result) {
            self.context_id = result;
            return self._do_fetch_html();
        });
    },
    // Does the actual rpc call to get the html
    _do_fetch_html: function() {
        var self = this;
        return self.context_model.call('get_html', [self.context_id, self.given_context], {context : self.odoo_context}).then(function (result) {
            self.html = result;
            return self.post_load();
        });
    },
    // Fetch the context_id or create one if none exist.
    // Look for a context with create_uid = current user (and with possibly a report_id)
    _get_context: function() {
        var self = this;
        var domain = [['create_uid', '=', self.session.uid]];
        if (!self.followup_all) {
            domain.push(['partner_id', '=', self.partner_id]);
        }
        return self.context_model.query(['id'])
        .filter(domain).first().then(function (result) {
            // If no context is found, create a new one
            if(!result) {
                return self._create_context();
            }
            else { // If the context was found, simply store its id
                self.context_id = result.id;
                return self._do_fetch_html();
            }
        });
    },
    _prepare_html_fetching: function() {
        var self = this;
        if (self.partner_done) { // If a partner has just been flagged 'done'
            return new Model('res.partner').call('get_partners_in_need_of_action').then(function (results) { // Get all the partners that require action
                if (results.length === 0 && !self.followup_all) { // If no more partners, display the 'finished' screen (from the followup_all mode)
                    var report_context = {partner_done: self.partner_done, followup_all: true};
                    self.restart(report_context); // Then restart the report
                }
                self.partner_id = results[0]; // Assign a new partner
                self.partners_number = results.length;
                return self._get_context();
            });
        }
        else {
            return self._get_context();
        }
    },
    // Fetches the html
    get_html: function() {
        var self = this;
        self.report_type = 'custom';
        if (this.followup_all) {
            self.context_model = new Model('account.report.context.followup.all');
        }
        else {
            self.context_model = new Model('account.report.context.followup');
        }
        return self._prepare_html_fetching();
    },
    // Once the html is loaded, fetches the context, the company_id, the fy, if there is xml export available and the company ids and names.
    post_load: function() {
        var self = this;
        if (this.followup_all) {
            var select = ['id', 'valuenow', 'valuemax', 'percentage', 'partner_filter', 'last_page'];
            return self.context_model.query(select)
            .filter([['id', '=', self.context_id]]).first().then(function (context) {
                self.report_context = context;
                self.render_searchview_buttons();
                self.render_searchview();
                self.render_pager();
                return self.update_cp();
            });
        }
        return self.update_cp();
    },
    render_buttons: function() {
        this.$buttons = '';
        return ''; // No buttons for followups
    },
    render_pager: function() {
        var self = this;
        if (this.followup_all) {
            var pager = new Pager(this, this.report_context.last_page, this.page, 1);
            pager.appendTo($('<div>')); // render the pager
            this.$pager = pager.$el;
            pager.on('pager_changed', this, function (state) {
                self.page = state.current_min;
                var report_context = {page: self.page}; // Create the context that will be given to the restart method
                self.restart(report_context); // Then restart the report
            });
        }
        return this.$pager;
    },
    render_searchview: function() {
        if (this.followup_all) { // Progressbar goes in the searchview area. Only when listing all the customer statements
            this.$searchview = $(QWeb.render("accountReports.followupProgressbar", {context: this.report_context}));
        }
        else {
            this.$searchview = '';
        }
        return this.$searchview;
    },
    render_searchview_buttons: function() {
        var self = this;
        if (this.followup_all) {
            this.$searchview_buttons = $(QWeb.render("accountReports.followupSearchView", {context: this.report_context}));
            this.$partnerFilter = this.$searchview_buttons.siblings('.o_account_reports_date-filter');
            this.$searchview_buttons.find('.o_account_reports_one-filter').bind('click', function (event) {
                var report_context = {partner_filter: $(event.target).parents('li').data('value')}; // Create the context that will be given to the restart method
                self.restart(report_context); // Then restart the report
            });
        }
        else {
            this.$searchview_buttons = '';
        }
        return this.$searchview_buttons;
    },
});
core.action_registry.add("account_report_followup_generic", account_report_followup_generic);
return account_report_followup_generic;
});
