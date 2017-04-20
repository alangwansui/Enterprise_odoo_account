odoo.define('dtdream_home.siderbar', function (require) {
"use strict";

var core = require('web.core');
var session = require('web.session');
var Widget = require('web.Widget');
var time_module = require('web.time');
var Model = require('web.Model');
var QWeb = core.qweb;

var apps = "";

var Main = Widget.extend({
        template: 'sidebar',
        events:{
            'click .panel': 'set_sidebar_effect',
            'keyup .on_app_search': 'search_app'
        },
        xls: {
            "销售":"sell",
            "产品":"product",
            "研发":"rd",
            "外出公干":"out",
            "绩效":"performance",
            "合同评审":"contract",
            "预算管理":"budget",
            "专项审批":"special",
            "客户接待":"reception",
            "出差":"trip",
            "费用报销":"expense",
            "IT需求管理":"it",
            "补助金管理":"subsidy",
            "开票":"account",
            "人力资源":"hr",
            "休假":"holiday",
            "应用":"app",
            "设置":"settings",
            "员工":"hr",
            "公告":"notice",
            "电子名片":"ecard",
            "资产管理":"assets",
			"信息安全":"security",
			"意见反馈":"feedback",
			"工资":"dtpay",
            "服务": "project_manage",
			"任职资格认证":"qualification",
            "采购":"purchase",
        },
//        模块类别配置--导航条分类--5类：公共应用(general)、销售(sell)、研发(RD)、服务(serve)、采购(chain)
        classify:{
            "销售":"sell",
            "研发":"RD",
            "采购":"chain",
            "服务": 'serve',
            "产品":"general",
            "合同评审":"general",
            "应用":"general",
            "设置":"general",
            "公告":"general",
            "电子名片":"general",
            "意见反馈":"general",
            "预算管理":"general",
            "专项审批":"general",
            "费用报销":"general",
            "资产管理":"general",
            "外出公干":"general",
            "绩效":"general",
            "出差":"general",
            "补助金管理":"general",
            "人力资源":"general",
            "休假":"general",
            "员工":"general",
            "工资":"general",
			"任职资格认证":"general",
            "客户接待":"general",
            "开票":"general",
            "酒店管理": "general",
            "餐饮管理": "general",
            "IT需求管理":"general",
            "信息安全":"general",
            "备用金管理":"general"
        },
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

                            if (child.name == "客户接待"){
                                for(var j=0; j < child.children.length; j++){
                                    if(child.children[j].name == '酒店餐饮管理'){
                                        for(var k=0; k < child.children[j].children.length; k++){
                                            var menu2={url:"",　name:"",class:""};
                                            menu2.name = child.children[j].children[k].name;
                                            var model_name;
                                            if (menu2.name == '酒店管理'){
                                                model_name = "dtdream.hotels.management";
                                            }else{
                                                model_name = "dtdream.dinner.management";
                                            }
                                            menu2.url = "/web#view_type=kanban&model=" + model_name + "&action=" + child.children[j].children[k].action.substring(child.children[j].children[k].action.indexOf(',')+1) + "&menu_id=" + child.id ;
                                            menu2.class = "dodo doicon-hotel-dinner";
                                            menus.push(menu2);
                                        }
                                    }
                                }
                            }

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
            var self=this;

            var general=[];
            var sell=[];
            var RD=[];
            var serve=[];
            var chain=[];

            if (info) {
                $.each(info,function(i,ele){
                    var search=self.classify[ele.name];
                    switch (search) {
                        case "general":
                            general.push(ele);
                            break;
                        case "sell":
                            sell.push(ele);
                            break;
                        case "RD":
                            RD.push(ele);
                            break;
                        case "serve":
                            serve.push(ele);
                            break;
                        case "chain":
                            chain.push(ele);
                            break;
                        default:
                            alert("孩砸，去前面代码看看模块类别配置对不对");
                            break;
                    }
                });
                console.log(info);
                var $info = $(QWeb.render('sidebar_info', {
                    'model_sets': info,
                    'general_sets':general,
                    'sell_sets':sell,
                    'RD_sets':RD,
                    'serve_sets':serve,
                    'chain_sets':chain,
                }));
                $el.append($info);
                apps = self.$el.find(".panel-body li");
            }
        },
        attach: function (el, options) {
            this.load_data(this);
//            this.search_app();
        },
        detach: function () {
            this.$el.detach();
        },
        set_sidebar_effect: function(e){
            var $target=$(e.target);
            if($target.data("toggle") == "collapse" || $target.hasClass("dodo")){
                if($target[0].nodeName.toLowerCase() == "a"){
                    var $span=$target.find("span");
                }else if($target[0].nodeName.toLowerCase() == "span"){
                    var $span=$target;
                }

                var $panel=$target.closest(".panel");
                var $expand=$panel.find(".panel-collapse");
                if(!$panel.hasClass("select")){
                    $panel.addClass("select").siblings(".select").removeClass("select");
                }
                if($expand.hasClass("in")){
                    if(!$span.hasClass("doicon-jiantouyou")){
                        $span.removeClass("doicon-jiantouxia").addClass("doicon-jiantouyou");
                    }
                }else{
                    if(!$span.hasClass("doicon-jiantouxia")){
                        $span.removeClass("doicon-jiantouyou").addClass("doicon-jiantouxia");
                        $panel.siblings(".panel").find(".doicon-jiantouxia").removeClass("doicon-jiantouxia").addClass("doicon-jiantouyou");
                    }
                }
            }
        },
        search_app: function(){
            var self = this;
            var current_value = self.$el.find(".on_app_search").val().trim();
            if(current_value == ""){
                $("#left-general").removeClass("in").attr("aria-expanded","false").closest(".panel").removeClass("select");
                self.$el.find(".panel-body li").css("background-color","transparent");
                return;
            }
            _.each(apps, function(ele){
                if(ele.innerText.trim().indexOf(current_value) != -1){
                    $("#left-general").addClass("in").attr("aria-expanded","true").closest(".panel").addClass("select");
                    ele.style.backgroundColor = "#d3dce6";
                    var move_distance = Math.ceil($(ele).offset().top);
                    $(".sidebar").scrollTop(move_distance-336);
                }
            });

        }
    });



return Main;

});