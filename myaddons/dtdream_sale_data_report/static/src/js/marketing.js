/**
 * Created by mm on 2017/2/6.
 */
//    设置时间日期插件
$(".datepickerstart").datetimepicker({
    format:'yyyy-mm-dd',
    todayBtn:  true,
    autoclose: true,
    startView: 'month',
    minView:'month',
    language: 'zh-CN'
});
$(".start").click(function(){
    $(".datepickerstart").datetimepicker('show');
});
$(".datepickerend").datetimepicker({
    format:'yyyy-mm-dd',
    todayBtn:  true,
    autoclose: true,
    startView: 'month',
    minView:'month',
    language: 'zh-CN'
});
$(".end").click(function(){
    $(".datepickerend").datetimepicker('show');
});
//    设置ul中的li水平居中
var ulWidth=$('#MKmyTab').width();
var paddingLeft=(ulWidth-750)/2;
$("#MKmyTab").css("padding-left",paddingLeft);
$('#MKmyTab .inline').css('left',paddingLeft);

//    设置滑动条的初始距离
if($("#MKmyTab li.active a").html() == "现金收入"){
    $('#MKmyTab .inline').css('width','150px');
    $("#mkcash").siblings('.active').removeClass('active');
}

//    设置鼠标移入li时的效果
$("#MKmyTab").on("mouseenter","li:not(.inline)",function(){

//        获取滑动条的滑动距离
    var movedistance=($(this).index())*150;
    $('#MKmyTab .inline').css('width','150px').css('left',paddingLeft+movedistance);

//        获取当前li的data-index值
    var dropId=$(this).data('index');
    $("#"+dropId).addClass('active').siblings('.active').removeClass('active');
    /*if($("#"+dropId).hasClass('active')){
     $("#"+dropId).addClass('in').siblings('.in').removeClass('in');
     }*/
    $("#"+dropId).addClass('in').siblings('.in').removeClass('in');
    if(!$(this).hasClass('active')){
        $(this).addClass('active').siblings('.active').removeClass('active');
    }
});
