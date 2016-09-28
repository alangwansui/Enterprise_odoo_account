//odoo.define('dtdream_grants', function (require) {
//"use strict";
//var View = require('web.View');
//var core = require('web.core');
//var common = require('web.form_common');
//var FormView = require('web.FormView');
//var Widget = require('web.Widget');
//var QWeb = core.qweb;
////var newview = FormView.extend({
////    //view_loading: function(r) {
////    //    this._super.apply(this, arguments);
////    //    console.log(123);
////    //}
////
////    //load_form: function(data) {
////    //    var self = this;
////    //    //this._super(data);
////    //    this._super.apply(this, arguments);
////    //    console.log(self);
////    //    console.log(self.$el.find(".o_form_field_number"));
////    //    }
////    //load_record:function(record){
////    //    this._super.apply(this, arguments);
////    //    console.log(123);
////    //}
////    //render_buttons: function($node){
////    //    this._super.apply(this, arguments);
////    //    console.log(123);
////    //}
////    //render_pager: function($node) {
////    //    this._super.apply(this, arguments);
////    //    console.log(123);
////    //}
////    //check_actual_mode: function(source, options) {
////    //    //if(this.get("actual_mode") === "view") {
////    //    //    this.$el.removeClass('oe_form_editable').addClass('oe_form_readonly');
////    //    //} else {
////    //    //    this.$el.removeClass('oe_form_readonly').addClass('oe_form_editable');
////    //    //    _.defer(_.bind(this.autofocus, this));
////    //    //}
////    //    this._super.apply(this, arguments);
////    //    console.log(123);
////    //}
////    //init: function(parent, dataset, view_id, options) {
////    //    this._super.apply(this, arguments);
////    //    console.log(123);
////    //}
////    //on_attach_callback: function() {
////    //    this._super.apply(this, arguments);
////    //    $('.o_form_field_number').keydown(function(){alert(123)})
////    //
////    //    console.log(123);
////    //},
////
////    //render_pager: function($node) {
////    //    this._super.apply(this, arguments);
////    //    var self =this;
////    //    this.$pager = $(QWeb.render("FormView.pager", {'widget': self}));
////    //}
////});
//var MyWidget = Widget.extend({
//    // QWeb template to use when rendering the object
//    template: "MyQWebTemplate",
//    events: {
//        // events binding example
//        'click .o_form_field_number': function(){
//            alert(123);
//        },
//    },
//});
//    var my_widget = new MyWidget(this);
//// Render and insert into DOM
//my_widget.appendTo(".o_form_field_number");
//
////core.view_registry.add('form', newview);
////return newview;
//})
//
////odoo.define('dtdream_grants', function (require) {
////    "use strict";
////    $(document).ready(function(){
////        console.log($(".o_form_field_number"));
////    })
////})

odoo.define('dtdream_grants.test', function (require) {
"use strict";

var core = require('web.core');
var Model = require('web.Model');
var _t = core._t;
var FormView = require('web.FormView');

FormView.include({
    events: _.defaults({
        'keyup input.int_cls': 'test_click',
    }, FormView.prototype.events),

    test_click: function(ev) {
        try{
            if (parseInt(document.activeElement.value.replace(",",""))>2147483647)
            {
                document.activeElement.value="";
                alert("整数类型字段值不能大于2147483647");
            }

        }
        catch (err){

        }


    },
});

});
