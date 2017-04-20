odoo.define('dtdream_home.ui', function (require) {
"use strict";

var core = require('web.core');
var session = require('web.session');
var Widget = require('web.Widget');
var time_module = require('web.time');
var Model = require('web.Model');
var WebClient = require('web.WebClient');
var QWeb = core.qweb;

var Header = require('dtdream_home.header');
var Siderbar = require('dtdream_home.siderbar');
var Content = require('dtdream_home.content');
var WaterMark = require('dtdream_home.WaterMark');

var Main = Widget.extend({
        template: 'home',
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

            this.waterMark = new WaterMark();
            this.waterMark.start();
        },
        load_template: function () {
            var xml = $.ajax({
                url: "/dtdream_home/static/xml/templates.xml?version=01",
                async: false // necessary as without the template there isn't much to do.
            }).responseText;
            QWeb.add_template(xml);
        },
    });



return Main;

});
