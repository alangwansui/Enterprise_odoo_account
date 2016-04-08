odoo.define('account_reports_followup.tour', function (require) {
'use strict';

var Tour = require('web.Tour');

Tour.register({
    id:   'account_followup_reports_widgets_2',
    name: "Tests the filters and other widgets for the followups with this module",
    mode: 'test',
    path: '/web#action=account_reports.action_account_followup_all',

    steps: [
        {
            title:      "wait web client",
            waitFor:    ".o_account_reports_page:contains(Epic Technologies)",
        },
        {
            title:      "click trust ball",
            waitFor:    ".o_account_reports_page:contains(Epic Technologies) i.oe-account_followup-trust",
        },
        {
            title:      "change trust",
            waitFor:    ".o_account_reports_page:contains(Epic Technologies) a[data-new-trust='good']",
        },
    ]
});
});
