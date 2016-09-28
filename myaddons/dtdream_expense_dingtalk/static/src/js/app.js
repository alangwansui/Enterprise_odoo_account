// logger.i('Here we go... wer...');
//
// logger.i("i fuck you ...")
//
// logger.i(location.href);
//
// logger.i("agentId:" + _config.jsticket);
// logger.i("corpId:" + _config.corpId);
// logger.i("timestamp:" + _config.timeStamp);
// logger.i("token:" + _config.token);
// logger.i("sign:" + _config.signature);

/**
 * _config comes from server-side template. see views/index.jade
 */
// logger.i("d:" + dd);

// main_url = '/dtdream_expense_dingtalk/main';
// logger.i(main_url);
// window.location.href = main_url;

dd.config({
    agentId: _config.agentId,
    corpId: _config.corpId,
    timeStamp: _config.timeStamp,
    nonceStr: _config.nonceStr,
    signature: _config.signature,
    jsApiList: [
        'runtime.info',
        'device.notification.prompt',
        'biz.chat.pickConversation',
        'device.notification.confirm',
        'device.notification.alert',
        'device.notification.prompt',
        'biz.chat.open',
        'biz.util.open',
        'biz.user.get',
        'biz.contact.choose',
        'biz.telephone.call',
        'biz.ding.post',
        'device.geolocation.get',
        'biz.navigation.setLeft',
        'biz.navigation.close',
        'ui.pullToRefresh.disable',

    ]
});

dd.ready(function () {
    // logger.i("fuck.....")
    // logger.i('dd.ready rocks!');
//
//       dd.biz.navigation.setLeft({
//     show: false,//控制按钮显示， true 显示， false 隐藏， 默认true
//     control: false,//是否控制点击事件，true 控制，false 不控制， 默认false
//     showIcon: false,//是否显示icon，true 显示， false 不显示，默认true； 注：具体UI以客户端为准
//     text: 'NO',//控制显示文本，空字符串表示显示默认文本
//     onSuccess : function(result) {
//        logger.i("success;"+JSON.stringify(result));
//         /*
//         {}
//         */
//         //如果control为true，则onSuccess将在发生按钮点击事件被回调
//     },
//     onFail : function(err) {
//         logger.i("error;"+JSON.stringify(result));
//     }
// });

    // dd.biz.navigation.setLeft({
    //     show: true,//控制按钮显示， true 显示， false 隐藏， 默认true
    //     control: true,//是否控制点击事件，true 控制，false 不控制， 默认false
    //     showIcon: true,//是否显示icon，true 显示， false 不显示，默认true； 注：具体UI以客户端为准
    //     text: '退出应用',//控制显示文本，空字符串表示显示默认文本
    //     onSuccess: function (result) {
    //         /*
    //          {}
    //          */
    //         //如果control为true，则onSuccess将在发生按钮点击事件被回调
    //
    //         dd.device.notification.confirm({
    //             message: "您确定要退出报销应用吗?",
    //             title: "提示",
    //             buttonLabels: ['确定', '取消'],
    //             onSuccess: function (result) {
    //
    //                 if (result.buttonIndex == 0) {
    //                     dd.biz.navigation.close({
    //                         onSuccess: function (result) {
    //                             /*result结构
    //                              {}
    //                              */
    //                         },
    //                         onFail: function (err) {
    //                         }
    //                     })
    //                 }
    //                 //onSuccess将在点击button之后回调
    //                 /*
    //                  {
    //                  buttonIndex: 0 //被点击按钮的索引值，Number类型，从0开始
    //                  }
    //                  */
    //
    //
    //             },
    //             onFail: function (err) {
    //             }
    //         });
    //     },
    //     onFail: function (err) {
    //     }
    // });

    dd.runtime.info({
        onSuccess: function (info) {
            logger.i('runtime info: ' + JSON.stringify(info));
        },
        onFail: function (err) {
            logger.e('fail: ' + JSON.stringify(err));
        }
    });

    setTimeout(dd.runtime.permission.requestAuthCode({
        corpId: _config.corpId, //企业id
        onSuccess: function (info) {
            logger.i('authcode: ' + info.code);

            dd.ui.pullToRefresh.disable();

            $.ajax({
                url: '/dtdream_expense_dingtalk/authUser',
                type: "GET",
                data: {"access_token": _config.token, "code": info.code},
                dataType: 'json',
                timeout: 9000,
                success: function (data, status, xhr) {
                    logger.i("fuck you");
                    logger.i('auth....');
                    // logger.i("data:"+ data.userid)
                    // logger.i("data:"+ data.userid)
                    // logger.i("errcode:"+ data.errcode===0)
                    logger.i("dd:" + data.userid);
                    dd.userid = data.userid;
                    // alert("dd:"+dd.userid);

                    odoo.define('dtdream_expense.dingtalk', function (require) {
                        var Dingtalk = require('dtdream_expense_dingtalk.ui');
                        // var Dingtalk=require('project_timeshee.ui')
                        var app = new Dingtalk();
                        app.appendTo($('.page'));
                    });

                    //main_url = '/dtdream_expense_dingtalk/main';
                    //logger.i(main_url);
                    // window.location.href = main_url;


                    // $('App').append('my god');


                    // var info = JSON.parse(data);
                    // logger.info("info:"+ info)
                    // // logger.i("info:"+info)
                    // if (data.errcode == 0) {
                    //     logger.i('user id: ' + info.userid);
                    //     dd.userid = info.userid;
                    // }
                    // else {
                    //     logger.e('auth error: ' + data);
                    // }
                },
                error: function (xhr, errorType, error) {
                    logger.i("error");
                    logger.e(errorType + ', ' + error);
                }
            });
        },
        onFail: function (err) {
            logger.e('requestAuthCode fail: ' + JSON.stringify(err));
        }
    }), 10000);


    logger.i("fuck ..ass")

});

dd.error(function (err) {
    logger.e('dd error: ' + JSON.stringify(err));
});

