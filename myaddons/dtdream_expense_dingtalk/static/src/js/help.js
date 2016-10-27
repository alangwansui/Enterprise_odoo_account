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
    dd.runtime.info({
        onSuccess: function (info) {
            // iso left事件
            dd.biz.navigation.setLeft({
                show: true,//控制按钮显示， true 显示， false 隐藏， 默认true
                control: true,//是否控制点击事件，true 控制，false 不控制， 默认false
                showIcon: true,//是否显示icon，true 显示， false 不显示，默认true； 注：具体UI以客户端为准
                text: '',//控制显示文本，空字符串表示显示默认文本
                onSuccess : function(result) {
                    window.open("/dtdream_expense_dingtalk/my?dd_nav_bgcolor=FF5E97F6");
                },
                onFail: function(err){
                }
            });

            document.addEventListener(
                'backbutton',
                function(e) {
                    e.preventDefault();
                    window.open("/dtdream_expense_dingtalk/my?dd_nav_bgcolor=FF5E97F6");
                },
                false
            );

        },
        onFail: function (err) {
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
});

dd.error(function (err) {
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