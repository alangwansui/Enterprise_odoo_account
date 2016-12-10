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
        'click .o_user_search_btn': 'search'
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
        var full_name = $('.o_full_name').val().trim();
        var nick_name = $('.o_nick_name').val().trim();
        var job_number = $('.o_job_number').val().trim();
        var condition = ""
        if ((full_name == undefined || full_name == "")
            && (nick_name == undefined || nick_name == "")
            && (job_number == undefined || job_number == "") ){
            return;
        }
        condition = []
        if (full_name){
            condition.push(['full_name', '=', full_name]);
        }
        if (nick_name){
            condition.push(['nick_name', '=', nick_name]);
        }
        if (job_number){
            condition.push(['job_number', '=', job_number]);
        }
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
                }
            );
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
        this.render_notice();
        this.render_event();
    },
    render_title: function(){
        var username = this.user;
        var $info = $(QWeb.render('content_title', {
            'username': username
        }));
        $info.appendTo('.o_content_title');
    },
    render_dashboard: function(parent){
        var data = {out:10, special:20, expense:30, my:50};
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
                    parent.load_echarts(result.month, result.total, result.completed, result.grants);
                })
            });
    },
    load_echarts:function(month, total, completed,grants){
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
        },
    render_notice: function(){
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
    },
    render_event: function(){
        var $info = $(QWeb.render('content_event', {}));
        $info.appendTo('.o_content_event');
        this.render_affairs();
        this.render_applies();
    },
    render_affairs: function(){
        var affairs = [];
        var currentPage =1
        var Menus = new Model('ir.ui.menu');
            Menus.call('load_menus', [core.debug], {context: session.user_context}).
                then( function(menu_data) {
                    new Model("dtdream.content.event.affairs")
                    .call("get_all_affairs", [menu_data,currentPage],{},null)
                    .then(function (data) {
                        if (data) {
                            affairData=data
                            affairs=data['affairs']
                        }
                        var $info = $(QWeb.render('content_event_affairs', {
                            'affairs': affairs,
                            'afftotalPage':data['totalPage'],
                            'affcurrentPage':data['currentPage'],
                            'affnextPage':parseInt(data['currentPage'])+1,
                            'affpreviousPage':parseInt(data['currentPage'])-1,
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
                            $("li.previous[type='affairs']").addClass('disabled')
                        }
                        else{
                            $("li.previous[type='affairs']").removeClass('disabled')
                        }
                        if (parseInt(data['currentPage'])+1>data['totalPage']){
                            $("li.next[type='affairs']").addClass('disabled')
                        }else{
                            $("li.next[type='affairs']").removeClass('disabled')
                        }
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
                    .call("get_all_applies", [menu_data,currentPage],{},null)
                    .then(function (data) {
                        if (data) {
                            applyData =data
                            applies=data['applies']
                        }
                        var $info = $(QWeb.render('content_event_applies', {
                            'applies': applies,
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
                            $("li.previous[type='applies']").addClass('disabled')
                        }
                        else{
                            $("li.previous[type='applies']").removeClass('disabled')
                        }
                        if (parseInt(data['currentPage'])+1>data['totalPage']){
                            $("li.next[type='applies']").addClass('disabled')
                        }else{
                            $("li.next[type='applies']").removeClass('disabled')
                        }
                    })
                });



    },
    destroy: function() {
        if (this.notices_time_hd){
            clearInterval(this.notices_time_hd);
            this.notices_time_hd=null;
        }
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
    }
});



return Main;

});