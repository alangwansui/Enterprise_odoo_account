odoo.define('dtdream_home.user', function (require) {
"use strict";

var core = require('web.core');
var session = require('web.session');
var Widget = require('web.Widget');
var time_module = require('web.time');
var Model = require('web.Model');
var UserMenu = require('web.UserMenu');

var QWeb = core.qweb;

var Main = UserMenu.extend({
    template: 'dtdream_user_menu',
    on_menu_logout: function() {
        this.do_action('logout');
    },
});

return Main;

});