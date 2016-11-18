odoo.define('dtdream_home.header', function (require) {
"use strict";

var core = require('web.core');
var session = require('web.session');
var Widget = require('web.Widget');
var time_module = require('web.time');
var Model = require('web.Model');
//var UserMenu = require('dtdream_home.user');
var UserMenu = require('web.UserMenu');

var WebClient = require('web.WebClient');
var QWeb = core.qweb;

var Main = Widget.extend({
        template: 'header',
        init: function (parent) {
            this._super(parent);
            this.load_template();
        },
        start: function () {
            var self = this;
//            return this._super.apply(this, arguments).then(function () {
//            });
        },
        load_data: function (parent) {
            var self = this;
            var $info = $(QWeb.render('header_info', {}));
            parent.$el.append($info);
            new UserMenu(self).appendTo($('.user-menu'));
        },
        attach: function (el, options) {

            if (options){
                this.user = options.user;
                this.uid = options.uid;
            }
            this.load_data(this, options);
        },
        detach: function () {
            this.$el.detach();
        },
        load_template: function () {
            var xml = $.ajax({
                url: "/web/static/src/xml/base.xml?version=01",
                async: false // necessary as without the template there isn't much to do.
            }).responseText;
            QWeb.add_template(xml);
            var common_xml = $.ajax({
                url: "/web/static/src/xml/base_common.xml?version=01",
                async: false // necessary as without the template there isn't much to do.
            }).responseText;
            QWeb.add_template(common_xml);
        },

    });



return Main;

});