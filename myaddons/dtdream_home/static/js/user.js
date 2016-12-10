odoo.define('dtdream_home.user', function (require) {
"use strict";

var ActionManager = require('web.ActionManager');
var core = require('web.core');
var session = require('web.session');
var Widget = require('web.Widget');
var time_module = require('web.time');
var Model = require('web.Model');
var UserMenu = require('web.UserMenu');

var QWeb = core.qweb;

var Main = UserMenu.extend({
    template: 'dtdream_user_menu',
    init: function(){
        this._super();
        this.action_manager = new ActionManager(this, {user: this});
    },
    on_menu_logout: function() {
        this.do_action('logout');
    },
    on_menu_change_passwd: function() {

        var html = [
        '<div class=pw-box-body>',
            '<script src=/dtdream_home/static/js/passwd.js></script>',
//            '<form name=change_password_form method=POST>',
                '<div class=form-group>',
                    '<label for=old_pwd class=\'col-sm-3 control-label\'>旧密码</label>',
                    '<div class=col-sm-6><input type=password class=form-control id=old_pwd placeholder=旧密码></div>',
                '</div>',
                '<div class=form-group>',
                    '<label for=new_pwd class=\'col-sm-3 control-label\'>新密码</label>',
                    '<div class=col-sm-6><input type=password class=form-control id=new_pwd placeholder=新密码></div>',
                '</div>',
                '<div class=form-group>',
                    '<label for=confirm_password class=\'col-sm-3 control-label\'>确认新密码</label>',
                    '<div class=col-sm-6><input type=password class=form-control id=confirm_password placeholder=确认新密码></div>',
                '</div>',
                '<div class=form-group>',
                '<span class=\'error-text col-sm-offset-3 col-sm-9\'></span>',
                '</div>'
                ,
                '<div class=form-group>',
                    '<div class=col-sm-offset-3>',
                        '<button class=\'btn btn-default oe_form_button o_dtdream_home_reset_passwd\'>确认</button>',
                    '</div>',
                '</div>',
//            '</form>',
        '</div>'
        ].join('\n');

        layer.open({
          title: "重置域密码",
          type: 1,
          skin: 'layui-layer-rim', //加上边框
          area: ['480px', '334px'], //宽高
          content: html
        });
        var self = this;
        var $button = self.$el.find('.oe_form_button');
        $button.eq(0).click(function(){
          self.rpc("/web/session/change_password",{
               'fields': $("form[name=change_password_form]").serializeArray()
          }).done(function(result) {
               if (result.error) {
                  self.display_error(result);
                  return;
               } else {
                  self.do_action('logout');
               }
          });
       });
    },
//    on_menu_settings: function() {
//        var self = this;
//        return self.rpc("/web/action/load", { action_id: "base.action_res_users_my" }).then(function(result) {
//            result.res_id = session.uid;
//            self.do_action(result);
//            return result;
//        });
//    },
    do_action: function(action) {
        var self = this;
        return this.action_manager.do_action.apply(this, arguments);
    },
});

return Main;

});