odoo.define('web.test.menu', function (require) {
"use strict";

var Tour = require('web.Tour');

Tour.register({
    id:   'test_menu',
    name: "Test all menu items",
    path: '/web',
    mode: 'test',
    steps: [
        {
            title:     "begin test",
            next:      "check",
        },

        // click all menu items
        {
            title:     "click on top menu",
            element:   '.o_application_switcher a[data-menu]:not([data-action-model="ir.actions.act_url"]):not(.already_tested):first',
            next:      "check",
            onload: function () {
                this.$current_app = $(this.element);
                console.log("Tour 'test_menu' click on App: '" +
                    this.$current_app.text().replace(/^\s+|\s+$/g, '') + "'");
            },
            onend: function () {
                this.$current_app.addClass('already_tested');
                $('.o_menu_sections .dropdown-menu').show();
            },
        },
        {
            title:     "click on sub menu",
            waitFor:   '.o_content',
            waitNot:   '.o_loading:visible',
            element:   '.o_menu_sections a:not(.dropdown-toggle):visible:not(.already_tested):first',
            next:      "check",
            onload: function () {
                console.log("Tour 'test_menu' click on Menu: '" +
                    $(this.element).find('span:first').text().replace(/^\s+|\s+$/g, '') + "'");
            },
            onend: function () {
                $(this.element).addClass('already_tested');
            },
        },
        {
            title:     "click on switch view",
            waitNot:   '.o_loading:visible',
            element:   '.o_cp_switch_buttons button:not(.already_tested):first',
            next:      "check",
            onload: function () {
                console.log("Tour 'test_menu' click on switch view: '" +
                    $(this.element).data('original-title') + "'");
            },
            onend: function () {
                $(this.element).addClass('already_tested');
            },
        },
        {
            title:     "back to app switcher",
            element:   '.o_menu_toggle',
            next:      "check",
            onend: function () {
                var remaining_apps_to_test = $('.o_application_switcher a[data-menu]:not([data-action-model="ir.actions.act_url"]):not(.already_tested)').length;
                if (remaining_apps_to_test === 0) {
                    return "finish";
                }
            },
        },
        {
            title:    "check",
            waitNot:  ".o_loading:visible",
        },
        {
            title:    "Select next action",
            onload: function () {
                if ($(".o_error_detail").size()) {
                    console.log("Error: Tour 'test_menu' has detected an error.");
                }
                if ($(".o_dialog_warning").size()) {
                    console.log("Warning: Tour 'test_menu' has detected a warning.");
                }

                $('.modal').modal('hide').remove();

                var steps = ["click on switch view", "click on sub menu", "click on top menu", "back to app switcher"];
                for (var k in steps) {
                    var step = Tour.search_step(steps[k]);
                    if ($(step.element).size()) {
                        return step.id;
                    }
                }
            },
        },

        // finish tour
        {
            title:     "finish",
        }
    ]
});

});
