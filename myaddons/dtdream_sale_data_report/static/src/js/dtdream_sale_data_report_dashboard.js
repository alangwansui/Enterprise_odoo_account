/**
 * @class DataReportDashboard
 * @classdesc 销售数据报表Dashboard
 */
odoo.define('dtdream_sale_data_report.ui.dashboard', function (require) {
    "use strict";

    var core = require('web.core');
    var formats = require('web.formats');
    var Model = require('web.Model');
    var session = require('web.session');
    var KanbanView = require('web_kanban.KanbanView');

    var QWeb = core.qweb;

    var _t = core._t;
    var _lt = core._lt;

    var provinces = []
    //对应一级数据
    var allSeriesData={
        "政务":[300,500,600,700,400,50,100,200,300,300,100,100,50,100],
        "政法":[200,600,300,400,50,100,0,200,0,0,100,100,0,0],
        "企业":[100,300,700,200,50,100,0,0,300,10,80,30,10,250],
        "专网":[50,200,400,30,50,100,500,20,300,100,180,130,110,50],
        "电力":[10,0,300,100,50,100,500,20,300,100,180,130,110,50]
    };
    //对应二级数据
    var provinceSeriesData={
        "政务":[150,50,250,300,150,200],
        "政法":[460,260,360,160,56,200],
        "企业":[40,340,840,440,140,200],
        "专网":[120,220,420,20,120,580],
        "电力":[290,590,450,390,230,360]
    };
    //对应三级数据
    var refreshSeries={
        "政务":[50,100,150,200,250,300],
        "政法":[60,160,260,360,16,100],
        "企业":[340,300,240,44,140,200],
        "专网":[220,20,120,320,420,80],
        "电力":[90,190,150,290,230,360]
    };
    /*图表中数据处理*/
    //设置初始图表的数据
    //var selContent=$("#area").val();
    var data="";
    var seriesContent="";

    /**
     * @class DataReportDashboardView
     * @classdesc 销售数据报表Dashboard
     * @augments KanbanView
     */
    var DataReportDashboardView = KanbanView.extend({
        events: _.defaults({
                'change #area' : 'change_area',
                'change #selectprovince' : 'change_province',
                'click #selectQueryBtn': 'click_queryBtn'
            }, KanbanView.prototype.events),

        //设置选择第二个选项框时的数据
        getProvinces:function(area){
            // var nowSelProvince=$("#selectprovince").find("option:selected").text();
            if(area != "请选择"){
                data=[area];
            }
            return data;
        },

        getSeriesData:function(area){
            // var nowSelProvince=$("#selectprovince").find("option:selected").text();
            if(area != "请选择"){
                seriesContent=[{
                    "name":"政务",
                    "type":"bar",
                    "stack":"总数",    //设置柱状图堆叠显示
                    "barMaxWidth":35,
                    "barGap":"10%",
                    "itemStyle":{
                        "normal":{
                            "color":"#1A69AD",
                            "label":{
                                "show":true,
                                "textStyle":{
                                    "color":"#fff"
                                },
                                "position":"insideTop",
                                formatter:function(p){
                                    return p.value > 0 ? (p.value):"";
                                }
                            }
                        }
                    },
                    "data":refreshSeries["政务"]
                },{
                    "name":"政法",
                    "type":"bar",
                    "stack":"总数",    //设置柱状图堆叠显示
                    "barMaxWidth":35,
                    "barGap":"10%",
                    "itemStyle":{
                        "normal":{
                            "color":"#1F8AE7",
                            "label":{
                                "show":true,
                                "textStyle":{
                                    "color":"#fff"
                                },
                                "position":"insideTop",
                                formatter:function(p){
                                    return p.value > 0 ? (p.value):"";
                                }
                            }
                        }
                    },
                    "data":refreshSeries["政法"]
                },{
                    "name":"企业",
                    "type":"bar",
                    "stack":"总数",    //设置柱状图堆叠显示
                    "barMaxWidth":35,
                    "barGap":"10%",
                    "itemStyle":{
                        "normal":{
                            "color":"#1FC2E7",
                            "label":{
                                "show":true,
                                "textStyle":{
                                    "color":"#fff"
                                },
                                "position":"insideTop",
                                formatter:function(p){
                                    return p.value > 0 ? (p.value):"";
                                }
                            }
                        }
                    },
                    "data":refreshSeries["企业"]
                },{
                    "name":"专网",
                    "type":"bar",
                    "stack":"总数",    //设置柱状图堆叠显示
                    "barMaxWidth":35,
                    "barGap":"10%",
                    "itemStyle":{
                        "normal":{
                            "color":"#21D3FF",
                            "label":{
                                "show":true,
                                "textStyle":{
                                    "color":"#fff"
                                },
                                "position":"insideTop",
                                formatter:function(p){
                                    return p.value > 0 ? (p.value):"";
                                }
                            }
                        }
                    },
                    "data":refreshSeries["专网"]
                },{
                    "name":"电力",
                    "type":"bar",
                    "stack":"总数",    //设置柱状图堆叠显示
                    "barMaxWidth":35,
                    "barGap":"10%",
                    "itemStyle":{
                        "normal":{
                            "color":"#67E1FF",
                            "label":{
                                "show":true,
                                "textStyle":{
                                    "color":"#fff"
                                },
                                "position":"insideTop",
                                formatter:function(p){
                                    return p.value > 0 ? (p.value):"";
                                }
                            }
                        }
                    },
                    "data":refreshSeries["电力"]
                }];
            }
            return seriesContent;
        },

        //获取第二个选项框对应的内容
        getSelectvalue:function (value){
            if(value != "选择区域"){
                return new Model('dtdream.sale.data.report')
                    .call('get_province_by_department', [value]);
            }
        },

        // 设置数据
        change_province:function(){
            var nowSelValue = $("#selectprovince").find("option:selected").text();
            if(nowSelValue == "请选择"){
                data=this.provinces;
                seriesContent=[{
                        "name":"政务",
                        "type":"bar",
                        "stack":"总数",    //设置柱状图堆叠显示
                        "barMaxWidth":35,
                        "barGap":"10%",
                        "itemStyle":{
                            "normal":{
                                "color":"#1A69AD",
                                "label":{
                                    "show":true,
                                    "textStyle":{
                                        "color":"#fff"
                                    },
                                    "position":"insideTop",
                                    formatter:function(p){
                                        return p.value > 0 ? (p.value):"";
                                    }
                                }
                            }
                        },
                        "data":provinceSeriesData["政务"]
                    },{
                        "name":"政法",
                        "type":"bar",
                        "stack":"总数",    //设置柱状图堆叠显示
                        "barMaxWidth":35,
                        "barGap":"10%",
                        "itemStyle":{
                            "normal":{
                                "color":"#1F8AE7",
                                "label":{
                                    "show":true,
                                    "textStyle":{
                                        "color":"#fff"
                                    },
                                    "position":"insideTop",
                                    formatter:function(p){
                                        return p.value > 0 ? (p.value):"";
                                    }
                                }
                            }
                        },
                        "data":provinceSeriesData["政法"]
                    },{
                        "name":"企业",
                        "type":"bar",
                        "stack":"总数",    //设置柱状图堆叠显示
                        "barMaxWidth":35,
                        "barGap":"10%",
                        "itemStyle":{
                            "normal":{
                                "color":"#1FC2E7",
                                "label":{
                                    "show":true,
                                    "textStyle":{
                                        "color":"#fff"
                                    },
                                    "position":"insideTop",
                                    formatter:function(p){
                                        return p.value > 0 ? (p.value):"";
                                    }
                                }
                            }
                        },
                        "data":provinceSeriesData["企业"]
                    },{
                        "name":"专网",
                        "type":"bar",
                        "stack":"总数",    //设置柱状图堆叠显示
                        "barMaxWidth":35,
                        "barGap":"10%",
                        "itemStyle":{
                            "normal":{
                                "color":"#21D3FF",
                                "label":{
                                    "show":true,
                                    "textStyle":{
                                        "color":"#fff"
                                    },
                                    "position":"insideTop",
                                    formatter:function(p){
                                        return p.value > 0 ? (p.value):"";
                                    }
                                }
                            }
                        },
                        "data":provinceSeriesData["专网"]
                    },{
                        "name":"电力",
                        "type":"bar",
                        "stack":"总数",    //设置柱状图堆叠显示
                        "barMaxWidth":35,
                        "barGap":"10%",
                        "itemStyle":{
                            "normal":{
                                "color":"#67E1FF",
                                "label":{
                                    "show":true,
                                    "textStyle":{
                                        "color":"#fff"
                                    },
                                    "position":"insideTop",
                                    formatter:function(p){
                                        return p.value > 0 ? (p.value):"";
                                    }
                                }
                            }
                        },
                        "data":provinceSeriesData["电力"]
                    }];
            }else{
                data=this.getProvinces(nowSelValue);
                seriesContent=this.getSeriesData(nowSelValue);
            }
        },

        change_area:function(){
            //$("#area").on("change",function(){
                var nowSelValue = $("#area").find("option:selected").val();
                //设置第二个选项框显示
                if(nowSelValue == "selectArea"){
                    $("#selectprovince").css("display","none");
                    data=["北京分部","杭州办","南京办","成都办","天津联络处","郑州联络处","长沙联络处","武汉联络处","昆明联络处","西宁联络处","西安联络处","兰州联络处","长春联络处","战略发展部"];
                    seriesContent=[{
                        "name":"政务",
                        "type":"bar",
                        "stack":"总数",    //设置柱状图堆叠显示
                        "barMaxWidth":35,
                        "barGap":"10%",
                        "itemStyle":{
                            "normal":{
                                "color":"#1A69AD",
                                "label":{
                                    "show":true,
                                    "textStyle":{
                                        "color":"#fff"
                                    },
                                    "position":"insideTop",
                                    formatter:function(p){
                                        return p.value > 0 ? (p.value):"";
                                    }
                                }
                            }
                        },
                        "data":allSeriesData["政务"]
                    },{
                        "name":"政法",
                        "type":"bar",
                        "stack":"总数",    //设置柱状图堆叠显示
                        "barMaxWidth":35,
                        "barGap":"10%",
                        "itemStyle":{
                            "normal":{
                                "color":"#1F8AE7",
                                "label":{
                                    "show":true,
                                    "textStyle":{
                                        "color":"#fff"
                                    },
                                    "position":"insideTop",
                                    formatter:function(p){
                                        return p.value > 0 ? (p.value):"";
                                    }
                                }
                            }
                        },
                        "data":allSeriesData["政法"]
                    },{
                        "name":"企业",
                        "type":"bar",
                        "stack":"总数",    //设置柱状图堆叠显示
                        "barMaxWidth":35,
                        "barGap":"10%",
                        "itemStyle":{
                            "normal":{
                                "color":"#1FC2E7",
                                "label":{
                                    "show":true,
                                    "textStyle":{
                                        "color":"#fff"
                                    },
                                    "position":"insideTop",
                                    formatter:function(p){
                                        return p.value > 0 ? (p.value):"";
                                    }
                                }
                            }
                        },
                        "data":allSeriesData["企业"]
                    },{
                        "name":"专网",
                        "type":"bar",
                        "stack":"总数",    //设置柱状图堆叠显示
                        "barMaxWidth":35,
                        "barGap":"10%",
                        "itemStyle":{
                            "normal":{
                                "color":"#21D3FF",
                                "label":{
                                    "show":true,
                                    "textStyle":{
                                        "color":"#fff"
                                    },
                                    "position":"insideTop",
                                    formatter:function(p){
                                        return p.value > 0 ? (p.value):"";
                                    }
                                }
                            }
                        },
                        "data":allSeriesData["专网"]
                    },{
                        "name":"电力",
                        "type":"bar",
                        "stack":"总数",    //设置柱状图堆叠显示
                        "barMaxWidth":35,
                        "barGap":"10%",
                        "itemStyle":{
                            "normal":{
                                "color":"#67E1FF",
                                "label":{
                                    "show":true,
                                    "textStyle":{
                                        "color":"#fff"
                                    },
                                    "position":"insideTop",
                                    formatter:function(p){
                                        return p.value > 0 ? (p.value):"";
                                    }
                                }
                            }
                        },
                        "data":allSeriesData["电力"]
                    }];
                }else{
                    //设置第二个选项框里面的内容
                    //var selectNum=$(this).val();
                    this.getSelectvalue(nowSelValue).then(function (result) {
                        if (!result){
                            $("#selectprovince").css("display","none");
                            alert('该区域未设置对应省份。')
                        }
                        else{
                            //设置第二个选项框显示
                            $("#selectprovince").css("display","block");
                            var html="<option value='00' selected>请选择</option>";
                            for(var i=0;i<result.length;i++){
                                html+="<option value='"+i+"'>"+result[i]+"</option>";
                            }
                            $("#selectprovince").html(html);
                            this.provinces = result;
                            data = result;
                            seriesContent=[{
                                    "name":"政务",
                                    "type":"bar",
                                    "stack":"总数",    //设置柱状图堆叠显示
                                    "barMaxWidth":35,
                                    "barGap":"10%",
                                    "itemStyle":{
                                        "normal":{
                                            "color":"#1A69AD",
                                            "label":{
                                                "show":true,
                                                "textStyle":{
                                                    "color":"#fff"
                                                },
                                                "position":"insideTop",
                                                formatter:function(p){
                                                    return p.value > 0 ? (p.value):"";
                                                }
                                            }
                                        }
                                    },
                                    "data":provinceSeriesData["政务"]
                                },{
                                    "name":"政法",
                                    "type":"bar",
                                    "stack":"总数",    //设置柱状图堆叠显示
                                    "barMaxWidth":35,
                                    "barGap":"10%",
                                    "itemStyle":{
                                        "normal":{
                                            "color":"#1F8AE7",
                                            "label":{
                                                "show":true,
                                                "textStyle":{
                                                    "color":"#fff"
                                                },
                                                "position":"insideTop",
                                                formatter:function(p){
                                                    return p.value > 0 ? (p.value):"";
                                                }
                                            }
                                        }
                                    },
                                    "data":provinceSeriesData["政法"]
                                },{
                                    "name":"企业",
                                    "type":"bar",
                                    "stack":"总数",    //设置柱状图堆叠显示
                                    "barMaxWidth":35,
                                    "barGap":"10%",
                                    "itemStyle":{
                                        "normal":{
                                            "color":"#1FC2E7",
                                            "label":{
                                                "show":true,
                                                "textStyle":{
                                                    "color":"#fff"
                                                },
                                                "position":"insideTop",
                                                formatter:function(p){
                                                    return p.value > 0 ? (p.value):"";
                                                }
                                            }
                                        }
                                    },
                                    "data":provinceSeriesData["企业"]
                                },{
                                    "name":"专网",
                                    "type":"bar",
                                    "stack":"总数",    //设置柱状图堆叠显示
                                    "barMaxWidth":35,
                                    "barGap":"10%",
                                    "itemStyle":{
                                        "normal":{
                                            "color":"#21D3FF",
                                            "label":{
                                                "show":true,
                                                "textStyle":{
                                                    "color":"#fff"
                                                },
                                                "position":"insideTop",
                                                formatter:function(p){
                                                    return p.value > 0 ? (p.value):"";
                                                }
                                            }
                                        }
                                    },
                                    "data":provinceSeriesData["专网"]
                                },{
                                    "name":"电力",
                                    "type":"bar",
                                    "stack":"总数",    //设置柱状图堆叠显示
                                    "barMaxWidth":35,
                                    "barGap":"10%",
                                    "itemStyle":{
                                        "normal":{
                                            "color":"#67E1FF",
                                            "label":{
                                                "show":true,
                                                "textStyle":{
                                                    "color":"#fff"
                                                },
                                                "position":"insideTop",
                                                formatter:function(p){
                                                    return p.value > 0 ? (p.value):"";
                                                }
                                            }
                                        }
                                    },
                                    "data":provinceSeriesData["电力"]
                                }];
                            }
                        });
                        //data=province[selectNum];
                }
        },
        /**
         * @memberOf DataReportDashboardView
         * @description 标题
         */
        display_name: '销售数据报表',
        /**
         * @memberOf DataReportDashboardView
         * @description 图标
         */
        icon: 'fa-dashboard',
        /**
         * @memberOf DataReportDashboardView
         * @description 新的视图类型 Data_dashboard
         */
        view_type: "dtdream_sale_data_report",
        /**
         * @memberOf DataReportDashboardView
         * @description 是否显示搜索栏
         */
        searchview_hidden: true,
        /**
         * @memberOf DataReportDashboardView
         * @description 从服务端获取数据
         * @returns {*|jQuery.Deferred}
         */
        fetch_data: function () {
             //Overwrite this function with useful data
            return new Model('dtdream.sale.data.report')
                .call('get_sales_report_data', []);
        },
        /**
         * @memberOf DataReportDashboardView
         * @description 显示看板视图内容
         * @returns {*|Promise|Promise.<TResult>}
         */
        render: function () {
            var super_render = this._super;
            var self = this;

            var start_date = $(".datepickerstart").val();
            var end_date = $(".datepickerend").val()
            self.fetch_data().then(function (result) {
                var report_dashboard = QWeb.render('dtdream_sale_data_report.sale_report', {
                    'cash_income_sum' : result.cash_income_sum,
                    'area' : result.areas
                });
                super_render.call(self);

                $(report_dashboard).prependTo(self.$el);
                self.$el.find('.oe_view_nocontent').hide();

                 //设置时间日期插件
                self.settingDatetimepicker();
                //设置选项卡区域的相关效果
                self.settingSliderArea();
                self.getEchartData().then(function (result) {
                    var areaName = result.office_names;

                })
                var selContent=$("#area").val();
                if(selContent=="selectArea"){
                    data=["北京分部","杭州办","南京办","成都办","天津联络处","郑州联络处","长沙联络处","武汉联络处","昆明联络处","西宁联络处","西安联络处","兰州联络处","长春联络处","战略发展部"];
                    seriesContent=[{
                        "name":"政务",
                        "type":"bar",
                        "stack":"总数",    //设置柱状图堆叠显示
                        "barMaxWidth":35,
                        "barGap":"10%",
                        "itemStyle":{
                            "normal":{
                                "color":"#1A69AD",
                                "label":{
                                    "show":true,
                                    "textStyle":{
                                        "color":"#fff"
                                    },
                                    "position":"insideTop",
                                    formatter:function(p){
                                        return p.value > 0 ? (p.value):"";
                                    }
                                }
                            }
                        },
                        "data":allSeriesData["政务"]
                    },{
                        "name":"政法",
                        "type":"bar",
                        "stack":"总数",    //设置柱状图堆叠显示
                        "barMaxWidth":35,
                        "barGap":"10%",
                        "itemStyle":{
                            "normal":{
                                "color":"#1F8AE7",
                                "label":{
                                    "show":true,
                                    "textStyle":{
                                        "color":"#fff"
                                    },
                                    "position":"insideTop",
                                    formatter:function(p){
                                        return p.value > 0 ? (p.value):"";
                                    }
                                }
                            }
                        },
                        "data":allSeriesData["政法"]
                    },{
                        "name":"企业",
                        "type":"bar",
                        "stack":"总数",    //设置柱状图堆叠显示
                        "barMaxWidth":35,
                        "barGap":"10%",
                        "itemStyle":{
                            "normal":{
                                "color":"#1FC2E7",
                                "label":{
                                    "show":true,
                                    "textStyle":{
                                        "color":"#fff"
                                    },
                                    "position":"insideTop",
                                    formatter:function(p){
                                        return p.value > 0 ? (p.value):"";
                                    }
                                }
                            }
                        },
                        "data":allSeriesData["企业"]
                    },{
                        "name":"专网",
                        "type":"bar",
                        "stack":"总数",    //设置柱状图堆叠显示
                        "barMaxWidth":35,
                        "barGap":"10%",
                        "itemStyle":{
                            "normal":{
                                "color":"#21D3FF",
                                "label":{
                                    "show":true,
                                    "textStyle":{
                                        "color":"#fff"
                                    },
                                    "position":"insideTop",
                                    formatter:function(p){
                                        return p.value > 0 ? (p.value):"";
                                    }
                                }
                            }
                        },
                        "data":allSeriesData["专网"]
                    },{
                        "name":"电力",
                        "type":"bar",
                        "stack":"总数",    //设置柱状图堆叠显示
                        "barMaxWidth":35,
                        "barGap":"10%",
                        "itemStyle":{
                            "normal":{
                                "color":"#67E1FF",
                                "label":{
                                    "show":true,
                                    "textStyle":{
                                        "color":"#fff"
                                    },
                                    "position":"insideTop",
                                    formatter:function(p){
                                        return p.value > 0 ? (p.value):"";
                                    }
                                }
                            }
                        },
                        "data":allSeriesData["电力"]
                    }];
                }
                self.marketingData($("#cashEchart")[0],$("#cashpie")[0],"现金收入");
            });
        },
        getEchartData:function(){
            return new Model('dtdream.sale.data.report')
                .call('get_echart_data', []);
        },
        settingDatetimepicker:function(){
            $(".datepickerstart").datetimepicker({
                    format:'YYYY-MM-DD',
                    todayBtn:  true,
                    autoclose: true,
                    language: 'zh-CN'
                });
            $(".start").click(function(){
                $(".datepickerstart").datetimepicker('show');
            });
            $(".datepickerend").datetimepicker({
                format:'YYYY-MM-DD',
                language: 'zh-CN'
            });
            $(".end").click(function(){
                $(".datepickerend").datetimepicker('show');
            });
        },
        settingSliderArea:function(){
            var super_render = this._super;
            var self = this;
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

                $("#"+dropId).addClass('in').siblings('.in').removeClass('in');
                if(!$(this).hasClass('active')){
                    $(this).addClass('active').siblings('.active').removeClass('active');
                }

                var sliceSelectArea=$(this).data("index").slice(2);
                var SelectAreaBar=$(".tab-content").find("#"+sliceSelectArea+"Echart")[0];
                var SelectAreaPie=$(".tab-content").find("#"+sliceSelectArea+"pie")[0];
                var echartTitle=this.innerText.replace(/^\s+|\s+$/g,"");
                if(this.innerText)
                self.marketingData(SelectAreaBar,SelectAreaPie,echartTitle);
            });
        },
        click_queryBtn: function(){
            var self = this;
            var activeArea=$("#MKmyTab").find("li.active").data("index").slice(2);
            var nowechartsTitle=$("#MKmyTab li.active a").html().trim();
            var nowbarid=$("#"+activeArea+"Echart")[0];
            var nowpieid=$("#"+activeArea+"pie")[0];
            self.marketingData(nowbarid,nowpieid,nowechartsTitle);
        },
        marketingData: function(barid,pieid,echartTitle){
            /*//点击查询按钮时，更新图表的数据
            $("#selectQueryBtn").click(function(){
                cashEchart.xAxis[0].data = data;
                cashEchart.series=seriesContent;
                mychart.setOption(cashEchart);
            });
*/

            //设置柱状图标题和饼图标题
            var bartitle="";
            var pietitle=echartTitle+"占比情况";
            if(echartTitle == "现金收入"){
                bartitle="现金收入与销售目标完成率(万元)"
            }else{
                bartitle=echartTitle+"统计表(万元)";
            }
            console.log(data,seriesContent);
            /*图表处理*/

            //柱状图
            var mychart=echarts.init(barid);
            var cashEchart={
                backgroundColor:"#F9FAFC",
                title:{
                    text:bartitle,
                    left:"100",
                    top:"20",
                    textStyle:{color:"#67727C"}
                },
                tooltip:{
                    trigger:'axis',   //设置坐标轴触发
                    axisPointer:{     //设置阴影指示器
                        type:"shadow",
                        shadowColor:"#fff"
                    }
                },
                legend:{
                    data:['政务','政法','企业','专网','电力'],
                    right:"10%",
                    top:"50"
                },
                grid:{
                    show:true,
                    top:"80",
                    left:"100",
                    bottom:"85",
                    borderWidth:"0.5"
                },
            //        calculable: true,
                xAxis:[{
                    type:"category",
                    splitLine: {
                        "show": false
                    },
                    axisLine:{
                        lineStyle: {
                            color: '#90979c'
                        }
                    },
                    axisTick: {
                        "show": false
                    },
                    axisLabel: {
                        "interval": 0,
                        "rotate":"35"
                    },
                    splitArea: {
                        "show": false
                    },
                    data:data
                }],
                yAxis:[{
                    type:"value",
                    splitLine: {
                        "show": true
                    },
                    axisLine:{
                        lineStyle: {
                            color: '#90979c'
                        }
                    },
                    axisTick: {
                        "show": false
                    },
                    axisLabel: {
                        "interval": 0
                    },
                    splitArea: {
                        "show": false
                    },
                    /*min:0,
                    max:3500,
                    interval:300*/
                }],
                series:seriesContent,
                dataZoom:[{
                    "type":"slider",
                    "height": 30,
                    "xAxisIndex": [0],
                    "backgroundColor":"#fff",
                    "bottom":"5",
                    "end": 80,
                    "textStyle":{color:"#6B747F"},
                    "borderColor":"#90979c",
                    "fillterColor":"#EDF2F7",
                    "handleIcon": 'path://M306.1,413c0,2.2-1.8,4-4,4h-59.8c-2.2,0-4-1.8-4-4V200.8c0-2.2,1.8-4,4-4h59.8c2.2,0,4,1.8,4,4V413z',
                    "handleSize": '110%',
                    "handleStyle":{
                        "color":"#B8CDDD",
                        "borderColor":"#A4BDD0"
                    }
                }]
            };
            mychart.setOption(cashEchart);

            //饼图
            var mychartpie=echarts.init(pieid);
            var cashpie={
                backgroundColor:"#F9FAFC",
                title : {
                    text: pietitle,
                    top:"20",
                    left:"20",
                    textStyle:{color:"#67727C"}
                },
                tooltip : {
                    trigger: 'item',
                    formatter: "{a} <br/>{b} : {c} ({d}%)"
                },
                series : [
                    {
                        name: '占比情况',
                        type: 'pie',
                        radius : '55%',
                        center: ['50%', '60%'],
                        data:[
                            {
                                value:835,
                                name:'政务',
                                selected:true,
                                itemStyle:{
                                    normal:{color:"#1A69AD"}
                                }
                            },
                            {
                                value:310,
                                name:'政法',
                                selected:true,
                                itemStyle:{
                                    normal:{color:"#1F8AE7"}
                                }
                            },
                            {
                                value:234,
                                name:'企业',
                                selected:true,
                                itemStyle:{
                                    normal:{color:"#1FC2E7"}
                                }
                            },
                            {
                                value:135,
                                name:'专网',
                                selected:true,
                                itemStyle:{
                                    normal:{color:"#21D3FF"}
                                }
                            },
                            {
                                value:648,
                                name:'电力',
                                selected:true,
                                itemStyle:{
                                    normal:{color:"#67E1FF"}
                                }
                            }
                        ],
                        label:{
                            normal:{
                                textStyle:{color:"#7A848D"}
                            }
                        },
                        labelLine:{
                            normal:{
                                show:false
                            },
                            emphasis:{
                                show:false
                            }
                        },
                        itemStyle: {
                            emphasis: {
                                shadowBlur: 10,
                                shadowOffsetX: 0,
                                shadowColor: 'rgba(0, 0, 0, 0.5)'
                            }
                        }
                    }
                ]
            };
            mychartpie.setOption(cashpie);

        }
    });

    core.view_registry.add('dtdream_sale_data_report', DataReportDashboardView);

    return DataReportDashboardView

});
