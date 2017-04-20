odoo.define('dtdream_sale.weekly_reports', function (require) {
"use strict";

var Model = require('web.Model');
var FormView = require('web.FormView');
var session = require('web.session');

var check_employee = [];     //用于存放员工个人信息的工号
var check_department = [];   //用于存放部门的id
var check_content = "";      //用于存放批复内容
var data_id = "";            //用于存放单据的id值
var check_session_uid = "";
var send_data = {
    "check_employee":[],
    "check_department":[],
    "check_content":"",
    "check_session_uid":"",
    "data_id":""
};

FormView.include({
    events:{
        'click .weeklyReport_check': 'checkout'
    },
    checkout: function(){
        console.log(session.uid);
        send_data.check_session_uid = session.uid;
        data_id = location.hash.slice(1).split("&")[0].slice(3);
        send_data.data_id = data_id;
        console.log(send_data);
        //加载默认批复对象
        var first_man = "";
        _($(".check_own_person")).each(function(ele){
            if(ele.innerHTML.replace(/^\s+|\s+$/g,"") != "报告人"){
                first_man = ele.innerHTML.replace(/^\s+|\s+$/g,"");
            }
        });

        var html1=[
        '<div class=check_layer>',
            '<div class=\'form-group\'>',
                '<label for=feedback_user class=\'col-sm-3 control-label\'>批复发送对象</label>',
                '<div class=\'check_input o_form_field col-sm-6\'>',
                    '<span class=\'badge dropdown\'>'
        ].join('\n');
        var html2 = '<span data-check="employee" data-number="'+first_man.split(" ")[1]+'" class="badge_text">'+first_man+'</span>';
        var html3=[
                        '<span class=\'fa fa-times check_delete\'></span>',
                    '</span>',
                    '<div class=\'check_input_content o_form_field\'>',
                        '<div class=check_input_dropdown>',
                            '<input class=\'o_form_input check_send_name\' type=text>',
                            '<i class=\'fa fa-sort-desc\' aria-hidden=true></i>',
                        '</div>',
                        '<ul class=\'dropdown-menu check_dropdown\'>',
                        '</ul>',
                    '</div>',
                '</div>',
            '</div>',
            '<div class=\'form-group\'>',
                '<label for=feedback_user class=\'col-sm-3 control-label\'>批复内容</label>',
                '<div class=\'check_input col-sm-6 check_write\'>',
                    '<textarea class=check_write_content rows=4 placeholder=\'批复内容将以邮件及钉钉消息方式发送至您选择的批复发送对象\'></textarea>',
                '</div>',
            '</div>',
        '</div>'
        ].join('\n');
        var html = html1+html2+html3;
        layer.open({
            title: "批复",
            type: 1,
            shade:false,
            //skin: 'layui-layer-rim', //加上边框
            area: ['50%', '292px'], //宽高
            content: html,
            btn:["确认","取消"],
            btnAlign: 'l',
            yes: function(index, layero){
                //点击确定按钮，发送邮件,并关闭弹出框
                _($(".badge_text")).each(function(ele){
                    console.log(ele.dataset.check);
                    if(ele.dataset.check == "employee"){
                        check_employee.push(ele.dataset.number);
                        send_data.check_employee = check_employee;
                    }
                    if(ele.dataset.check == "department"){
                        check_department.push(ele.dataset.number);
                        send_data.check_department = check_department;
                    }
                });
                var check_send_content = $(".check_write_content").val();
                if(check_send_content == ""){
                    alert("亲，请填写批复内容哦！")
                }else{
                    check_content = check_send_content;
                    send_data.check_content = check_content;
                    new Model('dtdream.sale.own.report')
                        .call('call_check_response',[send_data])
                        .then(function(result){

                        });

                    layer.close(index);
                }
                //清空所有数据
                check_employee = [];
                check_department = [];
                check_content = [];
                data_id = "";
                send_data.check_employee = [];
                send_data.check_department = [];
                send_data.check_content = "";
            },
            btn2: function(index, layero){
                //点击取消按钮，弹出框消失
                layer.close(index);
            }
        });

        //输入框的值发生改变时，如果有此人则显示一个框，框内为此人信息，若无则隐藏框
        $('.check_send_name').bind('input propertychange', function() {
            $(".check_dropdown").html("");
            var $input_val = $(this).val();
            if($input_val != ""){
                //将input中的值传入数据库，将查询到的结果输出在li中
                var html = "";
                new Model('dtdream.sale.own.report')
                    .call('get_users',[$input_val])
                    .then(function(result){
                        if(result[0].length > 0){ //result[0]中是员工的信息
                            _(result[0]).each(function(ele,i){
                                //ele[0]是员工名字和工号拼接而成的字符串,ele[1]是工号
                                html+="<li class=check_dropdown_li data-check='employee' data-number='"+ele[1]+"' data-name='"+ele[0]+"'>"+ele[0]+"</li>";
                            });
                        }
                        if(result[1].length > 0){
                             _(result[1]).each(function(ele,i){
                                //ele[0]是部门名字,ele[1]是部门id
                                html+="<li class=check_dropdown_li data-check='department' data-number='"+ele[1]+"' data-name='"+ele[0]+"'>"+ele[0]+"</li>";
                            });
                        }

                        if(result[0].length > 0 || result[1].length > 0){
                            $(".check_dropdown").css("display","block");
                        }else{
                            $(".check_dropdown").css("display","none");
                        }
                        $(".check_dropdown").append(html);
                        html = "";

                         //点击li将下拉列表隐藏，并将选中的批复对象展示到input中
                        $(".check_dropdown_li").on('click' ,function(){
                            console.log($(this));
                            var badge_html = "";
                            if($(this).data("check") == "employee"){
                                badge_html = "<span class='badge dropdown'><span data-check='employee' data-number='"+$(this).data("number")+"' class='badge_text'>"+$(this).data("name")+"</span><span class='fa fa-times check_delete'></span></span>";
                            }
                            if($(this).data("check") == "department"){
                                badge_html = "<span class='badge dropdown'><span data-check='department' data-number='"+$(this).data("number")+"' class='badge_text'>"+$(this).data("name")+"</span><span class='fa fa-times check_delete'></span></span>";
                            }

                            $(".check_input_content").before(badge_html);
                            $(".check_send_name").val("");
                            $(".check_dropdown").html("").css("display","none");

                            //点击badge中的删除图标，删除badge
                            $(".check_delete").click(function(){
                                $(this).closest(".badge").remove();
                            });
                        });
                    });
            }else if($input_val == ""){
                //如果输入的内容为空，则清空下拉列表中的内容
                $(".check_dropdown").html("");
            }

        });

        //点击badge中的删除图标，删除badge
        $(".check_delete").click(function(){
            $(this).closest(".badge").remove();
        });


    }

});

});