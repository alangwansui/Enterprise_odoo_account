odoo.define('dtdream_sale_date_report.ui', function (require) {
"use strict";

var core = require('web.core');
var session = require('web.session');
var Widget = require('web.Widget');
var Model = require('web.Model');
var WebClient = require('web.WebClient');
var QWeb = core.qweb;

var Header = require('dtdream_home.header');
var Siderbar = require('dtdream_home.siderbar');
var Content = require('dtdream_home.content');


var Main = Widget.extend({
        template: 'dtdream_sale_data_report',
        init: function (parent) {
            var self = this;
            self._super(parent);
            self.load_template();
        },
        events: {
            /**主工具栏*/
//            'click .tab-item': 'on_open_item',
        },
        willStart: function () {
            var self = this;

            return session.session_reload().then(function () {
                self.user = session.username;
                self.uid = session.uid;
            });
        },
        start: function (parent) {
//            this._super(parent);
            var self = this;
            var option = {
                user: self.user,
                uid: self.uid
            }
            this.header = new Header(self);
            this.header.appendTo($('.o_main_header'));
            this.header.attach($('.o_main_header'), option);

            this.siderbar = new Siderbar(self);
            this.siderbar.appendTo($('.o_main_sidebar'))
            this.siderbar.attach($('.o_main_header'), option);

            this.content = new Content(self);
            this.content.appendTo($('.o_main_content'));
            this.content.attach($('.o_main_content'), option);
        },
        load_template: function () {
            var xml = $.ajax({
                url: "/dtdream_sale_data_report/views/templates.xml?version=01",
                async: false // necessary as without the template there isn't much to do.
            }).responseText;
            QWeb.add_template(xml);
        },
    });

core.view_registry.add('dtdream_sale_data_report', Main);

return Main;

});
