Util.log("Before dd config", location.href.substring(location.href.lastIndexOf('/')+1));
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
Util.log("End dd config", location.href.substring(location.href.lastIndexOf('/')+1));
Util.log("Before dd ready", location.href.substring(location.href.lastIndexOf('/')+1));
dd.ready(function () {
//    alert("dd ready");
    dd.runtime.info({
        onSuccess: function (info) {
            Util.log("dd ready runtime success", location.href.substring(location.href.lastIndexOf('/')+1));
            logger.i('runtime info: ' + JSON.stringify(info));
        },
        onFail: function (err) {
            Util.log("dd ready runtime failed", location.href.substring(location.href.lastIndexOf('/')+1));
            logger.e('fail: ' + JSON.stringify(err));
            dd.device.notification.alert({
                "message": 'fail: ' + JSON.stringify(err),
                "title": "警告",
                "buttonName":"确定",
                onSuccess: function () {
                    dd.biz.navigation.back({});
                },
                onFail: function (err) {
                }
            });
        }
    });

    setTimeout(dd.runtime.permission.requestAuthCode({
        corpId: _config.corpId, //企业id
        onSuccess: function (info) {
            logger.i('authcode: ' + info.code);
            Util.log("dd ready requestAuthCode success", location.href.substring(location.href.lastIndexOf('/')+1));
            dd.ui.pullToRefresh.disable();

            $.ajax({
                url: '/dtdream_expense_dingtalk/authUser',
                type: "GET",
                data: {"access_token": _config.token, "code": info.code},
                dataType: 'json',
                timeout: 9000,
                success: function (data, status, xhr) {
                    Util.log("dd ready ajax success", location.href.substring(location.href.lastIndexOf('/')+1));
                    logger.i("userid:"+ data.userid);
                    logger.i("errcode:"+ data.errcode===0);

                    dd.biz.navigation.setIcon({
                        showIcon : true,//是否显示icon
                        iconIndex : 1,//显示的iconIndex,如上图
                        onSuccess : function(result) {
                            window.open("/dtdream_expense_dingtalk/help", "_blank");
                        },
                        onFail : function(err) {
                        }
                    });

                    dd.userid = data.userid;
                    odoo.define('dtdream_expense.dingtalk', function (require) {
                        var Dingtalk = require('dtdream_expense_dingtalk.detail');
                        var app = new Dingtalk();
                        app.appendTo($('.page'));
                    });
                },
                error: function (xhr, errorType, error) {

                    dd.device.notification.alert({
                        "message": errorType + ', ' + error,
                        "title": "警告",
                        "buttonName":"确定",
                        onSuccess: function () {
                            dd.biz.navigation.back({});
                        },
                        onFail: function (err) {
                        }
                    });

                    Util.log("dd ready ajax failed", location.href.substring(location.href.lastIndexOf('/')+1));
                    logger.i("error");
                    logger.e(errorType + ', ' + error);
                }
            });
        },
        onFail: function (err) {
            Util.log("dd ready requestAuthCode failed", location.href.substring(location.href.lastIndexOf('/')+1));
            logger.e('requestAuthCode fail: ' + JSON.stringify(err));
            dd.device.notification.alert({
                "message": 'requestAuthCode fail: ' + JSON.stringify(err),
                "title": "警告",
                "buttonName":"确定",
                onSuccess: function () {
                    dd.biz.navigation.back({});
                },
                onFail: function (err) {
                }
            });
        }
    }), 10000);

});

dd.error(function (err) {
//    alert("dd error");
    logger.e('dd error: ' + JSON.stringify(err));
    dd.device.notification.alert({
        "message": 'dd.error: ' + JSON.stringify(err),
        "title": "警告",
        "buttonName":"确定",
        onSuccess: function () {
            dd.biz.navigation.back({});
        },
        onFail: function (err) {
        }
    });
});

//$(function () {
//    odoo.define('dtdream_expense.dingtalk', function (require) {
//
//        Util.log("init", location.href.substring(location.href.lastIndexOf('/')+1));
//        var Dingtalk = require('dtdream_expense_dingtalk.detail');
//        var app = new Dingtalk();
//        app.appendTo($('.nav'));
//        $.init();
//    });
//});