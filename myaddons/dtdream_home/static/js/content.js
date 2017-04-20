odoo.define('dtdream_home.content', function (require) {
"use strict";

var core = require('web.core');
var session = require('web.session');
var Widget = require('web.Widget');
var time_module = require('web.time');
var Model = require('web.Model');
var QWeb = core.qweb;
var applyData= [];
var affairData= [];

var affairs_length="";

var Main = Widget.extend({
        template: 'content',
        init: function (parent) {
        },
        start: function () {
            var self = this;
            return this._super.apply(this, arguments).then(function () {
            });
        },
        attach: function (el, options) {
            if (options){
                this.user = options.user;
                this.uid = options.uid;
            }

            this.related = new Related();
            this.related.appendTo($('.o_related'));
            this.related.attach($('.o_related'), options)

            this.content = new Content();
            this.content.appendTo($('.o_content'));
            this.content.attach($('.o_content'), options);
        },
        detach: function () {
            this.$el.detach();
        },
    });

var Related = Widget.extend({
    template: 'related',
    events:{
        'click .o_user_search_btn': 'search',
        'click .teasing':'teasing'
    },
    init: function (parent) {
        this._super(parent);
    },
    start: function () {
        var self = this;
        self._super(parent);
    },
    attach: function (el, options) {
        if (options){
            this.user = options.user;
            this.uid = options.uid;
        }
        this.render_related(el);
    },
    render_related:function(){
        var data = "";
        var $info = $(QWeb.render('related_info', {
            'data': data
        }));
        $info.appendTo('.o_related_info');
    },
    search:function(){
        $('.o_user_search').html('');
        var condition = [];
        var input_search_text=$('.o_input_text').val().trim();
        if(input_search_text == undefined ||　input_search_text == ""){
            return;
        }
        condition.push('|', '|', ['full_name', '=', input_search_text], ['nick_name', '=', input_search_text], ['job_number', '=', input_search_text]);
        new Model('hr.employee')
            .query(['full_name', 'nick_name', 'job_number', 'work_email', 'mobile_phone','department_id'])
            .filter(condition)
            .all({'timeout': 3000, 'shadow': true})
            .then(function (result) {
                var $info = $(QWeb.render('user_search', {
                'users': result,
                'result': result.length
                }));
                $info.appendTo('.o_user_search');
            });
    },
    teasing:function(ev){
        ev.preventDefault();
        ev.stopPropagation();

        var self = this;
        var $action = $(ev.currentTarget);
        var action_name = $action.attr('name');
        var action_extra = $action.data('extra');
        var additional_context = {'dashboard': true};

        var html=[
        '<div class=pw-box-body>',
                '<div class=\'form-group margin-layer\'>',
                    '<label for=feedback_user class=\'col-sm-3 control-label\'>用户</label>',
                    '<div class=col-sm-6><input type=text class=form-control id=feedback_user readonly></div>',
                '</div>',
                '<div class=\'form-group margin-layer\'>',
                    '<label for=feedbackPrmModels class=\'col-sm-3 control-label\'>问题模块</label>',
                    '<div class=col-sm-6>',
                        '<select id=feedbackPrmModels class=form-control  placeholder=问题模块>',
                            '<option disabled selected value=0>请选择</option>',
                        '</select>',
                    '</div>',
                '</div>',
                '<div class=\'form-group errorSelect margin-layer\'>',
                    '<div class=col-sm-offset-3>',
                        '<p>请选择问题模块！</p>',
                    '</div>',
                '</div>',
                '<div class=\'form-group margin-layer\'>',
                    '<label for=feedback_file class=\'col-sm-3 control-label\'>附件</label>',
                    '<div class=col-sm-3 style=\'height:34px;padding-left:0;\'>',
                        '<button type=button class=\'form-control feedback_file_btn\' id=feedback_file>上传附件</button>',
                        '<input type=file class=\'form-control feedback_file_input_btn\' style=\'display:block;\' id=feedback_file_input>',
                    '</div>',
                    '<div class=col-sm-3>',
                        '<input type=text class=\'form-control\' id=feedback_file_text style=\'display:none;\'>',
                    '</div>',
                '</div>',
                '<div class=\'form-group margin-layer\'>',
                    '<label for=feedbackAdvice class=\'col-sm-3 control-label\'>意见</label>',
                    '<div class=col-sm-6><textarea id=feedbackAdvice class=form-control rows=8 placeholder=\'请提出您的宝贵意见，以便我们改进，谢谢\'></textarea></div>',
                '</div>',
                '<div class=\'form-group errorAdvice margin-layer\'>',
                    '<div class=col-sm-offset-3>',
                        '<p>请填写意见！</p>',
                    '</div>',
                '</div>',
                '<div class=\'form-group margin-layer\'>',
                    '<div class=\'col-sm-offset-3 col-sm-1\' style=\'padding-left:0;\'>',
                        '<button class=\'btn btn-default feedbackBtn\'>提交</button>',
                    '</div>',
                    '<div class=col-sm-3>',
                        '<button class=\'btn btn-default feedbackCancelBtn\'>取消</button>',
                    '</div>',
                '</div>',
        '</div>'
        ].join('\n');
        layer.open({
          title: "意见反馈",
          type: 1,
          skin: 'layui-layer-rim', //加上边框
          area: ['980px', '560px'], //宽高
          content: html
        });

        var input_file_attachment="";
        $("#feedback_file_input").on('change',function(){

            var file=document.getElementById("feedback_file_input").files[0];
            var File_reader=new FileReader();
            File_reader.onload = function(upload){
                var data=upload.target.result;
                data = data.split(',')[1];
                input_file_attachment=data;
            };
            File_reader.readAsDataURL(file);

            var fileAll=$(this).val();
            var fileName="";
            if(fileAll.indexOf("\\") == 0){
                fileName=fileAll;
            }else{
                var fileArr=fileAll.split("\\");
                fileName=fileArr[fileArr.length-1];
            }
            $("#feedback_file_text").css("display","block");
            $("#feedback_file_text").val(fileName);
        });

        var feedback_userId=this.uid;
        var feedbackUser=this.user;

        $("#feedback_user").val(feedbackUser);
        $(".form-control[readonly]").css("background-color","#fff");
        new Model('dtdream.feedback.advice')
                    .call('get_feedbackmodels_record', [{}]).then(function(result){
                        var $html=$("#feedbackPrmModels").html();
                        $.each(result,function(i,ele){
                            $html+="<option value="+ele[0]+">"+ele[1]+"</option>"
                        });
                        $("#feedbackPrmModels").html($html);
                    });
        var $button = $(".feedbackBtn").on('click', function (e){
            var input_file="";
            var input_file_name="";
            console.log(input_file_attachment);
            if($("#feedback_file_input").val() == ""){
                input_file="";
                input_file_name="";
            }else{
                input_file=input_file_attachment;
                input_file_name=document.getElementById("feedback_file_input").files[0].name;
            }
            var data ={
                "adviceMan":feedback_userId,
                "promblemModels_name":$('#feedbackPrmModels').val(),
                "feedback_advice":$('#feedbackAdvice').val(),
                "attachment_name":input_file_name,
                "attachment":input_file
            }
            console.log(data);
            if(data.promblemModels_name == null){
                $('.errorSelect').css("display","block");
            }else if(data.feedback_advice == ""){
                $('.errorAdvice').css("display","block");
            }else{
                new Model('dtdream.feedback.advice')
                        .call('add_feedback', data).then(function(result){
                            console.log(result);
                            if(result){
                                $(".layui-layer-shade").remove();
                                $(".layui-layer").remove();
                            }else{
                                alert('数据传入失败！');
                            }
                        });
            }
        });
        var $cancelbutton=$(".feedbackCancelBtn").on('click',function(){
            $(".layui-layer-shade").remove();
            $(".layui-layer").remove();
        });
    }

});

var Content = Widget.extend({
    template: 'content_info',
    events: {
        'click .next': 'on_next_click',
        'click .previous': 'on_next_click',
    },
    init: function (parent) {
        this._super(parent);
    },
    start: function () {
        var self = this;
        self._super(parent);
    },
    attach: function (el, options) {
        if (options){
            this.user = options.user;
            this.uid = options.uid;
        }

        this.render_title();
        this.render_dashboard(this);
        /*this.render_notice();*/
        this.render_event();
        this.render_slider();
    },
    render_title: function(){
        var username = this.user;
        var $info = $(QWeb.render('content_title', {
            'username': username
        }));
        $info.appendTo('.o_content_title');
    },
    render_dashboard: function(parent){
        new Model('ir.ui.menu')
            .call('load_menus', [core.debug], {context: session.user_context}).then(function(menu_data) {
                var menus = menu_data.children;

                var check=[];
                var finacial=[];
                var performance=[];
                var general=[];

                _.each(menus,function(ele,i){
                    var item = {url:"", name:""};
                    item.name = ele.name;
                    if(ele.name == "休假" || ele.name == "外出公干" || ele.name == "出差"){
                        item.url = "/web#menu_id="+ele.id;
                        if(ele.action){
                            item.url = item.url+"&action_id="+ele.action.substring(ele.action.indexOf(',')+1)
                            check.push(item);
                        }else if(ele.action === false){
                            while (ele.children && ele.children.length) {
                                    ele = ele.children[0];
                                    if (ele.action) {
                                        item.url = item.url+"&action_id="+ele.action.substring(ele.action.indexOf(',')+1)
                                        check.push(item);
                                        break;
                                    }
                                }
                        }
                    }
                    if(ele.name == "费用报销" || ele.name == "工资" || ele.name == "资产管理" || ele.name =="补助金管理"){
                        item.url = "/web#menu_id="+ele.id;
                        if(ele.action){
                            item.url = item.url+"&action_id="+ele.action.substring(ele.action.indexOf(',')+1)
                            finacial.push(item);
                        }else if(ele.action === false){
                            while (ele.children && ele.children.length) {
                                    ele = ele.children[0];
                                    if (ele.action) {
                                        item.url = item.url+"&action_id="+ele.action.substring(ele.action.indexOf(',')+1)
                                        finacial.push(item);
                                        break;
                                    }
                                }
                        }
                    }
                    if(ele.name == "绩效" || ele.name == "任职资格认证"){
                        item.url = "/web#menu_id="+ele.id;
                        if(ele.action){
                            item.url = item.url+"&action_id="+ele.action.substring(ele.action.indexOf(',')+1)
                            performance.push(item);
                        }else if(ele.action === false){
                            while (ele.children && ele.children.length) {
                                    ele = ele.children[0];
                                    if (ele.action) {
                                        item.url = item.url+"&action_id="+ele.action.substring(ele.action.indexOf(',')+1)
                                        performance.push(item);
                                        break;
                                    }
                                }
                        }
                    }
                    if(ele.name == "信息安全" || ele.name == "IT需求管理"){
                        item.url = "/web#menu_id="+ele.id;
                        if(ele.action){
                            item.url = item.url+"&action_id="+ele.action.substring(ele.action.indexOf(',')+1)
                            general.push(item);
                        }else if(ele.action === false){
                            while (ele.children && ele.children.length) {
                                    ele = ele.children[0];
                                    if (ele.action) {
                                        item.url = item.url+"&action_id="+ele.action.substring(ele.action.indexOf(',')+1)
                                        general.push(item);
                                        break;
                                    }
                                }
                        }
                    }
                });

                var $info = $(QWeb.render('content_dashboard', {
                    "check_sets": check,
                    "finacial_sets": finacial,
                    "performance_sets": performance,
                    "general_sets": general
                }));
                $info.appendTo('.o_content_dashboard');
            });
        /*var data = {out:10, special:20, expense:30, my:50};
        new Model('dtdream_home.dtdream_home')
                .call('get_record_num', [{'user_id': this.uid}]).then(function (result) {
                data = result || data;
                var $info = $(QWeb.render('content_dashboard', {
                    'data': data
                }));
                $info.appendTo('.o_content_dashboard');
                new Model('dtdream_home.dtdream_home')
                    .call('get_month_record', [{'user_id': parent.uid}]).then(function(result){
                    console.log(result);
                    *//*parent.load_echarts(result.month, result.total, result.completed, result.grants);*//*
                })
            });*/
    },
    /*load_echarts:function(month, total, completed,grants){
            var firstchartid=echarts.init($("#firstchart")[0]); //显示区域的id
            var option1  =  {
                title:  {
                    text:  '近一年个人业务事项',
                    top:'10%',
                    left:'1%',
                    textStyle:{
                        fontSize:14,
                    }
                },
                color:['#65B6A8','#F06C73','#C191E9','#76C470','#82A4DE',  '#F7AF6A','#65B6A8'],

                tooltip:  {
                    trigger:  'axis'
                },
                legend:  {
                    data:['申请事项','完成事项'],
                    top:'10%',
                    right:'1%',
                },
                grid:  {
                    show:false,
                    width:'90%',
                     x:'5%',
                    y:'35%',
                    bottom:'15%',


                },
                xAxis:  {
                    type:  'category',
                    boundaryGap:  false,
                    data:  month,

                },
                yAxis:  {
                    type:  'value',
                    splitLine:{
                        show:true,
                        lineStyle:{
                            color:'#fff'
                        }
                    }
                },

                series:  [
                    {
                        name:'申请事项',
                        type:'line',
                        smooth:true,
                        areaStyle: {normal: {
                            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{
                                offset: 0, color: 'rgba(101,182,168,.9)' // 0% 处的颜色
                            }, {
                                offset: 1, color: 'rgba(101,182,168,0)' // 100% 处的颜色
                            }], false)

                        }},
                        data: total || [4,  5,  10,  35,  23,  11,  23,  5,  10,  35,  23,2]
                    },
                    {
                        name:'完成事项',
                        type:'line',
                        smooth:true,
                        areaStyle: {normal: {
                            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{
                                offset: 0, color: 'rgba(240,108,115,.9)' // 0% 处的颜色
                            }, {
                                offset: 1, color: 'rgba(240,108,115,0)' // 100% 处的颜色
                            }], false)

                        }},
                        data:completed || [1,12,  15,  9,  25,  23,  15,  24,  15,  0,  15,3]
                    }

                ]
            };
            firstchartid.setOption(option1);
            var relatechatsid=echarts.init($("#relatechats")[0]); //显示区域的id
            var option2  =  {
                tooltip:  {
                    trigger:  'item',
                },
                title:  {
                    text:  '补助金分配',
                    textStyle:{
                        color:'#4a4a4a',
                        fontSize:14,
                        fontWeight:'normal',
                    },
                    top:'8%',
                    left:'5%',
                },
                legend:  {
                    orient:  'vertical',
                    align:'left',
                    bottom:'10%',
                   data:[
                        {
                            name:'油卡',
                            icon:'pin',
                        },
                        {
                            name:'中大卡',
                            icon:'pin',
                        },
                        {
                            name:'工资',
                            icon:'pin',
                        },
                    ],

                    right:'30%',
                    textStyle:{
                        fontStyle:'normal',
                        fontSize:12,
                    },
                },
                grid:{

                },

                color:['#65B6A8','#76C470','#82A4DE', '#C191E9', '#F06C73', '#F7AF6A','#65B6A8'],
                series:  [
                    {
                        name:'访问来源',
                        type:'pie',
                        radius:  ['35%',  '65%'],
                        center: ['25%', '60%'],
                        avoidLabelOverlap:  false,

                        label:  {
                            normal:  {
                                show:  false,
                                position:  'center'
                            },
                            emphasis:  {
                                show:  true,
                                textStyle:  {
                                    fontSize:  '12',
                                    fontWeight:  'normal',
                                }
                            }
                        },
                        labelLine:  {
                            normal:  {
                                show:  false,
                            }
                        },
                        data:[
                            {value:grants.you,  name:'油卡'},
                            {value:grants.fan,  name:'中大卡'},
                            {value:grants.cash,  name:'工资'}
                        ]
                    }
                ]
            };
            relatechatsid.setOption(option2);
        },*/
    /*render_notice: function(){
        new Model('dtdream_notice.dtdream_notice')
            .query(['name', 'url', 'content'])
            .filter([['valid','=', true]])
            .all({'timeout': 3000, 'shadow': true})
            .then(function (result) {
                    if (result.length != 0){
                        $('.o_content_notice').html('');
                        var $info = $(QWeb.render('content_notice', {
                            'notices': result
                        }));
                        $info.appendTo('.o_content_notice');
                        $('.newsticker').newsticker();
                    }

                }
            );

        if (this.notices_time_hd == null || this.notices_time_hd == undefined){
            // 5min 执行一次
            this.notices_time_hd = setInterval(this.render_notice, 600*1000);
        }
    },*/
    render_event: function(){
        var $info = $(QWeb.render('content_event', {}));
        $info.appendTo('.o_content_event');
        this.render_affairs();
        this.render_applies();
    },
    render_affairs: function(){
        var self = this;

        var affairs = [];
        var currentPage =1
        var Menus = new Model('ir.ui.menu');
            Menus.call('load_menus', [core.debug], {context: session.user_context}).
                then( function(menu_data) {
                    new Model("dtdream.content.event.affairs")
//                    .call("get_all_affairs", [menu_data,currentPage],{},null)
                    .call("get_all_affairs", [menu_data],{},null)
                    .then(function (data) {
                        if (data) {
                            affairData=data;
                            affairs=data['affairs'];
                            affairs_length=affairs.length;
                        }
                        var $info = $(QWeb.render('content_event_affairs', {
                            'affairs': affairs,
//                            'afftotalPage':data['totalPage'],
//                            'affcurrentPage':data['currentPage'],
//                            'affnextPage':parseInt(data['currentPage'])+1,
//                            'affpreviousPage':parseInt(data['currentPage'])-1,
                        }));
                        $info.appendTo('.o_content_event_affairs');
                        console.log(affairs_length);
                        if(affairs_length == 0){
                            self.$el.find(".o_affairs_badge").css("display","none");
                        }else{
                            self.$el.find(".o_affairs_badge").text(affairs_length);
                        }
                        /*currentPage = 'affair_'+currentPage+'_'
                        var all = $("tr[class*='affair_']")
                        for (var i=0;i<all.length;i++){
                            if (all[i].className!=currentPage){
                                $(all[i]).hide()
                            }
                        }
                        if (parseInt(data['currentPage'])-1==0){
                            $("li.previous[type='affairs']").addClass('disabled')
                        }
                        else{
                            $("li.previous[type='affairs']").removeClass('disabled')
                        }
                        if (parseInt(data['currentPage'])+1>data['totalPage']){
                            $("li.next[type='affairs']").addClass('disabled')
                        }else{
                            $("li.next[type='affairs']").removeClass('disabled')
                        }*/
                    })
                });

    },
    render_applies: function(){
        var applies=[]
        var currentPage =1
        var Menus = new Model('ir.ui.menu');
            Menus.call('load_menus', [core.debug], {context: session.user_context}).
                then( function(menu_data) {
                    new Model("dtdream.content.event.affairs")
//                    .call("get_all_applies", [menu_data,currentPage],{},null)
                    .call("get_all_applies", [menu_data],{},null)
                    .then(function (data) {
                        if (data) {
                            applyData =data
                            applies=data['applies']
                        }
                        var $info = $(QWeb.render('content_event_applies', {
                            'applies': applies,
//                            'totalPage':data['totalPage'],
//                            'currentPage':data['currentPage'],
//                            'nextPage':parseInt(data['currentPage'])+1,
//                            'previousPage':parseInt(data['currentPage'])-1,
                        }));
                        $info.appendTo('.o_content_event_applies');
                        /*currentPage = 'apply_'+currentPage+'_'
                        var all = $("tr[class*='apply_']")
                        for (var i=0;i<all.length;i++){
                            if (all[i].className!=currentPage){
                                $(all[i]).hide()
                            }
                        }
                        if (parseInt(data['currentPage'])-1==0){
                            $("li.previous[type='applies']").addClass('disabled')
                        }
                        else{
                            $("li.previous[type='applies']").removeClass('disabled')
                        }
                        if (parseInt(data['currentPage'])+1>data['totalPage']){
                            $("li.next[type='applies']").addClass('disabled')
                        }else{
                            $("li.next[type='applies']").removeClass('disabled')
                        }*/
                    })
                });



    },
    destroy: function() {
        /*if (this.notices_time_hd){
            clearInterval(this.notices_time_hd);
            this.notices_time_hd=null;
        }*/
    },
    on_next_click:function(ev){
        if($(ev.currentTarget).hasClass('disabled')) return true
        var currentPage=$(ev.currentTarget).attr('value')
        if ($(ev.currentTarget).attr('type')=='affairs'){
            $('.o_content_event_affairs').html('')
            var $info = $(QWeb.render('content_event_affairs', {
                'affairs': affairData['affairs'],
                'afftotalPage':affairData['totalPage'],
                'affcurrentPage':currentPage,
                'affnextPage':parseInt(currentPage)+1,
                'affpreviousPage':parseInt(currentPage)-1,
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
                $("li.previous[type='affairs']").addClass('disabled')
            }
            else{
                $("li.previous[type='affairs']").removeClass('disabled')
            }
            if (parseInt(currentPage)+1>affairData['totalPage']){
                $("li.next[type='affairs']").addClass('disabled')
            }else{
                $("li.next[type='affairs']").removeClass('disabled')
            }
        }
        else{
            $('.o_content_event_applies').html('')
            var $info = $(QWeb.render('content_event_applies', {
                'applies': applyData['applies'],
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
                $("li.previous[type='applies']").addClass('disabled')
            }
            else{
                $("li.previous[type='applies']").removeClass('disabled')
            }
            if (parseInt(currentPage)+1>applyData['totalPage']){
                $("li.next[type='applies']").addClass('disabled')
            }else{
                $("li.next[type='applies']").removeClass('disabled')
            }
        }
    },
    render_slider: function(){
        if($("#sliderSelectOptions li.active a").text().trim() == "待我处理事项"){
            $('#sliderSelectOptions .inline').css('width','150px').css('left',0);
        }
        $("#sliderSelectOptions").on("mouseenter","li.slider_li",function(){
            if(!$(this).hasClass('active')){
                $(this).addClass("active").siblings(".active").removeClass("active");
            }
            var movedistance=($(this).index())*150;
            $('#sliderSelectOptions .inline').css('width','150px').css('left',movedistance);

            var sliderEvent=$(this).data('index')+"_events";
            if(!$("#"+sliderEvent).hasClass("active")){
                $("#"+sliderEvent).addClass("active").addClass("in").siblings(".active").removeClass("active").removeClass("in");
            }
        });
    }
});



return Main;

});