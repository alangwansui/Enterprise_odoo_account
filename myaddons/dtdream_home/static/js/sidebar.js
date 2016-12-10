odoo.define('dtdream_home.siderbar', function (require) {
"use strict";

var core = require('web.core');
var session = require('web.session');
var Widget = require('web.Widget');
var time_module = require('web.time');
var Model = require('web.Model');
var QWeb = core.qweb;

var Main = Widget.extend({
        template: 'sidebar',
        xls: {
        "销售":"sell",         "产品":"product",      "研发":"rd",         "外出公干":"out",
        "绩效":"performance",  "合同评审":"contract", "预算管理":"budget",  "专项审批":"special",
        "客户接待":"reception", "出差":"trip",        "费用报销":"expense", "IT需求管理":"it",
        "补助金管理":"subsidy", "开票":"account",     "人力资源":"hr",      "休假":"holiday",
        "应用":"app",          "设置":"settings",    "员工":"hr",          "公告":"notice",
        "电子名片":"ecard", "资产管理":"assets"},
        init: function (parent) {
//            this._super(parent);
        },
        start: function () {
            var self = this;
            return this._super.apply(this, arguments).then(function () {
            });
        },
        load_data: function (parent) {
            var self = this;

            var Menus = new Model('ir.ui.menu');
            Menus.call('load_menus', [core.debug], {context: session.user_context}).
                then( function(menu_data) {
                    // Compute action_id if not defined on a top menu item
                    var menus = []
                    for (var i = 0; i < menu_data.children.length; i++) {
                        var menu={url:"",　name:"",class:""};
                        var child = menu_data.children[i];
                        menu.name = child.name
                        if (self.xls[child.name]){
                            menu.class = "dodo doicon-"+self.xls[child.name];
                            menu.url = "/web#menu_id="+child.id;
                            //#menu_id=99&amp;action_id=96
                            if (child.action === false) {
                                while (child.children && child.children.length) {
                                    child = child.children[0];
                                    if (child.action) {
                                        menu.url = menu.url+"&action_id="+child.action.substring(child.action.indexOf(',')+1)
                                        menus.push(menu);
                                        break;
                                    }
                                }
                            } else if(child.action){
                                menu.url = menu.url+"&action_id="+child.action.substring(child.action.indexOf(',')+1)
                                menus.push(menu);
                            }
                        }
                    }
                    parent.render_data(menus, parent.$el);
                });
        },
        render_data: function (info, $el) {

            if (info) {
                var $info = $(QWeb.render('sidebar_info', {
                    'model_sets': info
                }));
                $el.append($info);
            }
        },
        attach: function (el, options) {
            this.load_data(this);
        },
        detach: function () {
            this.$el.detach();
        },

    });



return Main;

});