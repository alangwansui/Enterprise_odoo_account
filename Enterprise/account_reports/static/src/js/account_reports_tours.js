odoo.define('account_reports.tour', function (require) {
'use strict';

var Tour = require('web.Tour');

Tour.register({
    id:   'account_reports_widgets',
    name: "Tests the filters and other widgets",
    mode: 'test',
    path: '/web#action=account_reports.action_account_report_pnl',

    steps: [
        {
            title:      "wait web client",
            waitFor:    ".breadcrumb",
        },
        {
            title:      "change date filter",
            element:    ".o_account_reports_date-filter > a"
        },
        {
            title:      "change date filter",
            element:    ".o_account_reports_one-filter[data-value='last_year'] > a"
        },
        {
            title:      "wait refresh",
            waitNot:    ".o_account_reports_date-filter.open",
            waitFor:    "tr[data-id='1'] span:contains(0.00)"
        },
        {
            title:      "change comparison filter",
            element:    ".o_account_reports_date-filter-cmp > a"
        },
        {
            title:      "change comparison filter",
            element:    ".o_account_reports_use-previous-period > a"
        },
        {
            title:      "change comparison filter",
            element:    '.o_account_reports_previous-period button',
            onload: function () {
                $('input[name="periods_number"]').val(3);
            },
        },
        {
            title:      "wait refresh",
            waitNot:    ".o_account_reports_date-filter-cmp.open",
            waitFor:    "th + th + th + th + th",
        },
        {
            title:      "click summary",
            element:    'input[name="summary"]'
        },
        {
            title:      "edit summary",
            element:    'textarea[name="summary"]',
            sampleText: 'v9 accounting reports are fabulous !'
        },
        {
            title:      "save summary",
            element:    '.o_account_reports_summary button'
        },
        {
            title:      "wait refresh",
            waitFor:    ".o_account_reports_saved_summary",
        },
/*        { // PDF printing can't be tested with phantomjs
            title:      "export pdf",
            element:    '.o_account-widget-pdf'
        },*/
        {
            title:      "export xls",
            element:    '.o_account-widget-xls'
        },
        {
            title:      "change bool filter",
            element:    ".o_account_reports_date-filter-bool > a"
        },
        {
            title:      "change bool filter",
            element:    '.o_account_reports_one-filter-bool[data-value="all_entries"]'
        },
        {
            title:      "wait refresh",
            waitNot:    ".o_account_reports_date-filter-bool.open",
        },
        {
            title:      "change date filter",
            element:    ".o_account_reports_date-filter > a"
        },
        {
            title:      "change date filter",
            element:    '.o_account_reports_one-filter[data-value="this_month"] > a'
        },
        {
            title:      "wait refresh",
            waitNot:    ".o_account_reports_date-filter.open",
        },
        {
            title:      "unfold",
            element:    '.o_account_reports_unfoldable'
        },
        {
            title:      "wait unfolding",
            waitFor:    'tr.account_id'
        },
        {
            title:      "dropdown",
            element:    'tr.account_id a[data-toggle="dropdown"]'
        },
        {
            title:      "footnote",
            waitFor:    'tr.account_id div.dropdown.open',
            element:    'tr.account_id .o_account_reports_add-footnote'
        },
        {
            title:      "footnote",
            element:    'textarea.o_account_reports_footnote_note',
            sampleText: 'You can even add footnotes !'
        },
        {
            title:      "save footnote",
            element:    'div.modal-footer > button.btn-primary'
        },
        {
            title:      "wait for footnote",
            waitFor:    'p.footnote'
        },
        {
            title:      "dropdown",
            element:    'tr.account_id a[data-toggle="dropdown"]'
        },
        {
            title:      "leave",
            waitFor:    'tr.account_id div.dropdown.open',
            element:    'tr.account_id .o_account_reports_web_action'
        },
    ]
});

Tour.register({
    id:   'account_followup_reports_widgets',
    name: "Tests the filters and other widgets for the followups",
    mode: 'test',
    path: '/web#action=account_reports.action_account_followup_all',

    steps: [
        {
            title:      "wait web client",
            waitFor:    ".o_account_reports_page:contains(Agrolait)",
        },
        {
            title:      "click excluded",
            element:    ".o_account_reports_page:contains(Best Designers) input[name='blocked']",
        },
        {
            title:      "change filter",
            element:    ".o_account_reports_followup-filter > a",
        },
        {
            title:      "change filter",
            element:    ".o_account_reports_one-filter[data-value='action'] > a",
        },
        {
            title:      "check change of both excluded and filter change", // The same filter is used as above just to refresh the page and see if best designers disappears as all lines are excluded
            waitNot:    ".o_account_reports_page:contains(Best Designers)",
        },
/*        { // PDF printing can't be tested with phantomjs
            title:      "print letter",
            element:    ".o_account_reports_page:contains(Agrolait) button.followup-letter",
        },*/
/*        { // Also prints pdf
            title:      "send email",
            element:    ".o_account_reports_page:contains(Agrolait) button.followup-email",
        },
        {
            title:      "check email",
            waitFor:    ".o_account_reports_page:contains(Agrolait) div.alert-info",
        },*/
        {
            title:      "click skip",
            element:    ".o_account_reports_page:contains(Agrolait) button.o_account_reports_followup_skip",
        },
        {
            title:      "check it disappeared",
            waitNot:    ".o_account_reports_page:contains(Agrolait)",
        },
        {
            title:      "change filter",
            element:    ".o_account_reports_followup-filter > a",
        },
        {
            title:      "change filter",
            element:    ".o_account_reports_one-filter[data-value='all'] > a",
        },
        {
            title:      "check Agrolait is back in after filter change",
            waitFor:    ".o_account_reports_page:contains(Agrolait)",
        },
    ]
});
});
