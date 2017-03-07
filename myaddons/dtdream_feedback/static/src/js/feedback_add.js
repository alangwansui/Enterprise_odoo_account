odoo.define('dtdream_feedback.dtdream_feedback_add_advice', function (require) {
"use strict";

var core = require('web.core');
var Model = require('web.DataModel');
var QWeb = core.qweb;
var _t = core._t;
var ListView = require('web.ListView');
var KanbanView = require('web_kanban.KanbanView')
var FormView = require('web.FormView');

FormView.include({
     events: _.defaults({
        'click .btn_confirm_refresh': 'refresh_feedback',
    }, FormView.prototype.events),

    refresh_feedback: function() {
    },
});

var FeedbackListView = ListView.extend({
    render_buttons: function ($node) {
        if (!this.$buttons) {
            this.$buttons = $(QWeb.render("FeedbackListView.buttons", {'widget': this}));

            this.$buttons.find('.oe_add_advice').click(this.proxy('add_advice_click'));

            $node = $node || this.options.$buttons;
            if ($node) {
                this.$buttons.appendTo($node);
            } else {
                this.$('.oe_list_buttons').replaceWith(this.$buttons);
            }
        }
    },

    add_advice_click: function (ev) {
        ev.preventDefault();
        ev.stopPropagation();

        var self = this;
        var $action = $(ev.currentTarget);
        var action_name = $action.attr('name');
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

var FeedbackKanban = KanbanView.extend({
    render_buttons: function ($node) {
        if (!this.$buttons) {
            this.$buttons = $(QWeb.render("FeedbackKanban.buttons", {'widget': this}));

            this.$buttons.find('.oe_add_advice').click(this.proxy('add_advice_click'));

            $node = $node || this.options.$buttons;
            if ($node) {
                this.$buttons.appendTo($node);
            } else {
                this.$('.o_cp_buttons').children('div').replaceWith(this.$buttons);
            }
        }
    },

    add_advice_click: function (ev) {
        ev.preventDefault();
        ev.stopPropagation();

        var self = this;
        var $action = $(ev.currentTarget);
        var action_name = $action.attr('name');
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

core.view_registry.add('tree_dtdream_feedback_advice', FeedbackListView);
core.view_registry.add('kanban_dtdream_feedback_advice', FeedbackKanban);

});
