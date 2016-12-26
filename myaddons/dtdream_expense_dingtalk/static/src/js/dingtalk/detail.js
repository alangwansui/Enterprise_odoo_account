/**
 * @author 夏雪宜<gaoq@dtdream.com>
 * @class DingtalkDetailUI
 */
odoo.define('dtdream_expense_dingtalk.detail', function (require) {
    "use strict";
    var core = require('web.core');
    var session = require('web.session');
    var Widget = require('web.Widget');
    var time_module = require('web.time');
    var Model = require('web.Model');
    var QWeb = core.qweb;
    var historyScreens = [];

    /**
     * @class Main
     * @classdesc 主界面
     */
    var Main = Widget.extend({

        /**
         * @memberOf Main
         * @member template
         * @description 模板名称,可以在src/xml/expense.xml中查找到main
         */
        template: 'footer',
        /**
         * @memberOf Main
         * @method init
         * @description 初始化,参考widget.js
         * @param {object} parent 父级传递的参数
         */
        init: function (parent) {
            var self = this;

            self._super(parent);
            self.load_template();

            // register change screen event
            core.bus.on('change_screen', this, this.go_to_screen);
            core.bus.on('go_back', this, this.go_back);

            // iso left事件
            dd.biz.navigation.setLeft({
                show: true,//控制按钮显示， true 显示， false 隐藏， 默认true
                control: true,//是否控制点击事件，true 控制，false 不控制， 默认false
                showIcon: true,//是否显示icon，true 显示， false 不显示，默认true； 注：具体UI以客户端为准
                text: '',//控制显示文本，空字符串表示显示默认文本
                onSuccess : function(result) {

                    if (view_image == true){
                        Util.log("iso left event", "close image:" + historyScreens.length);
                        $.closeModal();
                        view_image=false;
                        return;
                    }

                    Util.log("iso left event 0", "iso:" + historyScreens.length);
                    if (historyScreens.length <= 1) {
                        Util.log("iso left event 1", "xxxx");
                        dd.biz.navigation.back({});
                    } else {
                        Util.log("iso left event 2", historyScreens.length);
                        historyScreens.length--;
                        core.bus.trigger('change_screen', {
                            model: historyScreens[historyScreens.length-1].model,
                            action: historyScreens[historyScreens.length-1].action,
                            id: historyScreens[historyScreens.length-1].id,
                            back:true
                        });
                        Util.log("iso left event 3", historyScreens.length);
                    }

                },
                onFail: function(err){
                }
            });

            //android
            document.addEventListener(
                'backbutton',
                function(e) {
                    e.preventDefault();
                    if (view_image == true){
                        $.closeModal();
                        Util.log("android left event", "close image:" + historyScreens.length);
                        view_image=false;
                        return;
                    }
                    Util.log("android left event 0", "android:"+historyScreens.length);

                    if (historyScreens.length <= 1) {
                        Util.log("android left event 1", "xxxx");
                        dd.biz.navigation.back({});
                    } else {
                        Util.log("android left event 2", "android:"+historyScreens.length);
                        historyScreens.length--;
                        core.bus.trigger('change_screen', {
                            model: historyScreens[historyScreens.length-1].model,
                            action: historyScreens[historyScreens.length-1].action,
                            id:historyScreens[historyScreens.length-1].id,
                            back:true
                        });
                        Util.log("android left event 3", "android:"+historyScreens.length);
                    }
                },
                false
            );
        },
        /**
         * @memberOf Main
         * @member events
         * @description 定义事件
         */
        events: {
            /**主工具栏*/
            'click .tab-item': 'on_open_item',
        },
        /**
         * @memberOf Main
         * @description 点击主工具栏时触发界面跳转
         * @param {object}ev dom对象
         */
        on_open_item: function (ev) {
            core.bus.trigger('change_screen', {
                model: $(ev.currentTarget).data('item-id'),
                action: null,
                id: null
            });
        },

        go_back:function(args){
            if (historyScreens.length <= 1) {
                dd.biz.navigation.back({});
            } else {
                historyScreens.length--;
                core.bus.trigger('change_screen', {
                    model: historyScreens[historyScreens.length-1].model,
                    action: historyScreens[historyScreens.length-1].action,
                    id: historyScreens[historyScreens.length-1].id,
                    back:true
                });
            }
        },

        /**
         * @memberOf Main
         * @description 在主窗口上切换界面
         * @param ｛object} args 主要传递界面id,以及options，id参考map_ids_to_widgets
         */
        go_to_screen: function (args) {

            var self = this;

            if (args.back != undefined && args.back){
                this.load_screen(args.model, args.action, args.id);
                return;
            }

            if ( args.model != historyScreens[historyScreens.length-1].model ||
                 args.action != historyScreens[historyScreens.length-1].action ||
                 args.id != historyScreens[historyScreens.length-1].id) {

                 historyScreens[historyScreens.length] = {
                    "model": args.model,
                    "action": args.action,
                    "id": args.id
                 }
                 this.load_screen(args.model, args.action, args.id);
            }
        },
        /**
         * @memberOf Main
         * @description 介于init与start方法之间执行，具体参考widget.js
         * @returns {*|Promise|Promise.<TResult>}
         */
        willStart: function () {
            var self = this;
            return session.session_reload().then(function () {
                self.user = session.username;
                self.uid = session.uid;
            });
        },

        load_screen:function(model, action, id){
            if(this.current_screen){
                this.current_screen.detach();
            }

            var options = {
                    'offset': 0,
                    'have_next_page': true,
                    'is_loading': false,
            };

            if (model == "detail") {
                if (action) {
                    this.detail_info = new Detail_Info();
                    this.detail_info.uid = this.uid;
                    this.detail_info.appendTo($('.o_main_content'));
                    this.current_screen  = this.detail_info;
                    options['detail_id'] = id;
                    options['edit_type'] = action;
                    options['title'] = "消费明细";
                } else {
                    this.detail_list = new Detail_List();
                    this.detail_list.uid = this.uid;
                    this.detail_list.appendTo($('.o_main_content'));
                    this.current_screen = this.detail_list;
                    options['condition'] = [['create_uid', '=', this.uid], ['report_ids', '=', false]];
                    options['title'] = "未报销消费明细";
                }
            } else if (model == "receipts"){
                if (action) {
                    this.receipt_info = new Receipt_Info();
                    this.receipt_info.uid = this.uid;
                    this.receipt_info.appendTo($('.o_main_content'));
                    this.current_screen  = this.receipt_info;
                    options['receipt_id'] = id;
                    options['edit_type'] = action;
                    options['title'] = "报销申请";
                } else {
                    this.receipts_list = new Receipts_List();
                    this.receipts_list.uid = this.uid;
                    this.receipts_list.appendTo($('.o_main_content'));
                    this.current_screen = this.receipts_list;
                    options['condition'] = [['create_uid', '=', this.uid], ['state', '!=', 'yifukuan']];
                    options['title'] = "未报销申请";
                }
            } else if (model == "approval"){
                this.approval_list = new Approval_List();
                this.approval_list.uid = this.uid;
                this.approval_list.appendTo($('.o_main_content'));
                this.current_screen = this.approval_list;
                options['condition'] = [['currentauditperson_userid', '=', this.uid], ['state', '!=', 'jiekoukuaiji'],['state', '!=', 'daifukuan']];
                options['title'] = "待我审批的报销申请";
            } else if (model == "my") {
                this.my_list = new My_List();
                this.my_list.uid = this.uid;
                this.my_list.appendTo($('.o_main_content'));
                options['title'] = "我的";
                this.current_screen = this.my_list;
            } else if (model=="logs"){
                this.logs_list = new Log_List();
                this.logs_list.uid = this.uid;
                this.logs_list.appendTo($('.o_main_content'));
                this.current_screen = this.logs_list;
                options['title'] = "日志";
            }

            var tabs = $('.tab-item');
            for (var i = 0; i < tabs.length; i++){
                var tab = tabs[i];
                $(tab).removeClass('active');
                if ($(tab).data('item-id') == model){
                    $(tab).addClass('active');
                }
            }

            Util.log("QWeb before load data", model + ":" + action + ":" + id);
            this.current_screen.attach($('.o_main_content'), options);
        },
        /**
         * @memberOf Main
         * @description 在init方法后执行，具体参考widget.js
         * @param {object}parent 父对象传递回来的参数
         */
        start: function (parent) {
            this._super(parent);
            var self = this;

            var model_arr = window.location.search.substr(1).match(new RegExp("model=([^&]*)"));
            var action_arr = window.location.search.substr(1).match(new RegExp("action=([^&]*)"));
            var id_arr = window.location.search.substr(1).match(new RegExp("id=([^&]*)"));
            var model=null;
            var action=null;
            var id=null;

            if (model_arr) {
                model = model_arr[1];
                if (action_arr && id_arr){
                    action = action_arr[1];
                    id = id_arr[1];
                }
            } else {
                model = "my";
            }

            historyScreens[historyScreens.length] = {
                    "model": model,
                    "action": action,
                    "id": id
            }

            this.load_screen(model, action, id);
        },

        /**
         * @memberOf Main
         * @method load_template
         * @description 加载qweb界面
         */
        load_template: function () {
            var xml = $.ajax({
                url: "static/src/xml/dingtalk/detail.xml?version=87",
                async: false // necessary as without the template there isn't much to do.
            }).responseText;
            QWeb.add_template(xml);
        },
    });

    /**
     * @class BasicScreenWidget
     * @classdesc 基础对象,继承自widget
     */
    var BasicScreenWidget = Widget.extend({
        /**
         * @memberOf BasicScreenWidget
         * @method init
         * @description 初始化,参考widget.js
         * @param {object} parent 父级传递的参数
         */
        init: function (parent) {
            this._super(parent);
            this.has_been_loaded = false;
        },
        /**
         * @memberOf BasicScreenWidget
         * @description 在init方法后执行，具体参考widget.js
         * @param {object}parent 父对象传递回来的参数
         */
        start: function () {
            var self = this;
            return this._super.apply(this, arguments).then(function () {
                self.has_been_loaded = true;
            });
        },
        /**
         * @memberOf BasicScreenWidget
         * @description 加载qweb模板内容以及传递参数
         * @param {object}el dom 对象
         * @param {object}options 参数
         */
        attach: function (el, options) {
            if (options) {
                this.options = options;
            }
            this.renderElement();
            this.$el.appendTo(el);
            this.setTitle();
        },
        /**
         * @memberOf BasicScreenWidget
         * @description 释放qweb模版内容
         */
        detach: function () {
            this.$el.detach();
            this.didDetach();
            $.closeModal();
        },
        /**
         * @memberOf BasicScreenWidget
         * @description 释放qweb模版内容后执行其他的方法
         */
        didDetach: function () {
            $('.o_main_bar').show();
            return;
        },
        /**
         * @memberOf BasicScreenWidget
         * @description 调用钉钉api, 设置钉钉Title
         */
        setTitle: function () {
            this.title = this.options.title
            dd.biz.navigation.setTitle({
                title: this.title,//控制标题文本，空字符串表示显示默认文本
                onSuccess: function (result) {
                },
                onFail: function (err) {
                }
            });
        }
    });

    /**
     * @class Detail_List
     * @classdesc 消费明细列表
     * @augments BasicScreenWidget
     */
    var Detail_List = BasicScreenWidget.extend({
        /**
         * @memberOf Detail_List
         * @description 模版名称
         */
        'template': 'detail',
        'is_select': false,
        'eidt_type': "",
        /**
         * @memberOf Detail_List
         * @method init
         * @description 初始化,参考widget.js
         * @param {object} parent 父级传递的参数
         */
        'init': function (parent) {
            var self = this;
            self._super(parent);
        },
        /**
         * @memberOf Detail_List
         * @member events
         * @description 定义事件
         * @property {method} edit_expense 点击消费列表行，进入明细界面
         * @property {method} show_select_expense 勾选需要生成报销申请的消费明细列表
         * @property {method} action_button 选择要消费明细后，要执行的事件
         * @property {method} select_expense 点击消费列表内容
         */
        events: {
            'click .o_select_expense': 'select_expense',
            'click .o_view_expense':'view_expense',
            'click .generate_receipt': 'submit_expense',
            'click .delete_details': 'delete_details',
        },
        /**
         * @memberOf Detail_List
         * @description 在init方法后执行，具体参考widget.js
         * @param {object}parent 父对象传递回来的参数
         */
        start: function (parent) {
            var self = this;
            self._super(parent);
        },

        delete_details:function(e){
            e.stopPropagation();
            if ($('.btn-sc,.current').length == 0){
                return;
            }
            var details_ids=[];
            var selected_details = $('.o_select_expense');
            for (var i = 0; i< selected_details.length; i++){
                if($(selected_details[i]).find(':checkbox').prop('checked')){
                    details_ids.push(parseInt($(selected_details[i]).data('id')));
                }
            }

            if (details_ids.length == 0){
                 $.alert('请先选择费用明细。');
            } else {

                $.confirm('您确定要删除此条记录吗?',
                    function () {
                        $.when(new Model('dtdream.expense.record').call('unlink', [details_ids]))
                        .fail(function (err) {
                            $.alert(err.data.message.replace('None', ""));
                        })
                        .then(function () {
                            $.toast("删除成功");
                            core.bus.trigger('change_screen', {
                                model: 'detail',
                                action:null,
                                id: null,
                                back:true
                            });

                        });
                    },
                    function () {

                    }
                );
            }
        },
        /**
        * generate receipt.
        */
        submit_expense:function(e){
            e.stopPropagation();
            if ($('.btn-sc,.current').length == 0){
                return;
            }
            var details_ids=[];
            var selected_details = $('.o_select_expense');
            for (var i = 0; i< selected_details.length; i++){
                if($(selected_details[i]).find(':checkbox').prop('checked')){
                    details_ids.push(parseInt($(selected_details[i]).data('id')));
                }
            }

            if (details_ids.length == 0){
                 $.alert('请先选择费用明细。');
            } else {
                var context = {
                    active_model: 'dtdream.expense.record',
                    active_ids: details_ids,
                }

                $.when(new Model('dtdream.expense.record').call('create_expense_record_baoxiao', {context: context}))
                    .fail(function(error){
                        $.alert(error.data.message);
                    })
                    .then(function (records) {
                        core.bus.trigger('change_screen', {
                            model: 'receipts',
                            action: 'edit',
                            id: records.domain[0][2]
                        });
                    });
            }
        },
        /**
         * @memberOf Detail_List
         * @method select_expense
         * @description 点击消费列表内容停止冒泡
         * @param {object}e dom对象
         */
        select_expense: function (e) {
            e.stopPropagation();

            if ( $(e.currentTarget).find('input:checkbox').prop('checked')) {
                $('.btn-sc').addClass('current');
            } else {
                var checkboxs = $('input:checkbox');
                for (var i = 0; i < checkboxs.length; i++){
                    var checkbox = checkboxs[i];
                    if ($(checkbox).prop('checked')){
                        $('.btn-sc').addClass('current');
                        break;
                    }
                }

                if ( i == checkboxs.length ){
                    $('.btn-sc').removeClass('current')
                }
            }
        },
        /**
         * @memberOf Detail_List
         * @method select_expense
         * @description 点击消费列表内容停止冒泡
         * @param {object}e dom对象
         */
        view_expense: function (e) {

            e.stopPropagation();
            core.bus.trigger('change_screen', {
                                model: 'detail',
                                action:'edit',
                                id:parseInt($(e.currentTarget).data('id'))
                            });
        },
        /**
         * @memberOf Detail_List
         * @description 调用钉钉api,在钉钉界面右上角显示一个"新增"按钮，可以导航到新增消费明细界面
         * @param {object} parent 传递父对象
         */
        rend_navigate_button: function () {
            dd.biz.navigation.setRight({
                show: true,//控制按钮显示， true 显示， false 隐藏， 默认true
                control: true,//是否控制点击事件，true 控制，false 不控制， 默认false
                text: '新增',//控制显示文本，空字符串表示显示默认文本
                iconId: "add",
                onSuccess: function (result) {
                    core.bus.trigger('change_screen', {
                        model: 'detail',
                        action: "create",
                        id: null
                    });
                },
                onFail: function (err) {
                }
            });
        },
        /**
         * @memberOf Detail_List
         * @method load_data
         * @description 调用rpc从服务端获取未生成报销申请的消费明细数据，显示在界面上
         * @param ｛object}parent 传递父对象
         * @returns {jQuery.Deferred}
         */
        load_data: function (parent) {
            var self = this;
            self.is_select = false;
            var def = new $.Deferred();
            new Model('dtdream.expense.record')
                .query(['id', 'name', 'expensecatelog', 'report_ids', 'expensedetail', 'invoicevalue', 'city', 'province', 'currentdate', 'write_date', 'state'])
                .filter(this.options.condition)
                .order_by('-currentdate')
                .all({'timeout': 3000, 'shadow': true})
                .then(function (expense_records) {
                        self.expense_records = expense_records;
                        if (parent.render_data(expense_records, parent.$el)) {
                            def.resolve();
                        } else {
                            def.reject();
                        }
                    }, function (err, event) {
                        event.preventDefault();
                        def.reject();
                    }
                );
            return def.promise();
        },
        /**
         * @memberOf Detail_List
         * @description 将服务端获取的消费明细数据显示在界面上
         * @param {json} expense_records 消费明细
         * @param {object} $el dom对象
         */
        render_data: function (expense_records, $el) {
            for (var i in expense_records) {
                if (expense_records[i].expensedetail[1].length>15){
                    expense_records[i].expensedetail[1] = expense_records[i].expensedetail[1].substring(0, 12) + "...";
                }
            }
            var $expense_records = $(QWeb.render('detail_list', {'expense_records': expense_records, 'expense_records_len': expense_records.length}));
            $el.find('.o_expense').prepend($expense_records);
            Util.log("QWeb end load data", location.href.substring(location.href.lastIndexOf('/')+1));
        },
        /**
         * @memberOf Detail_List
         * @description 显示消费列表界面
         * @param {object} el dom对象
         * @param {object} options 参数
         */
        attach: function (el, options) {
            this._super(el, options);
            this.load_data(this);
            this.rend_navigate_button();
            this.setTitle();
        },
        /**
         * @memberOf Detail_List
         * @description 跳转至另外一个页面前,清空钉钉页面右上角按钮。
         */
        didDetach: function () {
            dd.biz.navigation.setRight({
                show: false,//控制按钮显示， true 显示， false 隐藏， 默认true
            });
        },
        /**
         * @memberOf Detail_List
         * @description 设置钉钉页面抬头内容
         */
        setTitle: function () {
//            this.title = this.options['title'];
            this._super();
        }
    });

    /**
     * @class Receipts_List
     * @classdesc 未报销列表
     * @augments BasicScreenWidget
     */
    var Receipts_List = BasicScreenWidget.extend({
        /**
         * @memberOf Receipts_List
         * @description 报销申请列表模板名称
         */
        template: 'receipts',
        /**
         * @memberOf Receipts_List
         * @description 事件
         * @property {method} edit_expense_report 打开报销申请明细内容界面
         * @property {method} tijiao 提交所选择的报销申请
         * @property {method} cuiban 催办所提交的报销申请
         * @property {method} get_next_page 加载下一页的报销申请
         */
        events: {
            'click .o_edit_receipt': 'edit_expense_report',
            'click .o_view_receipt': 'view_expense_report',
            'click .o_receipts_submit': 'submit',
            'click .o_receipts_cui': 'cui',
            'click .title-wbx': 'slide_toggle',
        },
        slide_toggle:function(ev){
            ev.preventDefault();
            ev.stopPropagation();
            $(ev.currentTarget).next(".list-block").slideToggle();
        },
        /**
         * @memberOf Receipts_List
         * @description 提交所选择的报销申请，执行服务端的workflow-btn_submit
         * @param {object} ev dom对象
         */
        submit: function (ev) {
            ev.preventDefault();
            ev.stopPropagation();
            var id = parseInt($(ev.currentTarget).data('id'));

            $.when(new Model('dtdream.expense.report').exec_workflow(id, 'btn_submit'))
                .fail(function (error) {
                    console.log(error);
                    $.alert(error.data.message);
                })
                .then(function (result) {
                    console.log(result);
                    dd.device.notification.alert({
                        message: "成功提交报销单",
                        title: "提示",//可传空
                        buttonName: "确认",
                        onSuccess : function() {},
                        onFail : function(err) {}
                    });
                    core.bus.trigger('change_screen', {
                        model: 'receipts',
                        action: null,
                        id: null,
                        back:true
                    });
                });
        },
        /**
         * @memberOf Receipts_List
         * @description 催签，执行服务端方法btn_cuiqian
         * @param {object} ev dom对象
         */
        cui: function (ev) {
            ev.preventDefault();
            ev.stopPropagation();

            $.confirm('确定要催签吗?', function () {
                var id = parseInt($(ev.currentTarget).data('id'));
                $.when(new Model('dtdream.expense.report').call_button('btn_cuiqian', [[id]]))
                    .fail(function (err) {
                        $.alert(err.data.message.replace('None', ""));
                    }).then(function (result) {
                        cui_buf[cui_buf.length] = id;
                        $(ev.currentTarget).parent().hide();
                        $.toast("催签完成");
                    });
            });
        },
        /**
         * @memberOf Receipts_List
         * @method init
         * @description 初始化,参考widget.js
         * @param {object} parent 父级传递的参数
         */
        init: function (parent) {
            var self = this;
            self._super(parent);

        },
        /**
         * @memberOf Receipts_List
         * @description 在init方法后执行，具体参考widget.js
         * @param {object}parent 父对象传递回来的参数
         */
        start: function (parent) {
            var self = this;
            self._super(parent);
        },
        /**
         * @memberOf Receipts_List
         * @description 跳转到报销申请明细内容界面
         * @param {object} ev dom对象
         */
        edit_expense_report: function (ev) {
            var id = $(ev.currentTarget).parent().data('id');
            core.bus.trigger('change_screen', {
                        model: 'receipts',
                        action: "edit",
                        id: parseInt(id)
                    });
        },
        /**
         * @memberOf Receipts_List
         * @description 跳转到报销申请明细内容界面
         * @param {object} ev dom对象
         */
        view_expense_report: function (ev) {
            var id = $(ev.currentTarget).parent().data('id');
            core.bus.trigger('change_screen', {
                        model: 'receipts',
                        action: "view",
                        id: parseInt(id)
                    });
        },
        /**
         * @memberOf Receipts_List
         * @description 从服务端加载报销申请数据，每页为20条
         * @param {object} parent 扶对象
         * @returns {jQuery.Deferred}
         */
        load_data: function (parent) {
            var def = new $.Deferred();
            var self = this;
            self.i = 0;
            new Model('dtdream.expense.report')
                .query(['id', 'name', 'state', 'paytype', 'total_invoicevalue', 'paycatelog', 'shoukuanrenxinming', 'work_place',
                    'kaihuhang', 'yinhangkahao', 'expensereason', 'create_uid', 'create_date', 'write_date', 'showcuiqian', 'currentauditperson',
                    'currentauditperson_userid', 'hasauditor', 'is_outtime', 'xingzhengzhuli', 'department_id', 'create_uid_self'])
                .filter(self.options.condition)
                .order_by(['-name'])
                .all({'timeout': 3000, 'shadow': true})
                .then(function (receipts) {
                        console.log(receipts);

                        if (self.i == 0) {
                            dd.biz.navigation.setRight({
                                show: false,//控制按钮显示， true 显示， false 隐藏， 默认true
                            });
                            var states = {
                                'draft': '草稿',
                                'xingzheng': '行政助理审批',
                                'zhuguan': '主管审批',
                                'quanqianren': '权签人审批',
                                'jiekoukuaiji': '接口会计审批',
                                'daifukuan': '待付款',
                                'yifukuan': '已付款',
                                'chuandi1':'纸件在发往行政助理的途中',
                                'chuandi2':'纸件在发往接口会计的途中'
                            }
                            var receipts_drafts=[];
                            var receipts_not_drafts=[];
                            $.each(receipts, function (key, value) {
                                if (value.state == "xingzheng" && value.showcuiqian != 1){
                                    value.state = "chuandi1";
                                } else if (value.state == "jiekoukuaiji" && value.showcuiqian != 2){
                                    value.state = "chuandi2";
                                }
                                value.state_name = states[value.state];
                                value.create_date = value.create_date.substring(0,10);
                                if (value.state == "draft"){
                                    receipts_drafts.push(value);
                                } else {
                                    if (cui_buf.indexOf(value.id) != -1){
                                        value.cui = false;
                                    } else{
                                        value.cui = true;
                                    }
                                    receipts_not_drafts.push(value)
                                }
                            });

                            if (parent.render_data(receipts_drafts, receipts_not_drafts, parent.$el, parent)) {
                                def.resolve();

                            } else {
                                def.reject();
                            }

                            self.i++;

                        }
                    }, function (err, event) {
                        event.preventDefault();
                        def.reject();
                    }
                );
            return def.promise();
        },
        /**
         * @memberOf Receipts_List
         * @description 显示报销申请数据到界面上
         * @param {json} expense_reports 报销申请数据
         * @param ｛object} $el dom对象
         */
        render_data: function (receipts_drafts, receipts_not_drafts, $el) {

            if (receipts_drafts || receipts_not_drafts) {
                var $receipts_info = $(QWeb.render('receipts_list', {
                    'receipts_drafts': receipts_drafts,
                    'receipts_drafts_len': receipts_drafts.length,
                    'receipts_not_drafts': receipts_not_drafts,
                    'receipts_not_drafts_len': receipts_not_drafts.length
                }));

                $el.find('.o_receipts').append($receipts_info);
                Util.log("QWeb end load data", location.href.substring(location.href.lastIndexOf('/')+1));
            }
        },
        /**
         * @memberOf Receipts_List
         * @description 显示待报销列表界面
         * @param {object} el dom对象
         * @param {object} options 参数
         */
        attach: function (el, options) {
            this._super(el, options);
            $('.o_main_bar').show();
            this.load_data(this);
            this.setTitle();
        },
        /**
         * @memberOf Receipts_List
         * @description 跳转至另外一个页面前,清空钉钉页面右上角按钮。
         */
        didDetach: function () {
            dd.biz.navigation.setRight({
                show: false,//控制按钮显示， true 显示， false 隐藏， 默认true
            });
        },
        setTitle: function () {
//            if (!this.title) this.title = "未完成报销申请";
            this._super();
        },

    });

    /**
     * @class Workflow_screen
     * @augments Report_screen
     * @description 待我审批的报销申请界面
     */
    var Approval_List = Receipts_List.extend({
        /**
         * @memberOf Workflow_screen
         * @description 显示待我审批的报销申请
         * @param {object} el dom对象
         * @param {object} options 参数
         */
        attach: function (el, options) {
            var self = this;
            if (!options['condition']) {
                options['condition'] = [['currentauditperson_userid', '=', self.uid]];
            }
            this._super(el, options);
            $('.o_main_bar').show();

            this.load_data(this);
        },
        /**
         *  @memberOf Workflow_screen
         *  @description 设置钉钉界面抬头内容
         */
        setTitle: function () {
//            if (!this.title) this.title = "待我审批的报销申请";
            this._super();
        },
        events: {
            'click .o_approval_receipt': 'approval_expense_report',
        },
        /**
         *  @memberOf Workflow_screen
         *  @description 显示报销申请明细界面
         * @param {object} ev dom对象
         */
        approval_expense_report: function (ev) {
            var id = $(ev.currentTarget).parent().data('id');
            core.bus.trigger('change_screen', {
                        model: 'receipts',
                        action: "approval",
                        id: parseInt(id)
                    });
        },
        /**
         *  @memberOf Workflow_screen
         *  @description 显示待我审批的报销申请列表
         * @param {json} expense_reports 报销申请
         * @param {object} $el dom对象
         * @returns {*}
         */
        render_data: function (receipts_drafts, receipts_not_drafts, $el) {
            var self = this;
            if (receipts_not_drafts) {
                var $approval_info = $(QWeb.render('approval_list', {
                    'approval_Lists': receipts_not_drafts
                }));
                $el.find('.o_receipts').append($approval_info);
                Util.log("QWeb end load data", location.href.substring(location.href.lastIndexOf('/')+1));
            }
        }
    });

    var Log_List = Receipts_List.extend({
        /**
         * @memberOf Workflow_screen
         * @description 显示待我审批的报销申请
         * @param {object} el dom对象
         * @param {object} options 参数
         */
        attach: function (el, options) {
            var self = this;
            this._super(el, options);
            $('.o_main_bar').show();
            this.render_data(this.$el);
        },
        /**
         *  @memberOf Workflow_screen
         *  @description 设置钉钉界面抬头内容
         */
        setTitle: function () {
//            if (!this.title) this.title = "日志";
            this._super();
        },

        /**
         *  @memberOf Workflow_screen
         *  @description 显示待我审批的报销申请列表
         * @param {json} expense_reports 报销申请
         * @param {object} $el dom对象
         * @returns {*}
         */
        render_data: function ($el) {
            var self = this;

            Util.log("QWeb end load data", location.href.substring(location.href.lastIndexOf('/')+1));

            var $log_info = $(QWeb.render('log', {
                'logs': sessionStorage.logBuf.split(';')
            }));
            $el.find('.o_receipts').append($log_info);
        }
    });

    var My_List = BasicScreenWidget.extend({
        /**
         * @memberOf Receipts_List
         * @description 报销申请列表模板名称
         */
        template: 'my',
        /**
         * @memberOf Receipts_List
         * @description 事件
         * @property {method} edit_expense_report 打开报销申请明细内容界面
         * @property {method} tijiao 提交所选择的报销申请
         * @property {method} cuiban 催办所提交的报销申请
         * @property {method} get_next_page 加载下一页的报销申请
         */
        events: {
            'click .item-content': 'view'
        },

        /**
         * @memberOf Receipts_List
         * @description 催签，执行服务端方法btn_cuiqian
         * @param {object} ev dom对象
         */
        view: function (ev) {
            ev.preventDefault();
            ev.stopPropagation();
            if ($(ev.currentTarget).data('item-id') == "create_detail"){
                core.bus.trigger('change_screen', {
                    model: "detail",
                    action: "create",
                    id: null
                });
            } else if($(ev.currentTarget).data('item-id') == "clear_logs"){
                sessionStorage.logBuf = "";
            } else {
                core.bus.trigger('change_screen', {
                    model: $(ev.currentTarget).data('item-id'),
                    action: null,
                    id: null
                });
            }

        },
        /**
         * @memberOf Receipts_List
         * @method init
         * @description 初始化,参考widget.js
         * @param {object} parent 父级传递的参数
         */
        init: function (parent) {
            var self = this;
            self._super(parent);
        },
        /**
         * @memberOf Receipts_List
         * @description 在init方法后执行，具体参考widget.js
         * @param {object}parent 父对象传递回来的参数
         */
        start: function (parent) {
            var self = this;
            self._super(parent);
        },

        /**
         * @memberOf Receipts_List
         * @description 从服务端加载报销申请数据，每页为20条
         * @param {object} parent 扶对象
         * @returns {jQuery.Deferred}
         */
        load_data: function (parent) {
            var self = this;
            new Model('dtdream.expense.report.dashboard')
                .call('retrieve_sales_dashboard', []).then(function (result) {
                parent.render_data(result, parent.$el)
            });
        },
        /**
         * @memberOf Receipts_List
         * @description 显示报销申请数据到界面上
         * @param {json} expense_reports 报销申请数据
         * @param ｛object} $el dom对象
         */
        render_data: function (info, $el) {

            if (info) {
                var $info = $(QWeb.render('my_info', {
                    'info': info,
                    'debug': DEBUG
                }));

                $el.find('.o_my').append($info);

                Util.log("QWeb end load data", location.href.substring(location.href.lastIndexOf('/')+1));
            }
        },
        /**
         * @memberOf Receipts_List
         * @description 显示待报销列表界面
         * @param {object} el dom对象
         * @param {object} options 参数
         */
        attach: function (el, options) {
            this._super(el, options);
            this.rend_navigate_button();
            this.load_data(this);
            this.setTitle();
        },
        rend_navigate_button: function () {
            dd.biz.navigation.setRight({
                show: true,//控制按钮显示， true 显示， false 隐藏， 默认true
                control: true,//是否控制点击事件，true 控制，false 不控制， 默认false
                text: '新增',//控制显示文本，空字符串表示显示默认文本
                iconId: "add",
                onSuccess: function (result) {
                    core.bus.trigger('change_screen', {
                        model: 'detail',
                        action: "create",
                        id: null
                    });
                },
                onFail: function (err) {
                }
            });
        },

        /**
         * @memberOf Receipts_List
         * @description 跳转至另外一个页面前,清空钉钉页面右上角按钮。
         */
        didDetach: function () {
            dd.biz.navigation.setRight({
                show: false,//控制按钮显示， true 显示， false 隐藏， 默认true
            });
        },

        setTitle: function () {
            this._super();
        },

    });

    var Detail_Info = BasicScreenWidget.extend({
    /**
         * @memberOf Expense_detail_screen
         * @member template
         * @description 消费明细详细内容界面模版名称
         */
        template: 'detail_info',
        /**
         * @memberOf Expense_detail_screen
         * @member events
         * @description 事件
         * @property {method} action_button 点击工具栏按钮事件
         * @property {method} on_file_change 上传图片事件
         * @property {method} preview_image 预览图片事件
         * @property {method} delete_image 删除图片事件
         */
        events: {
            'click .tab-item': 'action_button',
            'change .o_uploader_input': 'on_file_change',
            'click .o_uploader_file': 'preview_image',
            'click .o_expense_delete': 'delete_image',
        },
        load_detail: function (parent) {
            $('.o_select_expensecatelog').cascadingDropdown({
                selectBoxes: [
                    {
                        selector: '.o_expensecatelog',
                        disabled: true,
                        source: function (request, response) {
                            $.when(new Model('dtdream.expense.catelog').query().all({'timeout': 3000, 'shadow': true}), parent.options.detail)
                                .fail(function (err) {
                                    var message = "加载数据失败，请检查网络是否正常";
                                    if (err.data && err.data.message) {
                                        message = err.data.message.replace('None', "")
                                    } else if (err.message){
                                        message = err.message;
                                    }
                                    if (isAlert == false) {
                                        isAlert = true;
                                        dd.device.notification.alert({
                                            message: message,
                                            title: "警告",//可传空
                                            buttonName: "确定",
                                            onSuccess: function () {
                                                isAlert = false;
                                                core.bus.trigger('go_back', {});
                                            },
                                            onFail: function (err) {
                                            }
                                        });
                                    }

                                })
                                .then(function (catelog, expense) {
                                    var item_index = 0;
                                    $.map(catelog, function (item, index) {
                                        if (expense && expense[0].expensecatelog && item.id == expense[0].expensecatelog[0]) {
                                            item_index = index;
                                        }
                                    });
                                    response($.map(catelog, function (item, index) {
                                        console.log(item);
                                        return {
                                            label: item.name,
                                            value: item.id,
                                            selected: index == item_index // Select first available option
                                        };
                                    }));

                                    if (expense == 'draft') {
                                        $('.o_expensecatelog').prop('disabled', 'disabled');
                                    } else {
                                        $('.o_expensecatelog').prop('disabled', '');
                                    }
                                });
                        },

                    }, {
                        selector: '.o_expensedetail',
                        requires: ['.o_expensecatelog'],
                        source: function (request, response) {
                            $.when(new Model('dtdream.expense.detail').query()
                                    .filter([['parentid', '=', parseInt($('.o_expensecatelog').val())]])
                                    .all({'timeout': 3000, 'shadow': true}), parent.options.detail)
                                .fail(function (err) {
                                    var message = "加载数据失败，请检查网络是否正常";
                                    if (err.data && err.data.message) {
                                        message = err.data.message.replace('None', "")
                                    } else if (err.message){
                                        message = err.message;
                                    }
                                    if (isAlert == false) {
                                        isAlert = true;
                                        dd.device.notification.alert({
                                            message: message,
                                            title: "警告",//可传空
                                            buttonName: "确定",
                                            onSuccess: function () {
                                                isAlert = false;
                                                core.bus.trigger('go_back', {});
                                            },
                                            onFail: function (err) {
                                            }
                                        });
                                    }
                                })
                                .then(function (detail, expense) {
                                    var item_index = 0;
                                    $.map(detail, function (item, index) {
                                        if (expense && expense[0].expensedetail && item.id == expense[0].expensedetail[0]) {
                                            item_index = index;
                                        }
                                    });
                                    response($.map(detail, function (item, index) {
                                        return {
                                            label: item.name,
                                            value: item.id,
                                            selected: index == item_index, // Select first available option
                                        };
                                    }));
                                });
                        },
                    }],
                onReady: function (event, dropdownData) {
                    console.log(event);
                },
                onChange: function (event, dropdownData) {
                    console.log(event);
                    var tmp = $('.o_expensecatelog').find("option:selected").text();
                    if (tmp == "日常业务费"){
                        $('.o_kehurenshu').css('display','');
                        $('.o_peitongrenshu').css('display','');
                        $('.o_renjunxiaofei').css('display','');
                    } else {
                        $('.o_kehurenshu').css('display','none');
                        $('.o_peitongrenshu').css('display','none');
                        $('.o_renjunxiaofei').css('display','none');
                    }
                },
            });
        },
        load_city: function (parent) {
            $('.o_select_province_city').cascadingDropdown({
                selectBoxes: [
                    {
                        selector: '.o_province',
                        source: function (request, response) {

                            $.when(new Model('res.country.state')
                                    .query()
                                    .filter([['country_id.code', '=', 'CN']])
                                    .all({'timeout': 3000, 'shadow': true}), parent.options.detail)
                                .fail(function (err) {
                                    var message = "加载数据失败，请检查网络是否正常";
                                    if (err.data && err.data.message) {
                                        message = err.data.message.replace('None', "")
                                    } else if (err.message){
                                        message = err.message;
                                    }
                                    if (isAlert == false) {
                                        isAlert = true;
                                        dd.device.notification.alert({
                                            message: message,
                                            title: "警告",//可传空
                                            buttonName: "确定",
                                            onSuccess: function () {
                                                isAlert = false;
                                                core.bus.trigger('go_back', {});
                                            },
                                            onFail: function (err) {
                                            }
                                        });
                                    }
                                })
                                .then(function (province, expense) {
                                    var item_index = 0;
                                    var common_province = ["北京市", "浙江省", "江苏省", "广东省"];
                                    var province_1 = [];
                                    var province_2 = [];
                                    $.map(province, function (item, index) {
                                        var i = common_province.indexOf(item.name);
                                        if (i >= 0){
                                            province_1.push(item);
                                        } else {
                                            province_2.push(item);
                                        }
                                    });

                                    province = province_1.concat(province_2);
                                    $.map(province, function (item, index) {
                                        if (expense && expense[0].province && item.id == expense[0].province[0]) {
                                            item_index = index;
                                        }
                                    });

                                    response($.map(province, function (item, index) {

                                        return {
                                            label: item.name,
                                            value: item.id,
                                            selected: index == item_index // Select first available option
                                        };

                                    }));
                                });
                        },

                    }, {
                        selector: '.o_city',
                        requires: ['.o_province'],
                        source: function (request, response) {
                            $.when(new Model('dtdream.expense.city')
                                    .query()
                                    .filter([['provinceid', '=', parseInt($('.o_province').val())]])
                                    .all({'timeout': 3000, 'shadow': true}), parent.options.detail)
                                .fail(function (err) {
                                    var message = "加载数据失败，请检查网络是否正常";
                                    if (err.data && err.data.message) {
                                        message = err.data.message.replace('None', "")
                                    } else if (err.message){
                                        message = err.message;
                                    }
                                    if (isAlert == false) {
                                        isAlert = true;
                                        dd.device.notification.alert({
                                            message: message,
                                            title: "警告",//可传空
                                            buttonName: "确定",
                                            onSuccess: function () {
                                                isAlert = false;
                                                core.bus.trigger('go_back', {});
                                            },
                                            onFail: function (err) {
                                            }
                                        });
                                    }
                                })
                                .then(function (city, expense) {
                                    var item_index = 0;
                                    $.map(city, function (item, index) {
                                        if (expense && expense[0].city && item.id == expense[0].city[0]) {
                                            item_index = index;
                                        }
                                    });
                                    response($.map(city, function (item, index) {
                                        return {
                                            label: item.name,
                                            value: item.id,
                                            selected: index == item_index, // Select first available option
                                        };
                                    }));
                                });
                        },

                    }]
            });
        },
        /**
         * @memberOf Expense_detail_screen
         * @method delete_image
         * @description 删除图片
         * @param {object} e dom对象
         */
        delete_image: function (e) {
            e.preventDefault();

            if (this.options && this.options.edit_type=="view"){
                e.stopPropagation();
                return;
            }

            var li = e.currentTarget.parentNode.parentNode
            if ($(li).data('id')) {
                $(li).hide();
            } else {
                $(li).detach();
            }

            e.stopPropagation();
        },
        /**
         * @memberOf Expense_detail_screen
         * @description 预览图片
         * @param {object} e dom对象
         */
        preview_image: function (e) {
            e.preventDefault();
            var urls = [];
            $.each(this.$('.o_uploader_file'), function (key, value) {
                var url = value.style.backgroundImage;
                url = url.replace('url(', "")
                url = url.replace(')', "")
                url = url.replace('"', "");
                urls.push(url);
            });
            if (urls.length > 0) {
                var photos = $.photoBrowser({
                    photos: urls,
                    type: 'popup'
                });
                photos.open();
                view_image=true;
            }
        },
        /**
         * @memberOf Expense_detail_screen
         * @description 上传图片
         * @param {object} e dom对象
         */
        on_file_change: function (e) {
            var self = this;
            var file_node = e.target;
            // var file = file_node.files[0];
            $.each(file_node.files, function (key, value) {
                var file = value;
                lrz(file)
                    .then(function (rst) {
                        // 处理成功会执行
                        var $expense_img = $(QWeb.render('detail_img', {'url': rst.base64}));
                        $expense_img.appendTo('.o_expense_img')
                    })
                    .catch(function (err) {
                        // 处理失败会执行
                    })
                    .always(function () {
                        // 不管是成功失败，都会执行
                    });
            });
        },
        /**
         * @memberOf Expense_detail_screen
         * @description 显示消费明细详细内容
         * @param {object} el dom对象
         * @param {object} options 参数
         */
        attach: function (el, options) {
            $('.o_main_bar').hide();
            this._super(el, options);
            var self = this;

            if (options && options.detail_id) {
                $.when(new Model('dtdream.expense.record')
                    .query(['id', 'name', 'expensecatelog', 'customernumber', 'peitongnumber', 'report_ids', 'expensedetail', 'invoicevalue', 'city', 'province', 'currentdate', 'write_date', 'state', 'actiondesc'])
                    .filter([['id', '=', parseInt(options.detail_id)]])
                    .all({'timeout': 3000, 'shadow': true}), this)
                .fail(function (err) {
                    var message = "加载数据失败，请检查网络是否正常";
                    if (err.data && err.data.message) {
                        message = err.data.message.replace('None', "")
                    } else if (err.message){
                        message = err.message;
                    }
                    if (isAlert == false) {
                        isAlert = true;
                        dd.device.notification.alert({
                            message: message,
                            title: "警告",//可传空
                            buttonName: "确定",
                            onSuccess: function () {
                                isAlert = false;
                                core.bus.trigger('go_back', {});
                            },
                            onFail: function (err) {
                            }
                        });
                    }
                })
                .then(
                    function (data, parent) {
                        options['detail'] = data;
                        parent.options = options;
                        parent.load_detail(parent);
                        parent.load_city(parent);
                        parent.init_data(parent);
                    },
                    function (err, event) {
                        event.preventDefault();
                    });
            } else {
                this._super(el, options);
                this.load_detail(this);
                this.load_city(this);
            }

            if (options && options.edit_type=="create") {

                this.$('a[data-item-id=save_create]').css('display', '');
                this.$('a[data-item-id=save_quit]').css('display', '');
                this.$('a[data-item-id=delete]').css('display', 'none');

            } else if (options && options.edit_type=="view"){

                this.$('a[data-item-id=save_create]').css('display', 'none');
                this.$('a[data-item-id=save_quit]').css('display', 'none');
                this.$('a[data-item-id=delete]').css('display', 'none');

                $('.o_expensecatelog').prop('disabled', 'disabled');
                $('.o_expensedetail').prop('disabled', 'disabled');
                this.$('input[data-id=currentdate]').prop('disabled', 'disabled');
                this.$('input[data-id=invoicevalue]').prop('disabled', 'disabled');
                this.$('input[data-id=kehurenshu]').prop('disabled', 'disabled');
                this.$('input[data-id=peitongrenshu]').prop('disabled', 'disabled');
                this.$('.o_province').prop('disabled', 'disabled');
                this.$('.o_city').prop('disabled', 'disabled');
                this.$('.o_uploader_input_wrp').css('display', 'none');
                this.$('.o_uploader_status_content').css('display', 'none');
                this.$('a[data-item-id=save_create]').css('display', 'none');
                this.$('a[data-item-id=save_quit]').css('display', 'none');
            } else if (options && options.edit_type=="edit2") {

                this.$('a[data-item-id=save_create]').css('display', 'none');
                this.$('a[data-item-id=save_quit]').css('display', '');
                this.$('a[data-item-id=delete]').css('display', 'none');

            }else {

                this.$('a[data-item-id=save_create]').css('display', 'none');
                this.$('a[data-item-id=save_quit]').css('display', '');
                this.$('a[data-item-id=delete]').css('display', '');

            }
        },

        init_data: function(self){

            if (self.options) {
                this.options = self.options;
            }

            if (self.options && self.options.detail) {

                this.detail = self.options.detail[0];
                this.$('input[data-id=currentdate]').val(this.detail.currentdate);

                if (self.options.edit_type != "create") {
                    this.$('input[data-id=invoicevalue]').val(this.detail.invoicevalue);
                    this.$('input[data-id=kehurenshu]').val(this.detail.customernumber);
                    this.$('input[data-id=peitongrenshu]').val(this.detail.peitongnumber);
                    this.$('input[data-id=renjunxiaofei]').val(this.detail.invoicevalue / (this.detail.customernumber + this.detail.peitongnumber));
                    if (this.detail.actiondesc == "false"){
                        this.detail.actiondesc = "";
                    }
                    this.$('textarea[data-id=description]').val(this.detail.actiondesc);

                    $.when(
                        new Model('dtdream.expense.record.attachment')
                        .query(['id', 'record_id', 'attachment', 'write_date'])
                        .filter([['record_id', '=', parseInt(this.detail.id)]])
                        .all({'timeout': 3000, 'shadow': true}))
                    .fail(function (err) {
                        $.alert(err.data.message.replace('None', ""));
                    })
                    .then(function (attachments) {
                        console.log(attachments);
                        $.each(attachments, function (key, value) {
                            var url = session.url('/web/image', {
                                model: 'dtdream.expense.record.attachment',
                                id: value.id,
                                field: 'image',
                                unique: (value.write_date || '').replace(/[^0-9]/g, ''),
                            });
                            var $expense_img = $(QWeb.render('detail_img', {url: url, id: value.id}));
                            $expense_img.appendTo('.o_expense_img')
                        });
                    });
                }

                if (self.options.edit_type != "view") {
                    $("input[data-id=invoicevalue]").blur( function(){
                        var total = parseFloat($("input[data-id=invoicevalue]").val());
                        var a = parseInt($("input[data-id=kehurenshu]").val());
                        var b = parseInt($("input[data-id=peitongrenshu]").val());
                        if ( !isNaN(total) && (a + b) >= 1){
                            $("input[data-id=renjunxiaofei]").val(total/(a+b));
                        }
                    });

                    $("input[data-id=peitongrenshu]").blur( function(){
                        var total = parseFloat($("input[data-id=invoicevalue]").val());
                        var a = parseInt($("input[data-id=kehurenshu]").val());
                        var b = parseInt($("input[data-id=peitongrenshu]").val());
                        if ( !isNaN(total) && (a + b) >= 1){
                            $("input[data-id=renjunxiaofei]").val(total/(a+b));
                        }
                    });

                    $("input[data-id=kehurenshu]").blur(function(){
                        var total = parseFloat($("input[data-id=invoicevalue]").val());
                        var a = parseInt($("input[data-id=kehurenshu]").val());
                        var b = parseInt($("input[data-id=peitongrenshu]").val());
                        if ( !isNaN(total) && (a + b) >= 1){
                            $("input[data-id=renjunxiaofei]").val(total/(a+b));
                        }
                    });
                }
            }
        },
        /**
         * @memberOf Expense_detail_screen
         * @description 显示钉钉界面抬头内容
         */
        setTitle: function () {
//            this.title = "消费明细";
//            this._super();
            dd.biz.navigation.setTitle({
                title: "消费明细",//控制标题文本，空字符串表示显示默认文本
                onSuccess: function (result) {
                },
                onFail: function (err) {
                }
            });
        },
        /**
         * @memberOf Expense_detail_screen
         * @param {object} ev dom对象
         * @property {string} cancel 取消编辑后，返回消费明细列表界面
         * @property {string} save 保存消费明细后，返回消费明细列表界面
         * @property {string} delete 删除消费明细后，返回消费明细列表接 main
         */
        action_button: function (ev) {
            ev.preventDefault();
            ev.stopPropagation();

            var self = this;
            if ($(ev.currentTarget).data('item-id') == 'cancel') {

                //history.go(-1);
                $.confirm('您确定返回吗?',
                    function () {
                        core.bus.trigger('go_back', {});
                    },
                    function () {
                    }
                );

                return;
            }

            if ($(ev.currentTarget).attr("disabled") == "disabled"){
                return;
            }

            if ($(ev.currentTarget).data('item-id') == 'save_create' || $(ev.currentTarget).data('item-id') == 'save_quit') {

                var expense_detail = {
                    'expensecatelog': parseInt(this.$('.o_expensecatelog').val()),
                    'expensedetail': parseInt(this.$('.o_expensedetail').val()),
                    'invoicevalue': parseFloat(this.$('input[data-id=invoicevalue]').val()),
                    'currentdate': this.$('input[data-id=currentdate]').val(),
                    'province': parseInt(this.$('.o_province').val()),
                    'city': parseInt(this.$('.o_city').val()),
                    'actiondesc': this.$('textarea[data-id=description]').val(),
                };

                if ($('.o_expensecatelog').find("option:selected").text() == "日常业务费"){
                    expense_detail['customernumber'] = parseInt(this.$('input[data-id=kehurenshu]').val());
                    expense_detail['peitongnumber'] = parseInt(this.$('input[data-id=peitongrenshu]').val());
                    var tmp = expense_detail['customernumber'] + expense_detail['peitongnumber'];
                    if ( isNaN(tmp) || tmp <= 0 ) {
                        $.toast('客户人数和陪同人数之和不可以小于等于0');
                        this.$('input[data-id=kehurenshu]').focus();
                        return;
                    }
                }

                if (!expense_detail.expensecatelog || !expense_detail.expensedetail) {
                    $.toast('请输入费用明细');
                    return;
                }

                if (!expense_detail.currentdate) {
                    $.toast('请输入发生日期');
                    this.$('input[data-id=currentdate]').focus();
                    return;
                }

                if (!$.isNumeric(expense_detail.invoicevalue)) {
                    $.toast('费用金额应该为数字');
                    this.$('input[data-id=invoicevalue]').focus();
                    return;
                }

                if (!expense_detail.province) {
                    $.toast('请选择省份');
                    return;
                }

                if (!expense_detail.city) {
                    $.toast('请选择发生城市');
                    return;
                }

                var def = new $.Deferred();
                ev.detail = self.detail;

                // $.showIndicator();

                if (this.options.edit_type == "edit" || this.options.edit_type == "edit2") {
                    $.when(new Model('dtdream.expense.record').call('read', [[parseInt(self.detail.id)], ['id', 'write_date']]), this.options)
                    .fail(function (err) {
                        $.alert(err.data.message.replace('None', ""));
                    })
                    .then(function (records, options) {
                        if (records) {
                            if (records[0].write_date == ev.detail.write_date) {
                                var attachment_ids = []
                                var img_count = 0;
                                $.each(self.$('.o_uploader_status'), function (key, value) {
                                    if (!$(value).data("id")) {
                                        var url = value.style.backgroundImage;
                                        url = url.replace('url(', "")
                                        url = url.replace(')', "")
                                        url = url.replace('"', "");
                                        url = url.replace("data:image/jpeg;base64,", "")
                                        attachment_ids.push([0, 0, {
                                            'image': url,
                                        }])
                                    }
                                    if ($(value).is(":hidden")) {
                                        attachment_ids.push([2, parseInt($(value).data('id'))])
                                    } else {
                                        img_count++;
                                    }
                                });
// update by g0335 for resolve ODOO-763
//                                if ($('.o_expensedetail').find("option:selected").text() != "出差补助" && img_count == 0) {
//                                    $.toast('请上传发票附件');
//                                    return;
//                                }

                                if (attachment_ids.length > 0) {
                                    expense_detail.attachment_ids = attachment_ids;
                                }

                                $('a[data-item-id=save_create]').attr({"disabled":"disabled"});
                                $('a[data-item-id=save_quit]').attr({"disabled":"disabled"});
                                $('a[data-item-id=cancel]').attr({"disabled":"disabled"});
                                $.when(new Model('dtdream.expense.record').call('write', [[parseInt(self.detail.id)], expense_detail]), expense_detail, options)
                                    .fail(function (err) {
                                        $('a[data-item-id=save_create]').removeAttr("disabled");
                                        $('a[data-item-id=save_quit]').removeAttr("disabled");
                                        $('a[data-item-id=cancel]').removeAttr("disabled");
                                        $.alert(err.data.message.replace('None', ""));
                                    })
                                    .then(function (result, expense_detail, options) {
                                        // $.hideIndicator();
                                        $.toast("保存成功");
                                        core.bus.trigger('go_back', {});
                                    });
                            }
                            else {
                                $.toast('数据已经被修改,请刷新数据。');
                                core.bus.trigger('change_screen', {
                                    model: 'detail',
                                    action:null,
                                    id: null
                                });
                            }
                        } else {
                            $.toast('没有找到对应的纪录。');
                            core.bus.trigger('change_screen', {
                                model: 'detail',
                                action:null,
                                id: null
                            });
                        }

                        def.resolve();
                    });
                }

                if (this.options.edit_type == "create") {
                    var attachment_ids = [];
                    var img_count = 0;
                    $.each(self.$('.o_uploader_status'), function (key, value) {
                        if (!$(value).data("id")) {
                            var url = value.style.backgroundImage;
                            url = url.replace('url(', "")
                            url = url.replace(')', "")
                            url = url.replace('"', "");
                            url = url.replace("data:image/jpeg;base64,", "")
                            attachment_ids.push([0, 0, {
                                'image': url,
                            }])
                        }
                        if ($(value).is(":hidden")) {
                            attachment_ids.push([2, parseInt($(value).data('id'))])
                        } else {
                            img_count++;
                        }
                    });
// update by g0335 for resolve ODOO-763
//                    if ($('.o_expensedetail').find("option:selected").text() != "出差补助" && img_count == 0) {
//                        $.toast('请上传发票附件');
//                        return;
//                    }

                    if (attachment_ids.length > 0) {
                        expense_detail.attachment_ids = attachment_ids;
                    }

                    $('a[data-item-id=save_create]').attr({"disabled":"disabled"});
                    $('a[data-item-id=save_quit]').attr({"disabled":"disabled"});
                    $('a[data-item-id=cancel]').attr({"disabled":"disabled"});
                    $.when(new Model('dtdream.expense.record').call('create', [expense_detail]))
                    .fail(function(error){
                        $('a[data-item-id=save_create]').removeAttr("disabled");
                        $('a[data-item-id=save_quit]').removeAttr("disabled");
                        $('a[data-item-id=cancel]').removeAttr("disabled");
                        $.alert(error.data.message);
                    })
                    .then(function (data) {
                        $.toast("保存成功");
                        if ($(ev.currentTarget).data('item-id') == 'save_create') {
                            core.bus.trigger('change_screen', {
                                model: 'detail',
                                action:'create',
                                id:data
                            });
                        } else if ($(ev.currentTarget).data('item-id') == 'save_quit') {
                            core.bus.trigger('change_screen', {
                                model: 'detail',
                                action:null,
                                id: null
                            });
                        }
                    });
                }

            }

            if ($(ev.currentTarget).data('item-id') == 'delete') {
                var def = new $.Deferred();
                ev.detail = self.detail;
                new Model('dtdream.expense.record').call('read', [[self.detail.id], ['id', 'write_date', 'report_ids']]).then(function (records) {
                    if (records) {
                        if (records[0].write_date == ev.detail.write_date) {
                            $.confirm('您确定要删除此条记录吗?',
                                function () {
                                    $.when(new Model('dtdream.expense.record').call('unlink', [[self.detail.id]]))
                                    .fail(function (err) {
                                        $.alert(err.data.message.replace('None', ""));
                                    })
                                    .then(function () {
                                        $.toast("删除成功");
                                        core.bus.trigger('change_screen', {
                                            model: 'detail',
                                            action:null,
                                            id: null
                                        });
                                    });
                                },
                                function () {

                                }
                            );

                        } else {
                            $.toast('数据已经被修改,请刷新数据。');
                            core.bus.trigger('change_screen', {
                                model: 'detail',
                                action:null,
                                id: null
                            });
                        }
                    } else {
                        $.toast('没有找到对应的纪录,删除失败。');
                        core.bus.trigger('change_screen', {
                            model: 'detail',
                            action:null,
                            id: null
                        });
                    }
                    def.resolve();
                });
            }
        }
    });

    /**
     * @class Report_detail_screen
     * @description 报销申请明细界面
     */
    var Receipt_Info = BasicScreenWidget.extend({
        /**
         * @memberOf Report_detail_screen
         * @description 报销申请明细界面模板名称
         */
        template: 'receipts_info',
        /**
         * @memberOf Report_detail_screen
         * @description 事件
         * @property {method} action_button 工具栏事件
         * @property {method} action_paytype 选择支付方式事件
         * @property {method} action_paycatelog 选择支付类别事件
         * @property {method} add_expense 添加报销申请事件
         * @property {method} add_benefitdep 添加分摊比例事件
         * @property {method} get_department 获取分摊比例所属部门事件
         * @property {method} select_department 打开部门界面事件
         * @property {method} delete_benefitdep 删除分摊比例事件
         * @property {method} delete_detail 删除消费明细事件
         * @property {method} edit_benefitdep 编辑分摊比例事件
         * @property {method} select_reject_state 选择拒绝申请后，接收人事件
         * @property {method} search_detail 搜索报销申请事件
         * @property {method} add_chuchai 添加出差明细事件
         * @property {method} select_chuchai 选择出差明细事件
         * @property {methdd} delete_report_chuchai 删除出差明细事件
         * @property {method} search_chuchai 选择出差明细事件
         * @property {method} get_xingzhengzhuli 打开行政助理选择界面
         * @property {method} search_department 搜索部门
         */
        events: {
            'click .tab-item': 'action_button',

            'click input[data-id=paytype]': 'action_paytype',
            'click input[data-id=paycatelog]': 'action_paycatelog',

            'click .o_add_expense': 'add_detail',
            'click .o_delete_expense': 'delete_detail',
            'keyup .o_search_expense_record': 'search_detail',
            'click .o_report_expense_record': 'view_detail',

            'click .o_add_benefitdep': 'add_benefitdep',
            'click .o_benefitdep_list': 'edit_benefitdep',
            'click .o_delete_benefitdep': 'delete_benefitdep',
            'click input[data-name=dep_name]': 'get_department',
            'keyup .o_search_department': 'search_department',
            'click .o_select_dep': 'select_department',

            'click .o_add_chuchai': 'add_chuchai',
            'click .o_select_chuchai': 'select_chuchai',
            'click .o_delete_report_chuchai': 'delete_chuchai',
            'keyup .o_search_chuchai': 'search_chuchai',

            'click .o_reject_state': 'select_reject_state'


//            'click input[data-id=xingzhengzhuli]': 'get_xingzhengzhuli',
//            'keyup .o_search_xingzengzhuli': 'search_xingzhengzhuli',
//            'click .o_select_xingzhengzhuli': 'select_xingzhengzhuli',
        },

        load_xingzhengzhuli: function (parent) {
            $('.o_select_xingzhengzhuli').cascadingDropdown({
                selectBoxes: [
                    {
                        selector: '.o_xingzhengzhuli',
                        expense_report: parent.options.expense_report[0],
                        source: function (request, response) {

                            $.when(new Model('hr.department').query('id', 'name', 'assitant_id')
                                .filter([['id', '=', parent.options.expense_report[0].department_id[0]]])
                                .all({'timeout': 3000, 'shadow': true}), parent.options.expense_report[0])
                                .fail(function (err) {
                                    $.alert(err.data.message.replace('None', ""));
                                })
                                .then(function (dep, expense_report) {
                                    var condition = [];

                                    if (dep.length > 0) {
                                        $.each(dep, function (key, value) {
                                            condition.push(['id', 'in', value.assitant_id])
                                        });
                                    }

                                    $.when(new Model('hr.employee').query(['id', 'name',])
                                        .filter(condition)
                                        .all({'timeout': 3000, 'shadow': true}), expense_report)
                                        .fail(function (err) {
                                            $.alert(err.data.message.replace('None', ""));
                                        })
                                        .then(function (xingzhengzhuli) {
                                            var item_index = 0;
                                            $.map(xingzhengzhuli, function (item, index) {
                                                if (expense_report && expense_report.xingzhengzhuli && item.id == expense_report.xingzhengzhuli[0]) {
                                                    item_index = index;
                                                }
                                            });
                                            response($.map(xingzhengzhuli, function (item, index) {
                                                return {
                                                    label: item.name,
                                                    value: item.id,
                                                    selected: index == item_index // Select first available option
                                                };
                                            }));

                                            if (expense_report.state != 'draft') {
                                                $('.o_xingzhengzhuli').prop('disabled', 'disabled');
                                            } else {
                                                $('.o_xingzhengzhuli').prop('disabled', '');
                                            }
                                        });
                                });
                        },

                    }]
            });
        },

        /**
         * @memberOf Report_detail_screen
         * @description 搜索消费明细
         * @param {object} ev dom对象
         */
        search_detail: function (ev) {
            if (ev.keyCode == "13") {
                this.$('.o_report_expense').empty();

                this.load_details(this);
            }
        },

        /**
         * @memberOf Report_detail_screen
         * @description 删除消费明细
         * @param {object} e dom对象
         */
        delete_detail: function (e) {
            e.preventDefault();
            var li = e.currentTarget.parentNode.parentNode;
            if ($(li).data('id')) {
                $(li).hide();
            } else {
                $(li).detach();
            }

            e.stopPropagation();
        },

        /**
         * @memberOf Report_detail_screen
         * @description 添加消费明细
         * @param {object} ev dom对象
         */
        add_detail: function (ev) {
            ev.preventDefault();
            var self = this;
            self.load_details();
            $.popup('.popup-expense');

        },

        view_detail: function (ev) {
            var id = $(ev.currentTarget).data('id');

            var action = ""
            if (this.options['edit_type'] == "edit"){
                action = "edit2";
            } else {
                action = "view";
            }

            core.bus.trigger('change_screen', {
                                model: 'detail',
                                action: action,
                                id:parseInt(id)
                            });
        },

        /**
         * @memberOf Report_detail_screen
         * @description 从服务端获取消费明细列表
         */
        load_details: function () {
            var self = this;
            var old_expense_ids = [];

            $.each(self.$('.o_report_expense_record'), function (key, value) {
                var id = parseInt($(value).data('id'));
                if (id) {
                    if (!$(value).is(":hidden")) {
                        old_expense_ids.push(id)
                    }
                }
            });

            var condition = [];
            var value = $('.o_search_expense_record').val()
            if (value) {
                condition.push('|', ['expensecatelog', 'ilike', value], ['expensedetail', 'ilike', value]);
            }

            condition.push(['create_uid', '=', this.uid], ['report_ids', '=', false], ['id', 'not in', old_expense_ids]);

            var def = new $.Deferred();
            new Model('dtdream.expense.record')
                .query(['id', 'name', 'expensecatelog', 'report_ids', 'state', 'expensedetail','shibaoamount', 'invoicevalue', 'city', 'province', 'currentdate', 'write_date'])
                .filter(condition)
                .all({'timeout': 3000, 'shadow': true})
                .then(function (expense_records) {
                        self.search_expense_records = expense_records;
                        if (self.render_details_screen(expense_records, self.$('.o_report_expense'))) {
                            def.resolve();
                        } else {
                            def.reject();
                        }
                    }, function (err, event) {
                        event.preventDefault();
                        def.reject();
                    }
                );

        },
        /**
         * @memberOf Report_detail_screen
         * @description 显示消费明细
         * @param {json} expense_records 消费明细
         * @param {object} $el dom对象
         */
        render_details_screen: function (expense_records, $el) {
            $el.html("");
            for (var i in expense_records) {
                if (expense_records[i].expensedetail[1].length>15){
                    expense_records[i].expensedetail[1] = expense_records[i].expensedetail[1].substring(0, 12) + "...";
                }
            }
            var $expense_records = $(QWeb.render('receipts_search_detail_list', {'expense_records': expense_records}));
            $el.prepend($expense_records);
            // $users.appendTo('.o_expense');
        },

        /**
         * @memberOf Report_detail_screen
         * @description 搜索消费明细
         * @param {object} ev dom对象
         */
        search_department: function (ev) {
            if (ev.keyCode == "13") {
                this.$('.o_report_department').empty();
                this.get_department(this);
            }
        },

        /**
         * @memberOf Report_detail_screen
         * @description 搜索出差明细
         * @param {object} ev dom对象
         */
        search_chuchai: function (ev) {
            if (ev.keyCode == "13") {
                this.$('.o_report_chuchai').empty();
                this.load_chuchai(this);
            }
        },
        /**
         * @memberOf Report_detail_screen
         * @description 删除出差明细
         * @param {object} e dom对象
         */
        delete_chuchai: function (e) {
            e.preventDefault();
            var li = e.currentTarget.parentNode.parentNode;
            if ($(li).data('id')) {
                $(li).hide();
            } else {
                $(li).detach();
            }

            e.stopPropagation();
        },
        /**
         * @memberOf Report_detail_screen
         * @description 选择出差明细
         * @param {object} ev dom对象
         */
        select_chuchai: function (ev) {
            ev.preventDefault();

        },
        /**
         * @memberOf Report_detail_screen
         * @description 添加出差明细
         * @param {object} ev dom对象
         */
        add_chuchai: function (ev) {
            ev.preventDefault();
            var self = this;
            self.load_chuchai();
            $.popup('.popup-chuchai');

        },
        /**
         * @memberOf Report_detail_screen
         * @description 从服务端加载出差明细数据
         * @param {object} parent 父对象
         */
        load_chuchai: function (parent) {
            var self = this;
            var old_chuchai_ids = [];
            // if (self.chuchai_ids) {
            //     $.each(self.chuchai_ids, function (key, value) {
            //         old_chuchai_ids.push(parseInt(value.id));
            //     });
            // }

            $.each(self.$('.o_report_chuchai_id'), function (key, value) {
                var id = parseInt($(value).data('id'));
                if (id) {
                    if (!$(value).is(":hidden")) {
                        old_chuchai_ids.push(id)
                    }
                }
            });

            var condition = [];
            var value = $('.o_search_chuchai').val()
            if (value) {
                condition.push('|', '|', ['startaddress', 'ilike', value], ['endaddress', 'ilike', value], ['reason', 'ilike', value]);
            }
            condition.push(['create_uid', '=', self.uid], ['id', 'not in', old_chuchai_ids], ['travel_id.state', '=', '99']);
            //if(old_chuchai_ids.length>0) condition.push(['id', 'not in ', old_chuchai_ids]);

            var def = new $.Deferred();
            new Model('dtdream.travel.journey')
                .query(['id', 'starttime', 'endtime', 'startaddress', 'endaddress', 'reason'])
                .filter(condition)
                .order_by('-starttime')
                .all({'timeout': 3000, 'shadow': true})
                .then(function (chuchai_ids) {
                        self.search_chuchai_ids = chuchai_ids;
                        if (self.render_chuchai_screen(chuchai_ids, self.$('.o_report_chuchai'))) {
                            def.resolve();
                        } else {
                            def.reject();
                        }
                    }, function (err, event) {
                        event.preventDefault();
                        def.reject();
                    }
                );
        },
        /**
         * @memberOf Report_detail_screen
         * @description 显示出差明细界面
         * @param {json} chuchai_ids 出差明细
         * @param {object} $el dom对象
         */
        render_chuchai_screen: function (chuchai_ids, $el) {
            $el.html("");
            var $chuchai_ids = $(QWeb.render('receipts_search_chuchai_list', {'chuchai_ids': chuchai_ids}));
            $el.prepend($chuchai_ids);
        },

        /**
         * @memberOf Report_detail_screen
         * @description 编辑费用分摊比例
         * @param ｛object} e dom对象
         * @returns {boolean}
         */
        edit_benefitdep: function (e) {
            e.preventDefault();

            if (this.options.expense_report[0].state != 'draft') return false;

            var self = this;
            var id = $(e.currentTarget).data('id');
            var name = $(e.currentTarget).data('name');
            var sharepercent = $(e.currentTarget).data('sharepercent');
            var dep_name = $(e.currentTarget).find('.item-title').html();

            self.$('.o_benefitdep_form').data('id', id);
            self.$('.o_benefitdep_form').data('edit-type', "edit");
            self.$('input[data-name=dep_name]').val(dep_name);
            self.$('input[data-name=dep_name]').data('id', name);
            self.$('input[data-id=sharepercent]').val(sharepercent);

            $.popup('.popup-benefitdep');

        },

        /**
         * @memberOf Report_detail_screen
         * @description 删除费用分摊比例
         * @param {object} e dom对象
         */
        delete_benefitdep: function (e) {
            e.preventDefault();
            var li = e.currentTarget.parentNode;
            if ($(li).data('id') > 0) {
                $(li).hide();
            } else {
                $(li).detach();
            }

            e.stopPropagation();
        },
        /**
         * @memberOf Report_detail_screen
         * @description 选择部门
         * @param {object} e dom对象
         */
        select_department: function (e) {
            e.preventDefault();
            e.stopPropagation();
            var self = this;
            var id = $(e.currentTarget).data('id');
            if (self.departments) {
                $.each(self.departments, function (key, value) {
                    if (value.id == id) {
                        $('input[data-name=dep_name]').val(value.name);
                        $('input[data-name=dep_name]').data('id', value.id);
                    }
                });
            }

            self.$('.o_report_department').empty();
            $.popup('.popup-benefitdep');
        },
        /**
         * @memberOf Report_detail_screen
         * @description 从服务端获取部门列表
         * @param {object} e dom对象
         */
        get_department: function (e) {

            var self = this;
            var def = $.Deferred();
            var old_dep_ids = [];
            // if (self.benefitdep_records) {
            //     $.each(self.benefitdep_records, function (key, value) {
            //         old_dep_ids.push(value.name[0])
            //     })
            // }

            $.each(self.$('.o_benefitdep_list'), function (key, value) {
                var name = $(value).data('name');
                if (!$(value).is(":hidden")) {
                    old_dep_ids.push(name);
                }
            });

            var condition = [['id', 'not in', old_dep_ids]];
            var value = $('.o_search_department').val()
            if (value) {
                condition.push(['name', 'ilike', value]);
            }

            var def = new $.Deferred();
            new Model('hr.department').query(['id', 'name',])
                .filter(condition)
                .all({'timeout': 3000, 'shadow': true})
                .then(function (depatments) {
                    var department_ids = [];
                    self.departments = depatments;
                    $.each(depatments, function (key, value) {
                        department_ids.push(value.id);
                    });
                    $.when(new Model('hr.department').call('name_get', [department_ids]), depatments)
                    .fail(function (err) {
                        $.alert(err.data.message.replace('None', ""));
                    })
                    .then(function (record, depatments) {
                        $.each(depatments, function (key, value) {
                            $.each(record, function (key1, value1) {
                                if (value.id == value1[0]) {
                                    value.name = value1[1];
                                }
                            })
                        })

                        if (self.render_department_screen(depatments, self.$('.o_report_department'))) {
                            def.resolve();
                        } else {
                            def.reject();
                        }
                    })
                }, function (err, event) {
                    event.preventDefault();
                    def.reject();
                });

            $.popup('.popup-department');

            dd.biz.navigation.setRight({
                show: true,//控制按钮显示， true 显示， false 隐藏， 默认true
                control: true,//是否控制点击事件，true 控制，false 不控制， 默认false
                text: '取消',//控制显示文本，空字符串表示显示默认文本
                onSuccess: function (result) {

                    self.$('.o_report_department').empty();
                    $.popup('.popup-benefitdep');
                    dd.biz.navigation.setRight({
                        show: true,//控制按钮显示， true 显示， false 隐藏， 默认true
                        control: false,
                    });
                },
                onFail: function (err) {
                }
            });

        },
        /**
         * @memberOf Report_detail_screen
         * @description 显示部门列表
         * @param {json} departments 部门列表
         * @param {object} $el dom 对象
         */
        render_department_screen: function (departments, $el) {
            $el.html("");
            var $departments = $(QWeb.render('receipts_search_dep', {'departments': departments}));
            $el.prepend($departments);

        },
        /**
         * @memberOf Report_detail_screen
         * @description 添加费用分摊比例
         * @param {object} ev dom对象
         */
        add_benefitdep: function (ev) {
            ev.preventDefault();
            $.popup('.popup-benefitdep');
            self.$('.o_benefitdep_form').data('edit-type', "create");
            self.$('input[data-name=dep_name]').val("");
            self.$('input[data-id=sharepercent]').val("");

        },

        /**
         * @memberOf Report_detail_screen
         * @description 选择驳回节点
         * @param {object} e dom对象
         */
        select_reject_state: function (e) {
            var self = this;
            var value = self.expense_report.state;
            var state = self.$('.o_reject_state')
            var sqr = {
                text: '申请人',
                bold: true,
                color: 'danger',
                onClick: function () {
                    state.data('id', 'draft');
                    state.val('申请人');
                    $.popup('.popup-reject')
                }
            }

            var xzzl = {
                text: '行政助理',
                bold: true,
                color: 'danger',
                onClick: function () {
                    state.data('id', 'xingzheng');
                    state.val('行政助理');
                    $.popup('.popup-reject')
                }
            }

            var zg = {
                text: '主管',
                bold: true,
                color: 'danger',
                onClick: function () {
                    state.data('id', 'zhuguan');
                    state.val('主管');
                    $.popup('.popup-reject')
                }
            }

            var qqr = {
                text: '权签人',
                bold: true,
                color: 'danger',
                onClick: function () {
                    state.data('id', 'quanqianren');
                    state.val('权签人');
                    $.popup('.popup-reject')
                }
            }

            var items = [{
                text: '请选择',
                label: true
            },];
            if (value == "xingzheng") {
                items.push(sqr);
            }
            if (value == "zhuguan") {
                items.push(sqr, xzzl);
            }
            if (value == "quanqianren") {
                items.push(sqr, xzzl, zg);
            }

            if (value == "jiekoukuaiji") {
                items.push(sqr, xzzl, zg, qqr);
            }

            var buttons1 = items;
            var buttons2 = [
                {
                    text: '取消',
                    bg: 'danger',
                    onClick: function () {
                        $.popup('.popup-reject');
                    }
                }
            ];
            var groups = [buttons1, buttons2];
            $.actions(groups);
        },

        /**
         * @memberOf Report_detail_screen
         * @description 工具栏列表事件
         * @property {string} sumbit_benefitdep 保存费用分摊比例
         * @property {string} cancel_add_benefitdep 取消保存费用分摊比例
         * @property {string} cancel_add_chuchai 取消保存费用分摊比例
         * @property {string} add_chuchai 保存出差明细
         * @property {string} cancel_add_expense 取消保存出差明细
         * @property {string} add_detail 保存出差明细
         * @property {string} cancel 取消保存报销申请,返回报销申请界面
         * @property {string} save 保存报销申请,返回报销申请界面
         * @property {string} delete 报销爆笑申请,返回报销申请界面
         * @property {string} qianshou 签收文件后，返回报销申请界面
         * @property {string} confirm_pay 付款后，返回报销申请界面
         * @property {string} accept 同意审批,返回报销申请界面
         * @property {string} reject 打开拒绝审批界面
         * @property {string} cancel_reject 取消拒绝审批
         * @property {string} sumbit_reject 确认拒绝审批
         * @param {object} parent 父对象
         */
        action_add_benefitdep: function(parent){

            var self = this;
            var edit_type = self.$('.o_benefitdep_form').data('edit-type');

            if (!self.$('input[data-name=dep_name]').data('id')) {
                dd.device.notification.alert({
                    message: "请选择部门",
                    title: "提示",//可传空
                    buttonName: "确定",
                    onSuccess: function () {
                        //onSuccess将在点击button之后回调
                        /*回调*/
                    },
                    onFail: function (err) {
                    }
                });
                return;
            }

            var percent = self.$('input[data-id=sharepercent]').val();

            if (!$.isNumeric(percent)) {
                dd.device.notification.alert({
                    message: "分配比例必须为数字",
                    title: "提示",//可传空
                    buttonName: "确定",
                    onSuccess: function () {
                        //onSuccess将在点击button之后回调
                        /*回调*/
                    },
                    onFail: function (err) {
                    }
                });
                return;
            }

            if (percent <= 0 || percent > 100) {
                dd.device.notification.alert({
                    message: "分配比例必须在0和100之间",
                    title: "提示",//可传空
                    buttonName: "确定",
                    onSuccess: function () {
                        //onSuccess将在点击button之后回调
                        /*回调*/
                    },
                    onFail: function (err) {
                    }
                });
                return;
            }

            if (edit_type == 'edit') {
                var id = self.$('.o_benefitdep_form').data('id');
                var benefit = $('.o_benefitdep_list[data-id=' + id + ']');
                benefit.attr('data-name', self.$('input[data-name=dep_name]').data('id'));
                benefit.attr('data-sharepercent', self.$('input[data-id=sharepercent]').val());

                benefit.find('.item-title').html(self.$('input[data-name=dep_name]').val());
                benefit.find('.pull-center').html(self.$('input[data-id=sharepercent]').val() + "%");
            }

            if (edit_type == 'create') {
                var dep_id = self.$('input[data-name=dep_name]').data('id');
                var dep_name = self.$('input[data-name=dep_name]').val();
                var sharepercent = self.$('input[data-id=sharepercent]').val();
                var benefitdeps = [{
                    id: -new Date().getTime(),
                    name: [dep_id, dep_name],
                    sharepercent: sharepercent
                }]
                self.rend_benefitdep_detail(benefitdeps, self.$el);
            }

            self.$('input[data-name=dep_name]').val("");
            self.$('input[data-name=dep_name]').data('id', "");
            self.$('input[data-id=sharepercent]').val("");

            $.closeModal();
            self.$('.o_report_benefitdep').empty();
        },

        action_cancel_benefitdep: function(parent){
            var self = this;
            $.closeModal();
            self.$('.o_report_benefitdep').empty();
        },

        action_add_chuchai: function(parent){
            var self = this;
            var selected_chuchai = [];
            $.each(this.$('input[name=ck_report_chuchai]'), function (key, value) {
                if (value.checked) {
                    if (self.search_chuchai_ids) {
                        $.each(self.search_chuchai_ids, function (key_expense, value_chuchai) {
                            if (value_chuchai.id == $(value).data('id')) {
                                selected_chuchai.push(value_chuchai);
                                self.chuchai_ids.push(value_chuchai);
                            }
                        })
                    }
                }
            });

            if (selected_chuchai.length > 0) {
                self.rend_chuchai_detail(selected_chuchai, self.$el);
                $.closeModal('.popup-chuchai');
                self.$('.o_report_chuchai').empty();
            } else {
                $.toast('没有选择出差申请')
            }
        },

        action_cancel_chuchai: function(parent){
            var self = this;
            $.closeModal('.popup-chuchai');
            self.$('.o_report_chuchai').empty();
        },

        action_add_detail: function(parent){
            var self = this;
            var selected_expens = [];
            $.each(this.$('input[name=ck_report_expense]'), function (key, value) {
                if (value.checked) {
                    if (self.search_expense_records) {
                        $.each(self.search_expense_records, function (key_expense, value_expense) {
                            if (value_expense.id == $(value).data('id')) {
                                selected_expens.push(value_expense);
                                self.expense_records.push(value_expense);
                            }
                        })
                    }
                }
            });

            if (selected_expens.length > 0) {
                self.rend_expense_detail(selected_expens, self.$el);
                $.closeModal('.popup-expense');
                self.$('.o_report_expense').empty();
            } else {
                $.toast('没有选择费用明细')
            }
        },

        action_cancel_detail: function(parent){
            var self = this;
            $.closeModal('.popup-expense');
            self.$('.o_report_expense').empty();
        },

        action_delete: function(parent){
            var self = this;
            var def = new $.Deferred();
            parent.expense_report = self.expense_report;
            new Model('dtdream.expense.report').call('read', [[self.expense_report.id], ['id', 'write_date', 'report_ids']]).then(function (records) {
                if (records) {
                    if (records[0].write_date == parent.expense_report.write_date) {
                        $.confirm('您确定要删除此条记录吗?',
                            function () {
                                $.when(new Model('dtdream.expense.report').call('unlink', [[self.expense_report.id]]))
                                .fail(function (err) {
                                    $.alert(err.data.message.replace('None', ""));
                                })
                                .then(function () {
                                    $.toast("删除成功");
                                    core.bus.trigger('change_screen', {
                                        model: 'receipts',
                                        action: null,
                                        id: null
                                    });

                                });
                            },
                            function () {

                            }
                        );

                    } else {
                        $.toast('数据已经被修改,请刷新数据。');
                        core.bus.trigger('change_screen', {
                            model: 'receipts',
                            action: null,
                            id: null
                        });
                    }
                } else {
                    $.toast('没有找到对应的纪录,删除失败。');
                    core.bus.trigger('report', {
                        model: 'receipts',
                        action: null,
                        id: null
                    });
                }
                def.resolve();
            });
        },

        action_save: function(parent){
            var self = this;
            var xingzhengzhuli_id = this.$('.o_xingzhengzhuli').val();
            if (!xingzhengzhuli_id) {
                $.toast('请选择行政助理');
                this.$('.o_xingzhengzhuli').focus();
                return;
            }

            var chuchai_ids = [];
            $.each(self.$('.o_report_chuchai_id'), function (key, value) {
                var id = parseInt($(value).data('id'));
                if (id) {
                    if ($(value).is(":hidden")) {
                        chuchai_ids.push([3, id]);
                    } else {
                        chuchai_ids.push([4, id]);
                    }
                }
            });

            var expense_ids = [];
            $.each(self.$('.o_report_expense_record'), function (key, value) {
                var id = parseInt($(value).data('id'));
                if (id) {
                    if ($(value).is(":hidden")) {
                        expense_ids.push([3, id]);
                    } else {
                        expense_ids.push([4, id]);
                    }
                }
            });

            var benefitdep_ids = [];
            var sum_shaerpercent = 0;
            $.each(self.$('.o_benefitdep_list'), function (key, value) {

                var id = parseInt($(value).data('id'));
                var name = $(value).data('name');
                var sharepercent = $(value).data('sharepercent');

                if (id > 0) {
                    if ($(value).is(":hidden")) {
                        benefitdep_ids.push([2, id]);
                    } else {
                        benefitdep_ids.push([1, id, {
                            name: name,
                            sharepercent: sharepercent,
                        }]);
                        sum_shaerpercent += parseFloat(sharepercent);
                    }
                } else {
                    benefitdep_ids.push([0, 0, {
                        name: name,
                        sharepercent: sharepercent,
                    }])
                    sum_shaerpercent += parseFloat(sharepercent);
                }
            });

            if (sum_shaerpercent != 100) {
                $.toast('部门分摊比例不等于100%');
                return;
            }

            if (this.$('input[data-id=paycatelog]').data('paycatelog-id') == "fukuangeigongyingshang"){

                if($.trim(this.$('input[data-id=shoukuanren]').val()) == ""){
                    this.$('input[data-id=shoukuanren]').focus();
                    $.toast('请填写收款人姓名');
                    return;
                }

                if($.trim(this.$('input[data-id=kaihuhang]').val()) == ""){
                    this.$('input[data-id=kaihuhang]').focus();
                    $.toast('请填写开户行');
                    return;
                }

                if($.trim(this.$('input[data-id=yinhangkahao]').val()) == ""){
                    this.$('input[data-id=yinhangkahao]').focus();
                    $.toast('请填写银行卡号');
                    return;
                }
            }

            var expense_report_detail={};
            if (this.$('input[data-id=paycatelog]').data('paycatelog-id') == "fukuangeigongyingshang"){
                expense_report_detail = {
                'paytype': this.$('input[data-id=paytype]').data('paytype-id'),
                'paycatelog': this.$('input[data-id=paycatelog]').data('paycatelog-id'),
                'xingzhengzhuli': xingzhengzhuli_id,
                'expensereason': this.$('textarea[data-id=expensereason]').val(),
                'benefitdep_ids': benefitdep_ids,
                'record_ids': expense_ids,
                'chuchaishijian_ids': chuchai_ids,
                'kaihuhang':$.trim(this.$('input[data-id=kaihuhang]').val()),
                'shoukuanrenxinming': $.trim(this.$('input[data-id=shoukuanren]').val()),
                'yinhangkahao': $.trim(this.$('input[data-id=yinhangkahao]').val())
                }
            } else {
                expense_report_detail = {
                'paytype': this.$('input[data-id=paytype]').data('paytype-id'),
                'paycatelog': this.$('input[data-id=paycatelog]').data('paycatelog-id'),
                'xingzhengzhuli': xingzhengzhuli_id,
                'expensereason': this.$('textarea[data-id=expensereason]').val(),
                'benefitdep_ids': benefitdep_ids,
                'record_ids': expense_ids,
                'chuchaishijian_ids': chuchai_ids
                }
            }

            var def = new $.Deferred();
            parent.expense_report = self.expense_report;
            new Model('dtdream.expense.report').call('read', [[self.expense_report.id], ['id', 'write_date']]).then(function (records) {
                if (records) {
                    if (records[0].write_date == parent.expense_report.write_date) {
                        $.when(new Model('dtdream.expense.report').call('write', [[self.expense_report.id], expense_report_detail]))
                        .fail(function (err) {
                            $.alert(err.data.message.replace('None', ""));
                        })
                        .then(function () {
                            $.toast("保存成功");
                            core.bus.trigger('change_screen', {
                                model: 'receipts',
                                action: null,
                                id: null
                            });
                        });
                    }
                    else {
                        $.toast('数据已经被修改,请刷新数据。');
                        core.bus.trigger('change_screen', {
                            model: 'receipts',
                            action: null,
                            id: null
                        });
                    }
                } else {
                    $.toast('没有找到对应的纪录。');
                    core.bus.trigger('change_screen', {
                        model: 'receipts',
                        action: null,
                        id: null
                    });
                }
            },function (err) {
                    $.alert(err.data.message.replace('None', ""));
            });
            def.resolve();
        },

        action_qianshou: function(parent){
            var self = this;
            var id = parseInt(self.expense_report.id);
            new Model('dtdream.expense.report').call('btn_checkpaper', [[id]]).then(function (result) {
                console.log(result);
                $.toast("签收成功");
                core.bus.trigger('change_screen', {
                    model: 'receipts',
                    action: "approval",
                    id: id,
                    back: true
                });
            }, function (err) {
                console.log(err);
                $.alert(err.data.message.replace('None', ""));
            });
        },

        action_confirm_pay: function(parent) {
            var self = this;
            $.confirm('确定付款吗?', function () {
                var id = parseInt(self.expense_report.id);
                new Model('dtdream.expense.report').exec_workflow(id, 'btn_confirmmoney').then(function (result) {
                    console.log(result);
                    $.toast("付款成功");
                    core.bus.trigger('change_screen', {
                        model: 'approval',
                        action: null,
                        id: null
                    });
                }, function (err) {
                    console.log(err);
                    $.alert(err.data.message.replace('None', ""));
                });
            });
        },

        action_accept: function(parent) {
            var self = this;
            var text = QWeb.render('receipts_approval_accept');
            parent.report_id = parseInt(self.expense_report.id);
            var modal = $.modal({
                title: '同意?',
                afterText: text,
                buttons: [
                    {
                        text: '取消'
                    },
                    {
                        text: '确定',
                        bold: true,
                        onClick: function (ev) {
                            var accept_text = ev.find('.o_accept').val();
                            // if (accept_text.length == 0) {
                            //     $.alert('没有输入意见;')
                            // } else {
                            new Model('dtdream.expense.agree.wizard').call('create', [{advice: accept_text}]).then(function (result) {
                                console.log(result);

                                var context = [[result], {
                                    'lang': 'zh_CN',
                                    'uid': 1,
                                    'active_model': 'dtdream.expense.report',
                                    'search_disable_custom_filters': true,
                                    'active_ids': [parent.report_id],
                                    'active_id': parent.report_id
                                }]

                                new Model('dtdream.expense.agree.wizard').call_button('btn_confirm', context).then(function (result) {
                                    $.toast("审批完成");
                                    core.bus.trigger('change_screen', {
                                        model: 'approval',
                                        action: null,
                                        id: null
                                    });
                                }, function (err) {
                                    $.alert(err.data.message.replace('None', ""));
                                });
                            }, function (err) {
                            });

                            // }

                        }
                    },
                ]
            })
        },

        action_reject: function(parent) {
            var self = this;
            var accept_text = self.$('.o_reject_advice').val();
            var state = self.$('.o_reject_state').data('id');
            if (accept_text.length == 0) {
                $.alert('没有输入意见;')
            } else if (state.length == 0) {
                $.alert('没有选择节点');
            }
            else {
                var report_context = {
                    'active_ids': [self.expense_report.id],
                    'active_id': self.expense_report.id,
                    'active_model': 'dtdream.expense.report'
                }
                new Model('dtdream.expense.wizard').call('create', [{
                    liyou: accept_text,
                    state: state
                }], {context: report_context}).then(function (result) {
                    console.log(result);

                    var context = [[result], {
                        'lang': 'zh_CN',
                        'uid': 1,
                        'active_model': 'dtdream.expense.report',
                        'search_disable_custom_filters': true,
                        'active_ids': [self.expense_report.id],
                        'active_id': self.expense_report.id
                    }]
                    new Model('dtdream.expense.wizard').call_button('btn_confirm', context).then(function (result) {
                        $.toast("审批完成");
                        core.bus.trigger('change_screen', {
                            model: 'approval',
                            action: null,
                            id: null
                        });
                    }, function (err) {
                        $.alert(err.data.message.replace('None', ""));
                    });
                }, function (err) {
                });

            }
        },

        action_button: function (parent) {
            parent.preventDefault();
            parent.stopPropagation();

            var self = this;
            var itemID = $(parent.currentTarget).data('item-id');
            if ( itemID == 'sumbit_benefitdep') {
                this.action_add_benefitdep(parent);
            } else if (itemID == 'cancel_add_benefitdep') {
                this.action_cancel_benefitdep(parent);
            } else if (itemID == "add_chuchai") {
                this.action_add_chuchai(parent);
            } else if (itemID == "cancel_add_chuchai") {
                this.action_cancel_chuchai(parent);
            } else if (itemID == "add_detail") {
                this.action_add_detail(parent);
            } else if (itemID == "cancel_add_detail") {
                this.action_cancel_detail(parent);
            } else if (itemID == "cancel") {
                if (this.options.edit_type != "view"){
                    $.confirm('您确定返回吗?',
                        function () {
                            core.bus.trigger('go_back', {});
                        },
                        function () {
                        }
                    );
                } else {
                    core.bus.trigger('go_back', {});
                }
            } else if (itemID == "delete") {
                this.action_delete(parent);
            } else if (itemID == "save") {
                this.action_save(parent);
            } else if (itemID == "qianshou") {
                this.action_qianshou(parent);
            } else if (itemID == "confirm_pay") {
                this.action_confirm_pay(parent);
            } else if (itemID == "accept") {
                this.action_accept(parent);
            } else if (itemID == "reject") {
                $.popup('.popup-reject');
            } else if (itemID == "cancel_reject") {
                $.closeModal();
            } else if (itemID == "sumbit_reject") {
                this.action_reject(parent);
            }
        },
        /**
         * @memberOf Report_detail_screen
         * @description 打开支付方式界面
         * @param {object} ev dom对象
         */
        action_paytype: function (ev) {

            ev.preventDefault();

            var self = this;

            if (self.options.expense_report[0].state != 'draft')return;
            var buttons1 = [
                {
                    text: '请选择',
                    label: true
                },
                {
                    text: '银行转账',
                    bold: true,
                    color: 'danger',
                    onClick: function (e) {
                        $('input[data-id=paytype]').data('paytype-id', 'yinhangzhuanzhang');
                        $('input[data-id=paytype]').val('银行转账');
                    }
                },
                {
                    text: '核销备用金',
                    onClick: function (e) {
                        $('input[data-id=paytype]').data('paytype-id', 'hexiaobeiyongjin');
                        $('input[data-id=paytype]').val('核销备用金');
                    }
                }
            ];
            var buttons2 = [
                {
                    text: '取消',
                    bg: 'danger'
                }
            ];
            var groups = [buttons1, buttons2];
            $.actions(groups);
        },
        /**
         * @memberOf Report_detail_screen
         * @description 选择支付类别
         */
        action_paycatelog: function (ev) {

            ev.preventDefault();

            var self = this;
            if (self.options.expense_report[0].state != 'draft')return;

            var buttons1 = [
                {
                    text: '请选择',
                    label: true
                },
                {
                    text: '付款给员工',
                    bold: true,
                    color: 'danger',
                    onClick: function (e) {
                        $('input[data-id=paycatelog]').data('paycatelog-id', 'fukuangeiyuangong');
                        $('input[data-id=paycatelog]').val('付款给员工');
                        $('.o_shoukuanren').hide();
                        $('.o_kaihuhang').hide();
                        $('.o_yinhangkahao').hide();
                    }
                },
                {
                    text: '付款给供应商',
                    onClick: function (e) {
                        $('input[data-id=paycatelog]').data('paycatelog-id', 'fukuangeigongyingshang');
                        $('input[data-id=paycatelog]').val('付款给供应商');
                        $('.o_shoukuanren').show();
                        $('.o_kaihuhang').show();
                        $('.o_yinhangkahao').show();
                    }
                }
            ];

            var buttons2 = [
                {
                    text: '取消',
                    bg: 'danger'
                }
            ];
            var groups = [buttons1, buttons2];
            $.actions(groups);
        },
        /**
         * @memberOf Report_detail_screen
         * @description 显示爆笑申请详细内容
         * @param {object} el dom对象
         * @param {object} options 参数
         */
        attach: function (el, options) {
            $('.o_main_bar').hide();
            this._super(el, options);
            this.$('a[data-item-id=accept]').css('display', 'none');;
            this.$('a[data-item-id=reject]').css('display', 'none');;
            this.$('a[data-item-id=qianshou]').css('display', 'none');;
            this.$('a[data-item-id=confirm_pay]').css('display', 'none');;
            this.$('a[data-item-id=save]').css('display', 'none');;
            this.$('a[data-item-id=delete]').css('display', 'none');;

            if (options && options.receipt_id) {
                $.when(
                    new Model('dtdream.expense.report')
                        .query(['id', 'name', 'state', 'paytype', 'total_invoicevalue', 'paycatelog', 'work_place',
                                'expensereason', 'create_uid', 'create_date', 'write_date', 'showcuiqian',
                                'currentauditperson', 'currentauditperson_userid', 'hasauditor', 'is_outtime',
                                'xingzhengzhuli', 'department_id', 'create_uid_self','kaihuhang','shoukuanrenxinming','yinhangkahao', 'compute_currentaudit'])
                        .filter([['id', '=', parseInt(options.receipt_id)]])
                        .all({'timeout': 3000, 'shadow': true}), this)
                .fail(function (err) {
                    $.alert(err.data.message.replace('None', ""));
                })
                .then(
                    function (data, parent) {
                        options['expense_report'] = data;
                        parent.options = options;
                        parent.init_data(parent);
                        parent.load_xingzhengzhuli(parent);
                    },
                    function (err, event) {
                        event.preventDefault();
                    });
            }


        },

        init_data: function (self) {
            if (self.options){
                this.options = self.options;
            }
            if (this.options && this.options.expense_report) {
                this.expense_report = this.options.expense_report[0];
                this.$('input[data-id=name]').val(this.expense_report.name);
                this.$('input[data-id=paytype]').data('paytype-id', this.expense_report.paytype);
                var payType = {'yinhangzhuanzhang': '银行转账', 'hexiaobeiyongjin': '核销备用金'};
                this.$('input[data-id=paytype]').val(payType[this.expense_report.paytype]);
                this.$('input[data-id=paycatelog]').data('paycatelog-id', this.expense_report.paycatelog);
                var paycatelog = {'fukuangeiyuangong': '付款给员工', 'fukuangeigongyingshang': '付款给供应商'};
                this.$('input[data-id=paycatelog]').val(paycatelog[this.expense_report.paycatelog]);
                if (this.expense_report.paycatelog == "fukuangeigongyingshang"){
                    $('.o_shoukuanren').show();
                    $('.o_kaihuhang').show();
                    $('.o_yinhangkahao').show();
                    this.$('input[data-id=shoukuanren]').val(this.expense_report.shoukuanrenxinming);
                    this.$('input[data-id=kaihuhang]').val(this.expense_report.kaihuhang);
                    this.$('input[data-id=yinhangkahao]').val(this.expense_report.yinhangkahao);
                } else {
                    $('.o_shoukuanren').hide();
                    $('.o_kaihuhang').hide();
                    $('.o_yinhangkahao').hide();
                }

                this.$('input[data-id=work_place]').val(this.expense_report.work_place);
                this.$('input[data-id=create_uid_self]').val(this.expense_report.create_uid_self[1]);

                if (this.expense_report.currentauditperson) {
                    this.$('input[data-id=currentauditperson]').val(this.expense_report.currentauditperson[1]);
                    this.$('.o_currentauditperson').show();
                } else {
                    this.$('.o_currentauditperson').hide();
                }

                if (this.expense_report.expensereason) {
                    this.$('textarea[data-id=expensereason]').val(this.expense_report.expensereason);
                } else {
                    this.$('textarea[data-id=expensereason]').val("");
                }

                this.rend_expense(this);
                this.rend_benefitdep(this);
                this.rend_chuchai(this);

                if ( this.expense_report.compute_currentaudit == true && this.options.edit_type == "approval" && this.expense_report.state != 'draft' ) {

                    if (this.expense_report.state == 'xingzheng') {
                        if (this.expense_report.showcuiqian != 1) {
                            this.$('a[data-item-id=qianshou]').css('display', '');
                        } else {
                            this.$('a[data-item-id=accept]').css('display', '');
                            this.$('a[data-item-id=reject]').css('display', '');
                        }
                    } else if (this.expense_report.state == 'jiekoukuaiji') {
                        if (this.expense_report.showcuiqian != 2) {
                            this.$('a[data-item-id=qianshou]').css('display', '');
                        } else {
                            this.$('a[data-item-id=accept]').css('display', '');
                            this.$('a[data-item-id=reject]').css('display', '');
                        }
                    } else if (this.expense_report.state == 'daifukuan') {
                        this.$('a[data-item-id=confirm_pay]').css('display', '');
                    } else {
                        this.$('a[data-item-id=accept]').css('display', '');
                        this.$('a[data-item-id=reject]').css('display', '');
                    }

                    this.$('.o_add_expense').hide();
                    this.$('.o_add_benefitdep').hide();
                    this.$('.o_add_chuchai').hide();

                    this.$('textarea[data-id=expensereason]').attr("readonly", "readonly");
                    this.$('input[data-id=shoukuanren]').attr("readonly", "readonly");
                    this.$('input[data-id=kaihuhang]').attr("readonly", "readonly");
                    this.$('input[data-id=yinhangkahao]').attr("readonly", "readonly");

                } else if ( this.options.edit_type == "view" ) {

                    this.$('.o_add_expense').hide();
                    this.$('.o_add_benefitdep').hide();
                    this.$('.o_add_chuchai').hide();

                    this.$('textarea[data-id=expensereason]').attr("readonly", "readonly");
                    this.$('input[data-id=shoukuanren]').attr("readonly", "readonly");
                    this.$('input[data-id=kaihuhang]').attr("readonly", "readonly");
                    this.$('input[data-id=yinhangkahao]').attr("readonly", "readonly");

                }  else if ( this.options.edit_type == "edit") {
                    this.$('a[data-item-id=save]').css('display', '');
                    this.$('a[data-item-id=delete]').css('display', '');
                }
            }
        },
        /**
         * @memberOf Report_detail_screen
         * @description 显示出差明细
         * @param {object} parent 父对象
         */
        rend_chuchai: function (parent) {
            var def = new $.Deferred();
            var self = this;
            new Model('dtdream.travel.journey')
                .query(['id', 'starttime', 'endtime', 'startaddress', 'endaddress', 'reason'])
                .filter([['report_ids', '=', this.expense_report.id]])
                .all({'timeout': 3000, 'shadow': true})
                .then(function (chuchai_ids) {
                        self.chuchai_ids = chuchai_ids;
                        if (parent.rend_chuchai_detail(chuchai_ids, parent.$el)) {
                            def.resolve();
                        } else {
                            def.reject();
                        }
                    }, function (err, event) {
                        event.preventDefault();
                        def.reject();
                    }
                );
        },

        /**
         * @memberOf Report_detail_screen
         * @description 显示出差明细
         * @param {json} chuchai_ids 出差明细
         * @param {object} $el dom对象
         */
        rend_chuchai_detail: function (chuchai_ids, $el) {
            if (chuchai_ids) {
                var $chuchai_ids = $(QWeb.render('receipts_chuchai_list', {
                    'chuchai_ids': chuchai_ids,
                    'state': this.options.expense_report[0].state
                }));
                $el.find('.o_report_chuchai_ids').append($chuchai_ids);
            }
        },

        /**
         * @memberOf Report_detail_screen
         * @description 从服务端获取消费明细
         * @param {object} parent 父对象
         */
        rend_expense: function (parent) {
            var def = new $.Deferred();
            var self = this;
            new Model('dtdream.expense.record')
                .query(['id', 'name', 'report_ids', 'expensecatelog', 'expensedetail', 'shibaoamount', 'koujianamount', 'invoicevalue', 'city', 'province', 'outtimenumber', 'currentdate', 'write_date', 'state'])
                .filter([['report_ids', '=', this.expense_report.id]])
                .all({'timeout': 3000, 'shadow': true})
                .then(function (expense_records) {
                        self.expense_records = expense_records;
                        var expense_ids = []
                        $.each(expense_records, function (key, value) {
                            expense_ids.push(parseInt(value.id));
                        })

                        if (parent.rend_expense_detail(expense_records, parent.$el)) {
                            def.resolve();
                        } else {
                            def.reject();
                        }
                    }, function (err, event) {
                        event.preventDefault();
                        def.reject();
                    }
                );
        },

        /**
         * @memberOf Report_detail_screen
         * @description 显示消费明细
         * @param {json} expense_records 消费明细
         * @param {object} $el dom对象
         */
        rend_expense_detail: function (expense_records, $el) {
            if (expense_records) {
                for (var i in expense_records) {
                    if (expense_records[i].expensedetail[1].length>15){
                            expense_records[i].expensedetail[1] = expense_records[i].expensedetail[1].substring(0, 12) + "...";
                    }
                }
                var $expense_records = $(QWeb.render('receipts_detail_list', {
                    'expense_records': expense_records,
                    'state': this.options.expense_report[0].state
                }));
                $el.find('.o_report_expense_ids').append($expense_records);
                for (var i in expense_records) {
                    if (expense_records[i].expensecatelog[1] != "差旅费"){
                        $('.o_report_chuchai_ids').hide();
                    }
                }
            }
        },

        /**
         * @memberOf Report_detail_screen
         * @description 从服务端获取费用分摊明细
         * @param {object} parent 父对象
         */
        rend_benefitdep: function (parent) {
            var def = new $.Deferred();
            var self = this;
            new Model('dtdream.expense.benefitdep')
                .query(['id', 'name', 'sharepercent', 'write_date'])
                .filter([['report_id', '=', this.expense_report.id]])
                .all({'timeout': 3000, 'shadow': true})
                .then(function (benefitdep_records) {
                        self.benefitdep_records = benefitdep_records;
                        var department_ids = [];
                        $.each(benefitdep_records, function (key, value) {
                            department_ids.push = value.name[0];
                        })
                        $.when(new Model('hr.department').call('name_get', [department_ids]), benefitdep_records)
                        .fail(function (err) {
                            $.alert(err.data.message.replace('None', ""));
                        })
                        .then(function (record, benefitdep_records) {
                            $.each(benefitdep_records, function (key, value) {
                                $.each(record, function (key1, value1) {
                                    if (value.name[0] == value1[0]) {
                                        value.name[1] = value1[1];
                                    }
                                })
                            })
                            if (parent.rend_benefitdep_detail(benefitdep_records, parent.$el)) {
                                def.resolve();
                            } else {
                                def.reject();
                            }

                        })

                    }, function (err, event) {
                        event.preventDefault();
                        def.reject();
                    }
                );
        },

        /**
         * @memberOf Report_detail_screen
         * @description 显示费用分摊明细
         * @param {json} benefitdep_records 费用分摊明细
         * @param {object} $el dom对象
         */
        rend_benefitdep_detail: function (benefitdep_records, $el) {
            if (benefitdep_records) {
                var $benefitdep_records = $(QWeb.render('receipts_benefitdep_list', {
                    'benefitdep_records': benefitdep_records,
                    'state': this.options.expense_report[0].state
                }));
                $el.find('.o_report_benefitdep_ids').append($benefitdep_records);

            }
        },

        /**
         * @memberOf Report_detail_screen
         * @description 显示钉钉界面抬头内容
         */
        setTitle: function () {
//            if (this.options) {
//                if (this.options.detail_title) {
//                    this.title = this.options.detail_title;
//                } else if (this.options.expense_report && this.options.expense_report[0].state == 'draft') {
//                    this.title = '待提交的报销申请';
//                } else {
//                    this.title = '未完成的报销申请';
//                }
//            }
            this._super();
        },
    });

    return Main;
})
;
