dd.config({
    // agentId: _config.agentId,
    // corpId: _config.corpId,
    // timeStamp: _config.timeStamp,
    // nonceStr: _config.nonceStr,
    // signature: _config.signature,
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
    dd.biz.navigation.setRight({
        show: false,//控制按钮显示， true 显示， false 隐藏， 默认true
        control: false,
    });
});
