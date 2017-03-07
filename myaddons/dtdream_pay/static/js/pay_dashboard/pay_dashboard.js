
odoo.define('dtdream_pay.ui.dashboard', function (require) {
    "use strict";

    var core = require('web.core');
    var formats = require('web.formats');
    var Model = require('web.Model');
    var session = require('web.session');
    var KanbanView = require('web_kanban.KanbanView');
    var form_common = require('web.form_common');

//    var pay_detail = require('dtdream_pay.ui.dashboard.detail')

    var QWeb = core.qweb;

    var _t = core._t;
    var _lt = core._lt;
    var applyData= [];
    var affairData= [];
    var doneData=[];


    var PayDashboardView = KanbanView.extend({

        display_name: '工资',

        icon: 'fa-dashboard',

        view_type: "dtdream_pay_dashboard",

        searchview_hidden: true,

        events: {
            'click.sjbtn':'on_open_item_sjbtn',
            'click .dosave':'on_doSave',
            'click .open_detail': 'open_detail',
            'click.queryBtn':'do_pay_search',
            'click.return':'do_back',
            'click.open_detail_phone':'open_detail_phone',
            'click.phone_back':'do_phone_back',
            'click.toIndex':'do_to_index',
        },

        fetch_data: function () {
            // Overwrite this function with useful data
            return new Model('dtdream.pay')
                .call('retrieve_pay_dashboard', []);
        },

        render: function () {
            var super_render = this._super;
            var self = this;
            var report_dashboard = QWeb.render('dtdream_pay.validate', {
            });
            super_render.call(self);
            $(report_dashboard).prependTo(self.$el);
            self.$el.find('.oe_view_nocontent').hide();
        },
        on_open_item_sjbtn:function(ev){
        if($(ev.target).attr('class')=='lineInput-btn sjbtn'){
            var data={}
            $.ajax({
                type: 'POST',
                url: "/dtdream_pay/getValidateCode",
                contentType: "application/json; charset=utf-8",
                data: JSON.stringify(data),
                dataType: "json",
                success: function(data){
                    console.log(data.result);
                    if(data.result){
                        if (data.result.code == 10000){
                            $(".pleasedxfs").children()[0].innerText="校验码短信已发送到你的手机"+data.result.telephone+"上，请及时查收。"
                            $(".pleasedxfs").addClass("appearError").siblings('.appearError').removeClass('appearError');
                        } else{
                            $(".pleasewarm").children()[0].innerText=data.result.message
                            $(".pleasewarm").addClass("appearError").siblings('.appearError').removeClass('appearError');
                        }
                    }else if(data.error){
                        alert(data.error.data.message)
                    }
                },
                error:function(data){
                    console.log("error")
                }
            });
            }
        },
        on_doSave:function(ev){
        if($(ev.target).attr('class')=='savebtn dosave'){
            ev.preventDefault();
            ev.stopPropagation();
            var self = this;
            var sn = document.getElementById("lineInput").value;
            if ( sn == null || sn == undefined || sn == "" ) {
                $("#lineInput").addClass("errorBorder");
                $(".pleaseSR").addClass("appearError").siblings('.appearError').removeClass('appearError');
                return true;
            } else{
                document.getElementById("lineInput").className = "lineInput-no";
                $(".pleaseSR").removeClass("appearError")
            }
            var data={"sn":sn}
            $.ajax({
                type: 'POST',
                url: "/dtdream_pay/saveValidateCode",
                contentType: "application/json; charset=utf-8",
                data: JSON.stringify(data),
                dataType: "json",
                success: function(data){
                    console.log(data.result);
                    if(data.result){
                        if (data.result.code == 10000){
                            sessionStorage.setItem("vaCode", data.result.vaCode)
                            var startMonth="";
                            var endMonth="";
                            self.fetch_data().then(function (result) {
                                var $info = QWeb.render('dtdream_pay.dashboardView', {
                                    "times":result.times,
                                    "previous_date": result.previous_date,
                                });
                                $('.o_kanban_ungrouped').html('')
                                $($info).appendTo('.o_kanban_ungrouped');
                                self.render_content(startMonth,endMonth,sessionStorage.getItem('vaCode'));
                                self.render_watermark(data.result.waterline);
                                self.render_datetimepicker();
                            });
                        }else if(data.result.code==10002){
                            $(".pleaseyzcw").addClass("appearError").siblings('.appearError').removeClass('appearError');
                        }else{
                            $(".pleasewarm").children()[0].innerText=data.result.message
                            $(".pleasewarm").addClass("appearError").siblings('.appearError').removeClass('appearError');
                        }
                    }else if(data.error){
                        alert(data.error.data.message)
                    }
                },
                error:function(data){
                    console.log("error")
                }
            });
            }
        },
        render_content: function(startMonth,endMonth,vaCode){
            new Model("dtdream.pay")
            .call("get_pay_list_by_user", [startMonth,endMonth,vaCode,location.host],{},null)
            .then(function (data) {
                if (data && data['lists']) {
                    var lists=data['lists']
                    var $info = $(QWeb.render('dtdream_pay.content_event_data', {
                        'lists': lists,
                        'total_benyueyingfa':data['total_benyueyingfa'],
                        'total_koushebaogjj':data['total_koushebaogjj'],
                        'total_shuiqianshouru':data['total_shuiqianshouru'],
                        'total_kougeren':data['total_kougeren'],
                        'total_shifa':data['total_shifa'],
                    }));
                    $('.dataContainer').html('')
                    $info.appendTo('.dataContainer');
                }else if(data && data['code']){
                    if(data['code']==10001){
                        location.reload([true])
                    }else{
                        alert(data['message'])
                    }
                }
             });
        },
        render_datetimepicker:function(){
            $('.datepicker').datetimepicker({
                format:'YYYY-MM',
                calendarWeeks: false,
                viewMode:'months',
                minViewMode:'months',
                pickTime: false,
                useMinutes: false,
                language: 'zh-CN'             //设置时间控件为中文          
            });
        },
        render_watermark:function(userName){
            $(".o_view_manager_content").css("background-color","transparent")
            var self = this;
            function textToImg(canvasWidth,canvasHeight,txtX,txtY,txtFont,opacity,deg) {
                var len = 100;
                var i = 0;
                var fontSize = txtFont;
                var fontWeight = $('fontWeight').value || 'normal';
                var txt = userName;
                var canvas = document.createElement('canvas');
                if (len > txt.length) {
                    len = txt.length;
                }
                canvas.width = canvasWidth;
                canvas.height = canvasHeight;
                var context = canvas.getContext('2d');
                context.clearRect(0, 0, canvas.width, canvas.height);
                context.fillStyle = "rgba(160,160,160,"+opacity+")";
                context.font = fontWeight + ' ' + fontSize + 'px sans-serif';
                context.textBaseline = 'top';
                context.rotate(-Math.PI/deg);
                canvas.style.display = 'none';
                // console.log(txt.length);
                function fillTxt(text) {
                    while (text.length > len) {
                        var txtLine = text.substring(0, len);
                        text = text.substring(len);
                        context.fillText(txtLine, 20, fontSize * (3 / 2) * i++,
                                canvas.width);
                    }
                    context.fillText(text, txtX, txtY, canvas.width);
                }
                var txtArray = txt.split('\n');
                for ( var j = 0; j < txtArray.length; j++) {
                    fillTxt(txtArray[j]);
                    context.fillText('\n', 0, fontSize * (3 / 2) * i++, canvas.width);
                }
                var imageData = context.getImageData(0, 0, canvas.width, canvas.height);
                var imgSrc = canvas.toDataURL("image/png");
                return imgSrc;
            }
            var img1 = textToImg(225,140,100,100,14,1,6);
//            $(".o_content").css("background-image","url("+img1+")");
            $(".o_kanban_ungrouped").css("background-image","url("+img1+")");

        },


        open_detail:function(ev){
            ev.preventDefault();
            ev.stopPropagation();
            var self = this;
            var month=ev.currentTarget.innerText
            var vaCode=sessionStorage.getItem('vaCode')
            new Model("dtdream.pay")
            .call("get_pay_list_detail_by_month", [month,vaCode,location.host],{},null)
            .then(function (data) {
                if (data && data['lists']) {
                    var lists=data['lists']
                    var $info = $(QWeb.render('dtdream_pay.dashboard_detailView', {
                        'lists':lists
                    }));
                    $('.o_kanban_ungrouped').html('')
                    $info.appendTo('.o_kanban_ungrouped');
                    var all = document.querySelectorAll('.canhide')
                    for(var i=0,l=all.length;i<l;i++){
                        if(all[i].children[1].innerText==0){
                            $(all[i]).remove()
                        }
                    }
                    var all = document.querySelectorAll('.canhidedif')
                    var canhidedif=false
                    for(var i=0,l=all.length;i<l;i++){
                        if(all[i].children[1].innerText!=0){
                            canhidedif=true
                            break
                        }
                    }
                    if(!canhidedif){
                        for(var i=0,l=all.length;i<l;i++){
                            $(all[i]).remove()
                        }
                    }
                    var noText=`
                    <div class="col-xs-4">
                        <span class="tText"></span>
                        <span class="cText"></span>
                    </div>`;
                    var judgeAll=document.querySelectorAll('.judge');
                    for(var i=0,l=judgeAll.length;i<l;i++){
                        var html=judgeAll[i].innerHTML;
                        var count=judgeAll[i].querySelectorAll('.col-xs-4').length;
                        if(count%3!=0){
                            for(var j=0,k=3-count%3;j<k;j++){
                                html+=noText;
                            }
                            judgeAll[i].innerHTML=html;
                        }
                    }
                }else if(data && data['code']){
                    if(data['code']==10001){
                        location.reload([true])
                    }else{
                        alert(data['message'])
                    }
                }
            })
        },
        do_pay_search:function(ev){
            ev.preventDefault();
            ev.stopPropagation();
            var self = this;
            if($(ev.target).attr('class')=='btn queryBtn'){
                var startMonth=$('#startmonth').val()
                 var endMonth=$('#endmonth').val()
                 sessionStorage.setItem("startMonth", startMonth)
                 sessionStorage.setItem("endMonth", endMonth)
                if($('#datacontainer').css('display')=="none"){
                    new Model("dtdream.pay")
                    .call("get_pay_phone_list_by_user", [startMonth,endMonth,sessionStorage.getItem('vaCode'),location.host],{},null)
                    .then(function (data) {
                        if (data && data['lists']) {
                            var lists=data['lists']
                            var $info = $(QWeb.render('dtdream_pay.dashboardPhoneView', {
                                'startMonth':startMonth,
                                'endMonth':endMonth,
                                'lists':lists,
                            }));
                            $('.o_kanban_ungrouped').html('')
                            $info.appendTo('.o_kanban_ungrouped');
                        }else if(data && data['code']){
                            if(data['code']==10001){
                                location.reload([true])
                            }else{
                                alert(data['message'])
                            }
                        }
                    })
                }else{
                    $('.dataContainer').html('')
                    self.render_content(startMonth,endMonth,sessionStorage.getItem('vaCode'))
                }
            }
        },
        do_back:function(ev){
            ev.preventDefault();
            ev.stopPropagation();
            var self = this;
            if($(ev.target).attr('class')=='return'){
                var startMonth=sessionStorage.getItem('startMonth');
                var endMonth=sessionStorage.getItem('endMonth');
                self.fetch_data().then(function (result) {
                    var $info = QWeb.render('dtdream_pay.dashboardView', {
                        "times":result.times,
                        "previous_date": result.previous_date,
                    });
                    $('.o_kanban_ungrouped').html('')
                    $($info).appendTo('.o_kanban_ungrouped');
                    self.render_content(startMonth,endMonth,sessionStorage.getItem('vaCode'));
                    self.render_datetimepicker();
            });
        }},
        do_to_index:function(ev){
            ev.preventDefault();
            ev.stopPropagation();
            var self = this;
            if($(ev.target).attr('class')=='toIndex'){
                $('.o_kanban_ungrouped').html('')
                    var $info = QWeb.render('dtdream_pay.dashboardView', {
                    });
                    $($info).appendTo('.o_kanban_ungrouped');
                    self.render_datetimepicker();
            }
        },
        open_detail_phone:function(ev){
            ev.preventDefault();
            ev.stopPropagation();
            var self = this;
            if($(ev.target).attr('class')=='qyText open_detail_phone'){
                var month=$('.faxinyue')[0].innerText
                var vaCode=sessionStorage.getItem('vaCode')
                new Model("dtdream.pay")
                .call("get_pay_phone_list_detail_by_month", [month,vaCode,location.host],{},null)
                .then(function (data) {
                    if (data && data['lists']) {
                        var lists=data['lists']
                        var $info = $(QWeb.render('dtdream_pay.dashboard_detailphoneView', {
                            'lists':lists,
                        }));
                        $('.o_kanban_ungrouped').html('')
                        $info.appendTo('.o_kanban_ungrouped');
                        var all = document.querySelectorAll('.canhide')
                        for(var i=0,l=all.length;i<l;i++){
                            if(all[i].children[1].innerText==0){
                                $(all[i]).parent().remove()
                            }
                        }
                        var all = document.querySelectorAll('.canhidedif')
                        var canhidedif=false
                        for(var i=0,l=all.length;i<l;i++){
                            if(all[i].children[1].innerText!=0){
                                canhidedif=true
                                break
                            }
                        }
                        if(!canhidedif){
                            for(var i=0,l=all.length;i<l;i++){
                                $(all[i]).parent().remove()
                            }
                        }
                    }else if(data && data['code']){
                        if(data['code']==10001){
                            location.reload([true])
                        }else{
                            alert(data['message'])
                        }
                    }
                })
            }
        },
        do_phone_back:function(ev){
            ev.preventDefault();
            ev.stopPropagation();
            var self = this;
            if($(ev.target).attr('class')=='qyText phone_back'){
                var startMonth=sessionStorage.getItem('startMonth');
                var endMonth=sessionStorage.getItem('endMonth');
                 new Model("dtdream.pay")
                    .call("get_pay_phone_list_by_user", [startMonth,endMonth,sessionStorage.getItem('vaCode'),location.host],{},null)
                    .then(function (data) {
                        if (data && data['lists']) {
                            var lists=data['lists']
                            var $info = $(QWeb.render('dtdream_pay.dashboardPhoneView', {
                                'startMonth':startMonth,
                                'endMonth':endMonth,
                                'lists':lists,
                            }));
                            $('.o_kanban_ungrouped').html('')
                            $info.appendTo('.o_kanban_ungrouped');
                        }else if(data && data['code']){
                        if(data['code']==10001){
                            location.reload([true])
                        }else{
                            alert(data['message'])
                        }
                    }
                    })
            }
        },
    });

    core.view_registry.add('dtdream_pay_dashboard', PayDashboardView);

    return PayDashboardView

});
