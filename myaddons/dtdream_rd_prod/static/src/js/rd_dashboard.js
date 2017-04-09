
odoo.define('dtdream_rd_prod.ui.dashboard', function (require) {
    "use strict";

    var core = require('web.core');
    var formats = require('web.formats');
    var Model = require('web.Model');
    var session = require('web.session');
    var KanbanView = require('web_kanban.KanbanView');
    var form_common = require('web.form_common');

    var QWeb = core.qweb;

    var _t = core._t;
    var _lt = core._lt;
    var applyData= [];
    var affairData= [];
    var doneData=[];


    var RdDashboardView = KanbanView.extend({

        display_name: '研发',

        icon: 'fa-dashboard',

        view_type: "rd_dashboard",

        searchview_hidden: true,

        events: {
            'click .panel': 'on_dashboard_action_clicked',
            'click .next': 'on_next_click',
            'click .previous': 'on_next_click',
            'click .clickPage': 'on_btnPage_click'
        },

        fetch_data: function () {
            // Overwrite this function with useful data
            return new Model('dtdream.rd.dashboard')
                .call('retrieve_rd_dashboard', []);
        },

        render: function () {
            var super_render = this._super;
            var self = this;

            this.fetch_data().then(function (result) {
                var report_dashboard = QWeb.render('dtdream_rd_prod.RdDashboardView', {
                    "submit_product":result.submit_product,
                    "submit_version": result.submit_version,
                });
                super_render.call(self);

                $(report_dashboard).prependTo(self.$el);
                self.$el.find('.oe_view_nocontent').hide();
                self.render_affairs();
                self.render_applies();
                self.render_done();
                self.render_rd_slider_tab();
            });
        },
        render_affairs: function(){
            var affairs = [];
            var currentPage =1;
            var btnPage=[];
            new Model("dtdream.rd.dashboard")
            .call("get_all_affairs", [currentPage],{},null)
            .then(function (data) {
                if (data) {
                    affairData=data;
                    affairs=data['affairs'];
                    btnPage=_.range(1,data['totalPage']+1);
                }
                var $info = $(QWeb.render('dtdream_rd_prod.content_event_affairs', {
                    'affairs': affairs,
                    'totalNumber':affairs.length,
                    'btnPage':btnPage,
                    'totalPage':data['totalPage'],
                    'currentPage':data['currentPage'],
                    'nextPage':parseInt(data['currentPage'])+1,
                    'previousPage':parseInt(data['currentPage'])-1,
                }));
                $info.appendTo('.o_content_event_affairs');
                currentPage = 'affair_'+currentPage+'_'
                var all = $("tr[class*='affair_']")
                for (var i=0;i<all.length;i++){
                    if (all[i].className!=currentPage){
                        $(all[i]).hide()
                    }
                }
                if (parseInt(data['currentPage'])-1==0){
                    $(".previous[type='affairs']").addClass('disabled')
                }
                else{
                    $(".previous[type='affairs']").removeClass('disabled')
                }
                if (parseInt(data['currentPage'])+1>data['totalPage']){
                    $(".next[type='affairs']").addClass('disabled')
                }else{
                    $(".next[type='affairs']").removeClass('disabled')
                }
                /*if (affairs.length==0){
                    $('.o_content_event_affairs').hide()
                }*/
            })
        },
        render_applies: function(){
            var applies=[];
            var currentPage =1;
            var btnPage=[];
            new Model("dtdream.rd.dashboard")
            .call("get_all_applies", [currentPage],{},null)
            .then(function (data) {
                if (data) {
                    applyData =data;
                    applies=data['applies'];
                    btnPage=_.range(1,data['totalPage']+1);
                }
                var $info = $(QWeb.render('dtdream_rd_prod.content_event_applies', {
                    'applies': applies,
                    'totalNumber':applies.length,
                    'btnPage':btnPage,
                    'totalPage':data['totalPage'],
                    'currentPage':data['currentPage'],
                    'nextPage':parseInt(data['currentPage'])+1,
                    'previousPage':parseInt(data['currentPage'])-1,
                }));
                $info.appendTo('.o_content_event_applies');
                currentPage = 'apply_'+currentPage+'_'
                var all = $("tr[class*='apply_']")
                for (var i=0;i<all.length;i++){
                    if (all[i].className!=currentPage){
                        $(all[i]).hide()
                    }
                }
                if (parseInt(data['currentPage'])-1==0){
                    $(".previous[type='applies']").addClass('disabled')
                }
                else{
                    $(".previous[type='applies']").removeClass('disabled')
                }
                if (parseInt(data['currentPage'])+1>data['totalPage']){
                    $(".next[type='applies']").addClass('disabled')
                }else{
                    $(".next[type='applies']").removeClass('disabled')
                }
                /*if (applies.length==0){
                    $('.o_content_event_applies').hide()
                }*/
            })
        },
        render_done: function(){
            var affairs = [];
            var currentPage =1;
            var btnPage=[];
            new Model("dtdream.rd.dashboard")
            .call("get_all_dones", [currentPage],{},null)
            .then(function (data) {
                if (data) {
                    doneData=data;
                    affairs=data['dones'];
                    btnPage=_.range(1,data['totalPage']+1);
                }
                var $info = $(QWeb.render('dtdream_rd_prod.content_event_dones', {
                    'dones': affairs,
                    'totalNumber':affairs.length,
                    'btnPage':btnPage,
                    'totalPage':data['totalPage'],
                    'currentPage':data['currentPage'],
                    'nextPage':parseInt(data['currentPage'])+1,
                    'previousPage':parseInt(data['currentPage'])-1,
                }));
                $info.appendTo('.o_content_event_dones');
                currentPage = 'done_'+currentPage+'_'
                var all = $("tr[class*='done_']")
                for (var i=0;i<all.length;i++){
                    if (all[i].className!=currentPage){
                        $(all[i]).hide()
                    }
                }
                if (parseInt(data['currentPage'])-1==0){
                    $(".previous[type='dones']").addClass('disabled')
                }
                else{
                    $(".previous[type='dones']").removeClass('disabled')
                }
                if (parseInt(data['currentPage'])+1>data['totalPage']){
                    $(".next[type='dones']").addClass('disabled')
                }else{
                    $(".next[type='dones']").removeClass('disabled')
                }
                /*if (affairs.length==0){
                    $('.o_content_event_dones').hide()
                }*/
            })
        },
        render_rd_slider_tab: function(){
            if($("#rd_sliderSelectOptions li.active a").html() == "待我审批流程"){
                $('#rd_sliderSelectOptions .inline').css({'width':'155px','left':0});
            }
            $("#rd_sliderSelectOptions").on("mouseenter","li.slider_li",function(){
                if(!$(this).hasClass('active')){
                    $(this).addClass("active").siblings(".active").removeClass("active");
                }
                var movedistance=($(this).index())*155;
                $('#rd_sliderSelectOptions .inline').css({'width':'155px','left':movedistance});

                var sliderEvent=$(this).data('index')+"_events";
                if(!$("#"+sliderEvent).hasClass("active")){
                    $("#"+sliderEvent).addClass("active").addClass("in").siblings(".active").removeClass("active").removeClass("in");
                }
            });
        },
        /**
         * @description 跳转界面
         * @param ev
         */
        on_dashboard_action_clicked: function (ev) {
            ev.preventDefault();
            ev.stopPropagation();

            var self = this;
            var $action = $(ev.currentTarget);
            var action_name = $action.attr('name');
            var action_extra = $action.data('extra');
            var additional_context = {'dashboard': true};


            /**
             *  打开菜单栏
             */

            new Model("ir.model.data")
                .call("xmlid_to_res_id", [action_name])
                .then(function (data) {
                    if (data) {
                        self.do_action(data, additional_context);
                    }
                });

            /**
             *  打开单条记录
             */
            //return self.rpc("/web/action/load", {action_id: "dtdream_rd_prod.act_dtdream_prod_appr"}).then(function(result) {
            //    result.views = [[false, "form"], [false, "list"]];
            //    result.res_id=23
            //    return self.do_action(result);
            //});


            /**
             *  弹出框
             */

            //var pop = new form_common.FormViewDialog(self, {
            //           'type': 'ir.actions.act_window',
            //            'view_type': 'form',
            //            'view_mode': 'form',
            //            'res_model': 'dtdream_prod_appr',
            //            'res_id': 23,
            //            'context':'',
            //        }).open();


        },
        on_next_click:function(ev){
            if($(ev.currentTarget).hasClass('disabled')) return true
            var currentPage=$(ev.currentTarget).attr('value')
            if ($(ev.currentTarget).attr('type')=='affairs'){
                $('.o_content_event_affairs').html('');
                var affair_btnPage=[];
                affair_btnPage=_.range(1,affairData['totalPage']+1);
                var $info = $(QWeb.render('dtdream_rd_prod.content_event_affairs', {
                    'affairs': affairData['affairs'],
                    'totalNumber':affairData['affairs'].length,
                    'btnPage':affair_btnPage,
                    'totalPage':affairData['totalPage'],
                    'currentPage':currentPage,
                    'nextPage':parseInt(currentPage)+1,
                    'previousPage':parseInt(currentPage)-1,
                }));
                $info.appendTo('.o_content_event_affairs');
                var affair_currentPage = 'affair_'+currentPage+'_'
                var all = $("tr[class*='affair_']")
                for (var i=0;i<all.length;i++){
                    if (all[i].className!=affair_currentPage){
                        $(all[i]).hide()
                    }
                }
                if (parseInt(currentPage)-1==0){
                    $(".previous[type='affairs']").addClass('disabled')
                }
                else{
                    $(".previous[type='affairs']").removeClass('disabled')
                }
                if (parseInt(currentPage)+1>affairData['totalPage']){
                    $(".next[type='affairs']").addClass('disabled')
                }else{
                    $(".next[type='affairs']").removeClass('disabled')
                }
            }
            else if ($(ev.currentTarget).attr('type')=='applies'){
                $('.o_content_event_applies').html('');
                var apply_btnPage=[];
                apply_btnPage=_.range(1,applyData['totalPage']+1);
                var $info = $(QWeb.render('dtdream_rd_prod.content_event_applies', {
                    'applies': applyData['applies'],
                    'totalNumber':applyData['applies'].length,
                    'btnPage':apply_btnPage,
                    'totalPage':applyData['totalPage'],
                    'currentPage':currentPage,
                    'nextPage':parseInt(currentPage)+1,
                    'previousPage':parseInt(currentPage)-1,
                }));
                $info.appendTo('.o_content_event_applies');
                var apply_currentPage = 'apply_'+currentPage+'_'
                var all = $("tr[class*='apply_']")
                for (var i=0;i<all.length;i++){
                    if (all[i].className!=apply_currentPage){
                        $(all[i]).hide()
                    }
                }
                if (parseInt(currentPage)-1==0){
                    $(".previous[type='applies']").addClass('disabled')
                }
                else{
                    $(".previous[type='applies']").removeClass('disabled')
                }
                if (parseInt(currentPage)+1>applyData['totalPage']){
                    $(".next[type='applies']").addClass('disabled')
                }else{
                    $(".next[type='applies']").removeClass('disabled')
                }
            }
            else{
                $('.o_content_event_dones').html('');
                var done_btnPage=[];
                done_btnPage=_.range(1,doneData['totalPage']+1);
                var $info = $(QWeb.render('dtdream_rd_prod.content_event_dones', {
                    'dones': doneData['dones'],
                    'totalNumber':doneData['dones'].length,
                    'btnPage':done_btnPage,
                    'totalPage':doneData['totalPage'],
                    'currentPage':currentPage,
                    'nextPage':parseInt(currentPage)+1,
                    'previousPage':parseInt(currentPage)-1,
                }));
                $info.appendTo('.o_content_event_dones');
                var apply_currentPage = 'done_'+currentPage+'_'
                var all = $("tr[class*='done_']")
                for (var i=0;i<all.length;i++){
                    if (all[i].className!=apply_currentPage){
                        $(all[i]).hide()
                    }
                }
                if (parseInt(currentPage)-1==0){
                    $(".previous[type='dones']").addClass('disabled')
                }
                else{
                    $(".previous[type='dones']").removeClass('disabled')
                }
                if (parseInt(currentPage)+1>doneData['totalPage']){
                    $(".next[type='dones']").addClass('disabled')
                }else{
                    $(".next[type='dones']").removeClass('disabled')
                }
            }
        },
        on_btnPage_click: function(ev){
            var currentPage=$(ev.currentTarget).data('index');
            if ($(ev.currentTarget).attr('type')=='affairs'){
                $('.o_content_event_affairs').html('');
                var affair_btnPage=[];
                affair_btnPage=_.range(1,affairData['totalPage']+1);
                var $info = $(QWeb.render('dtdream_rd_prod.content_event_affairs', {
                    'affairs': affairData['affairs'],
                    'totalNumber':affairData['affairs'].length,
                    'btnPage':affair_btnPage,
                    'totalPage':affairData['totalPage'],
                    'currentPage':currentPage,
                    'nextPage':parseInt(currentPage)+1,
                    'previousPage':parseInt(currentPage)-1,
                }));
                $info.appendTo('.o_content_event_affairs');

                var affair_currentPage = 'affair_'+currentPage+'_'
                var all = $("tr[class*='affair_']")
                for (var i=0;i<all.length;i++){
                    if (all[i].className!=affair_currentPage){
                        $(all[i]).hide()
                    }
                }
                if (parseInt(currentPage)-1==0){
                    $(".previous[type='affairs']").addClass('disabled')
                }
                else{
                    $(".previous[type='affairs']").removeClass('disabled')
                }
                if (parseInt(currentPage)+1>affairData['totalPage']){
                    $(".next[type='affairs']").addClass('disabled')
                }else{
                    $(".next[type='affairs']").removeClass('disabled')
                }
            }
            else if ($(ev.currentTarget).attr('type')=='applies'){
                $('.o_content_event_applies').html('');
                var applies_btnPage=[];
                applies_btnPage=_.range(1,applyData['totalPage']+1);
                var $info = $(QWeb.render('dtdream_rd_prod.content_event_applies', {
                    'applies': applyData['applies'],
                    'totalNumber':applyData['applies'].length,
                    'btnPage':applies_btnPage,
                    'totalPage':applyData['totalPage'],
                    'currentPage':currentPage,
                    'nextPage':parseInt(currentPage)+1,
                    'previousPage':parseInt(currentPage)-1,
                }));
                $info.appendTo('.o_content_event_applies');
                var apply_currentPage = 'apply_'+currentPage+'_'
                var all = $("tr[class*='apply_']")
                for (var i=0;i<all.length;i++){
                    if (all[i].className!=apply_currentPage){
                        $(all[i]).hide()
                    }
                }
                if (parseInt(currentPage)-1==0){
                    $(".previous[type='applies']").addClass('disabled')
                }
                else{
                    $(".previous[type='applies']").removeClass('disabled')
                }
                if (parseInt(currentPage)+1>applyData['totalPage']){
                    $(".next[type='applies']").addClass('disabled')
                }else{
                    $(".next[type='applies']").removeClass('disabled')
                }
            }
            else{
                $('.o_content_event_dones').html('');
                var done_btnPage=[];
                done_btnPage=_.range(1,doneData['totalPage']+1);
                var $info = $(QWeb.render('dtdream_rd_prod.content_event_dones', {
                    'dones': doneData['dones'],
                    'totalNumber':doneData['dones'].length,
                    'btnPage':done_btnPage,
                    'totalPage':doneData['totalPage'],
                    'currentPage':currentPage,
                    'nextPage':parseInt(currentPage)+1,
                    'previousPage':parseInt(currentPage)-1,
                }));
                $info.appendTo('.o_content_event_dones');
                var apply_currentPage = 'done_'+currentPage+'_'
                var all = $("tr[class*='done_']")
                for (var i=0;i<all.length;i++){
                    if (all[i].className!=apply_currentPage){
                        $(all[i]).hide()
                    }
                }
                if (parseInt(currentPage)-1==0){
                    $(".previous[type='dones']").addClass('disabled')
                }
                else{
                    $(".previous[type='dones']").removeClass('disabled')
                }
                if (parseInt(currentPage)+1>doneData['totalPage']){
                    $(".next[type='dones']").addClass('disabled')
                }else{
                    $(".next[type='dones']").removeClass('disabled')
                }
            }
        }
    });

    core.view_registry.add('rd_dashboard', RdDashboardView);

    return RdDashboardView

});
