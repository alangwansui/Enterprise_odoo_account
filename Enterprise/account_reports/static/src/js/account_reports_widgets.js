odoo.define('account_reports.ReportWidget', function (require) {
'use strict';

var core = require('web.core');
var Widget = require('web.Widget');
var Model = require('web.Model');
var Dialog = require('web.Dialog');

var QWeb = core.qweb;

var ReportWidget = Widget.extend({
    events: {
        'click .fa-pencil-square': 'clickPencil',
        'click .fa-pencil': 'clickPencil',
        'click .o_account_reports_foldable': 'fold',
        'click .o_account_reports_unfoldable': 'unfold',
        'click .fa-trash-o': 'rmContent',
        'click .o_account_reports_saved_summary > span': 'editSummary',
        "click input[name='summary']": 'onClickSummary',
        "click button.saveSummary": 'saveSummary',
        'click button.saveContent': 'saveContent',
        'click .o_account_reports_add-footnote': 'footnoteFromDropdown',
        'click .o_account_reports_web_action': 'outboundLink',
        'click .o_account_reports_footnote_sup': 'goToFootNote',
    },
    init: function(parent, context, context_model, odoo_context) {
        this.context = context;
        this.context_model = context_model;
        this.odoo_context = odoo_context;
        this._super.apply(this, arguments);
    },
    start: function() {
        QWeb.add_template("/account_reports/static/src/xml/account_report_financial_line.xml");
        this.$('[data-toggle="tooltip"]').tooltip(); // start the tooltip widget
        var res = this._super.apply(this, arguments);
        core.bus.on("keydown", this, this.onKeyPress); // Bind key press to the right function
        return res;
    },
    update_context: function(update) {
        $.extend(this.context, update)
    },
    // Used to trigger actions
    outboundLink: function(e) {
        var self = this;
        var action_id = $(e.target).data('action-id');
        var action_name = $(e.target).data('action-name');
        var active_id = $(e.target).data('active-id');
        var res_model = $(e.target).data('res-model');
        var action_domain = $(e.target).data('action-domain');
        var force_context = $(e.target).data('force-context');
        var additional_context = {};
        if (active_id) { 
            additional_context = {active_id: active_id};
        }
        if (res_model && active_id) { // Open the view form of the given model
            return this.do_action({
                type: 'ir.actions.act_window',
                res_model: res_model,
                res_id: active_id,
                views: [[false, 'form']],
                target: 'current'
            });
        }
        if (res_model && action_domain) {
            return this.do_action({
                type: 'ir.actions.act_window',
                name: action_name ? action_name : '',
                res_model: res_model,
                domain: action_domain,
                views: [[false, 'list']],
            });
        }
        if (!_.isUndefined(force_context)) {
            var context = {
                date_filter: this.context.date_filter,
                date_filter_cmp: this.context.date_filter_cmp,
                date_from: self.report_type !== 'no_date_range' ? this.context.date_from : 'none',
                date_to: this.context.date_to,
                periods_number: this.context.periods_number,
                date_from_cmp: this.context.date_from_cmp,
                date_to_cmp: this.context.date_to_cmp,
                cash_basis: this.context.cash_basis,
                all_entries: this.context.all_entries,
                company_ids: this.context.company_ids,
            };
            additional_context.context = context;
            additional_context.force_context = true;
        }
        if (action_name && !action_id) { // If an action name is given, resolve it then do_action
            var dataModel = new Model('ir.model.data');
            var res = action_name.split('.');
            return dataModel.call('get_object_reference', [res[0], res[1]]).then(function (result) {
                return self.do_action(result[1], {additional_context: additional_context});
            });
        }
        return this.do_action(action_id, {additional_context: additional_context});
    },
    onKeyPress: function(e) {
        if ((e.which === 70) && (e.ctrlKey || e.metaKey) && e.shiftKey) { // Fold all
            this.$(".o_account_reports_foldable").trigger('click');
        }
        else if ((e.which === 229) && (e.ctrlKey || e.metaKey) && e.shiftKey) { // Unfold all
            this.$(".o_account_reports_unfoldable").trigger('click');
        }
    },
    // Changes the placeholder into an editable textarea and give it the focus
    onClickSummary: function(e) {
        e.stopPropagation();
        $(e.target).parents("div.o_account_reports_summary").html(QWeb.render("editSummary"));
        this.$("textarea[name='summary']").focus();
    },
    // When the user is done editing the summary
    saveSummary: function(e) {
        e.stopPropagation();
        e.preventDefault();
        var context_id = $(e.target).parents("div.o_account_reports_page").data("context");
        var summary = $(e.target).siblings("textarea[name='summary']").val().replace(/\r?\n/g, '<br />').replace(/\s+/g, ' ');
        if (summary) // If it isn't empty, display it normally
            $(e.target).parents("div.o_account_reports_summary").html(QWeb.render("savedSummary", {summary : summary}));
        else // If it's empty, delete the summary and display the default placeholder
            $(e.target).parents("div.o_account_reports_summary").html(QWeb.render("addSummary"));
        return this.context_model.call('edit_summary', [[parseInt(context_id, 10)], summary]);
    },
    // Displays the footnote modal
    footnoteFromDropdown: function(e) {
        e.stopPropagation();
        e.preventDefault();
        var self = this;
        var context_id = $(e.target).parents("div.o_account_reports_body").find('div.o_account_reports_page').data("context");
        var curFootNoteTarget = $(e.target).parents("div.dropdown").find("a:first"); // Save the current footnote target
        if(curFootNoteTarget.parents('div.dropdown').find('sup').length === 0) { // Make sure there's no footnote yet
            var type = $(e.target).parents('tr').data('type'); // Store the type, target_id and column in hidden fields
            var target_id = $(e.target).parents('tr').data('id');
            var column = $(e.target).parents('td').index();
            var $content = $(QWeb.render("footnoteForm", {target_id: target_id, type: type, column: column}));
            var save = function () {
                var note = $content.find(".o_account_reports_footnote_note").val().replace(/\r?\n/g, '<br />').replace(/\s+/g, ' '); // Get the note and strip off extra spaces and line returns
                return  self.context_model.call('get_next_footnote_number', [[parseInt(context_id, 10)]]).then(function (footNoteSeqNum) { // Get the next sequence number
                    curFootNoteTarget.after(QWeb.render("supFootNoteSeqNum", {footNoteSeqNum: footNoteSeqNum})); // Render the link to the footnote in the report
                    return self.context_model.query(['footnotes_manager_id']) // Store the footnote
                    .filter([['id', '=', context_id]]).first().then(function (context) {
                        new Model('account.report.footnotes.manager').call('add_footnote', [[parseInt(context.footnotes_manager_id[0], 10)], $content.find(".o_account_reports_footnote_type").val(), $content.find(".o_account_reports_footnote_target_id").val(), $content.find(".o_account_reports_footnote_column").val(), footNoteSeqNum, note]);
                        self.$("div.o_account_reports_page").append(QWeb.render("savedFootNote", {num: footNoteSeqNum, note: note})); // Render the footnote at the bottom
                    });
                });
            }
            new Dialog(this, {title: 'Annotate', size: 'medium', $content: $content, buttons: [{text: 'Save', classes: 'btn-primary', close: true, click: save}, {text: 'Cancel', close: true}]}).open();
        }
    },
    // When clicking on the summary, display a textarea to edit it.
    editSummary: function(e) {
        e.stopPropagation();
        e.preventDefault();
        var $el = $(e.target);
        var height = Math.max($el.height(), 100); // Compute the height that will be needed
        var text = $el.html().replace(/\s+/g, ' ').replace(/\r?\n/g, '').replace(/<br>/g, '\n').replace(/(\n\s*)+$/g, ''); // Remove unnecessary spaces and line returns
        var par = $el.parents("div.o_account_reports_summary");
        $el.parents("div.o_account_reports_summary").html(QWeb.render("editSummary", {summary: text})); // Render the textarea
        par.find("textarea").height(height); // Give it the right height
        this.$("textarea[name='summary']").focus(); // And the focus
    },
    clickPencil: function(e) {
        e.stopPropagation();
        e.preventDefault();
        if ($(e.target).parents("p.footnote").length > 0) { // If it's to edit a footnote at the bottom
            $(e.target).parents('.footnote').attr('class', 'o_account_reports_footnote_edit');
            var $el = $(e.target).parents('.o_account_reports_footnote_edit').find('span.text');
            var text = $el.html().replace(/\s+/g, ' ').replace(/\r?\n/g, '').replace(/<br>/g, '\n').replace(/(\n\s*)+$/g, ''); // Remove unnecessary spaces and line returns
            text = text.split('.'); // The text needs to be split into the number of the footnote and the actually content of the footnot
            var num = text[0];
            text = text[1];
            $el.html(QWeb.render("editContent", {num: num, text: text})); // Render the textarea to edit the footnote.
        }
    },
    saveContent: function(e) {
        e.stopPropagation();
        e.preventDefault();
        var context_id = $(e.target).parents("div.o_account_reports_page").data("context");
        var text = $(e.target).siblings('textarea').val().replace(/\r?\n/g, '<br />').replace(/\s+/g, ' '); // Remove unnecessary spaces and line returns
        var footNoteSeqNum = $(e.target).parents('p.o_account_reports_footnote_edit').text().split('.')[0];
        if ($(e.target).parents("p.o_account_reports_footnote_edit").length > 0) {
            $(e.target).parents("p.o_account_reports_footnote_edit").attr('class', 'footnote'); // Remove textarea and change back class name
            $(e.target).siblings('textarea').replaceWith(text);
            this.context_model.query(['footnotes_manager_id']) // And store the footnote
            .filter([['id', '=', context_id]]).first().then(function (context) {
                new Model('account.report.footnotes.manager').call('edit_footnote', [[parseInt(context.footnotes_manager_id[0], 10)], parseInt(footNoteSeqNum, 10), text]);
            });
        }
        $(e.target).remove();
    },
    rmContent: function(e) {
        e.stopPropagation();
        e.preventDefault();
        var num = $(e.target).parents('.footnote').text().split('.')[0].replace(/ /g,'').replace(/\r?\n/g,'');
        this.$("sup b a:contains('" + num + "')").parents('sup').remove(); // Remove the footnote number in the report
        $(e.target).parents('.footnote').remove();
        var context_id = window.$("div.o_account_reports_page").data("context");
        return this.context_model.query(['footnotes_manager_id']) // And delete the footnote
        .filter([['id', '=', context_id]]).first().then(function (context) {
            return new Model('account.report.footnotes.manager').call('remove_footnote', [[parseInt(context.footnotes_manager_id[0], 10)], parseInt(num, 10)]);
        });
    },
    fold: function(e) {
        e.stopPropagation();
        e.preventDefault();
        var context_id = $(e.target).parents("div.o_account_reports_page").data("context");
        var el;
        var $el;
        var $nextEls = $(e.target).parents('tr').nextAll(); // Get all the next lines
        for (el in $nextEls) { // While domain lines are found, keep hiding them. Stop when they aren't domain lines anymore
            $el = $($nextEls[el]).find("td span.o_account_reports_domain_line_1, td span.o_account_reports_domain_line_2, td span.o_account_reports_domain_line_3");
            if ($el.length === 0)
                break;
            else {
                $($el[0]).parents("tr").hide();
            }
        }
        var active_id = $(e.target).parents('tr').find('td.o_account_reports_foldable').data('id');
        $(e.target).parents('tr').toggleClass('o_account_reports_unfolded'); // Change the class, rendering, and remove line from model
        $(e.target).parents('tr').find('td.o_account_reports_foldable').attr('class', 'o_account_reports_unfoldable ' + active_id);
        $(e.target).parents('tr').find('span.o_account_reports_foldable').replaceWith(QWeb.render("unfoldable", {lineId: active_id}));
        return this.context_model.call('remove_line', [[parseInt(context_id, 10)], parseInt(active_id, 10)]);
    },
    unfold: function(e) {
        e.stopPropagation();
        e.preventDefault();
        var self = this;
        var report_name = window.$("div.o_account_reports_page").data("report-name");
        var context_id = window.$("div.o_account_reports_page").data("context");
        var active_id = $(e.target).parents('tr').find('td.o_account_reports_unfoldable').data('id');
        return this.context_model.call('add_line', [[parseInt(context_id, 10)], parseInt(active_id, 10)]).then(function () { // First add the line to the model
            var el;
            var $el;
            var $nextEls = $(e.target).parents('tr').nextAll();
            var isLoaded = false;
            for (el in $nextEls) { // Look at all the element
                $el = $($nextEls[el]).find("td span.o_account_reports_domain_line_1, td span.o_account_reports_domain_line_2, td span.o_account_reports_domain_line_3");
                if ($el.length === 0) // If you find an element that is not a domain line, break out
                    break;
                else { // If you find an domain line element, it means the element has already been loaded and you only need to show it.
                    $($el[0]).parents("tr").show();
                    isLoaded = true;
                }
            }
            if (!isLoaded) { // If the lines have not yet been loaded
                var $cursor = $(e.target).parents('tr');
                new Model('account.report.context.common').call('get_full_report_name_by_report_name', [report_name]).then(function (result) {
                    var reportObj = new Model(result);
                    var f = function (lines) {// After loading the line
                        self.context_model.call('get_columns_types', [[parseInt(context_id, 10)]]).then(function (types) {
                            var line;
                            lines.shift();
                            for (line in lines) { // Render each line
                                $cursor.after(QWeb.render("report_financial_line", {l: lines[line], types: types}));
                                $cursor = $cursor.next();
                            }
                        });
                    };
                    if (report_name === 'financial_report') { // Fetch the report_id first if needed
                        self.context_model.query(['report_id'])
                        .filter([['id', '=', context_id]]).first().then(function (context) {
                            reportObj.call('get_lines', [[parseInt(context.report_id[0], 10)], parseInt(context_id, 10), parseInt(active_id, 10)], {context : self.odoo_context}).then(f);
                        });
                    }
                    else {
                        reportObj.call('get_lines', [parseInt(context_id, 10), parseInt(active_id, 10)], {context : self.odoo_context}).then(f);
                    }
                });
            }
            $(e.target).parents('tr').toggleClass('o_account_reports_unfolded'); // Change the class, and rendering of the unfolded line
            $(e.target).parents('tr').find('td.o_account_reports_unfoldable').attr('class', 'o_account_reports_foldable ' + active_id);
            $(e.target).parents('tr').find('span.o_account_reports_unfoldable').replaceWith(QWeb.render("foldable", {lineId: active_id}));
        });
    },
    goToFootNote: function(e) {
        e.preventDefault();
        var elem = $(e.currentTarget).find('a').attr('href');
        this.trigger_up('scrollTo', {selector: elem});
    },
});

return ReportWidget;

});
