/**
 * Created by mm on 2017/1/24.
 */
//设置第二个选项框里面的内容
var province=[
    ["北京市"],
    ["浙江省","上海市","广西省","海南省","福建省","江西省"],
    ["江苏省","安徽省","山东省"],
    ["广东省","深圳市"],
    ["四川省","天津市","河北省","河南省","湖南省","湖北省","云南省","青海省","陕西省","甘肃省","吉林省","宁夏自治区","内蒙古自治区"],
    ["战略发展部"]
];

var ProvinceDetail={
    "北京市":["北1","北2","北3","北4","北5","北6"],
    "浙江省":["浙1","浙2","浙3","浙4","浙5","浙6"],
    "上海市":["上1","上2","上3","上4","上5","上6"],
    "广西省":["广西1","广西2","广西3","广西4","广西5","广西6"],
    "海南省":["海南1","海南2","海南3","海南4","海南5","海南6"],
    "福建省":["福建1","福建2","福建3","福建4","福建5","福建6"],
    "江西省":["江西1","江西2","江西3","江西4","江西5","江西6"],
    "江苏省":["江苏1","江苏2","江苏3","江苏4","江苏5","江苏6"],
    "安徽省":["安徽1","安徽2","安徽3","安徽4","安徽5","安徽6"],
    "山东省":["山东1","山东2","山东3","山东4","山东5","山东6"],
    "广东省":["广东1","广东2","广东3","广东4","广东5","广东6"],
    "深圳市":["深圳1","深圳2","深圳3","深圳4","深圳5","深圳6"],
    "四川省":["川1","川2","川3","川4","川5","川6"],
    "天津市":["天津1","天津2","天津3","天津4","天津5","天津6"],
    "河北省":["河北1","河北2","河北3","河北4","河北5","河北6"],
    "河南省":["河南1","河南2","河南3","河南4","河南5","河南6"],
    "湖南省":["湖南1","湖南2","湖南3","湖南4","湖南5","湖南6"],
    "湖北省":["湖北1","湖北2","湖北3","湖北4","湖北5","湖北6"],
    "云南省":["云1","云2","云3","云4","云5","云6"],
    "青海省":["青海1","青海2","青海3","青海4","青海5","青海6"],
    "陕西省":["陕西1","陕西2","陕西3","陕西4","陕西5","陕西6"],
    "甘肃省":["甘肃1","甘肃2","甘肃3","甘肃4","甘肃5","甘肃6"],
    "吉林省":["吉林1","吉林2","吉林3","吉林4","吉林5","吉林6"],
    "宁夏自治区":["宁夏1","宁夏2","宁夏3","宁夏4","宁夏5","宁夏6"],
    "内蒙古自治区":["内蒙古1","内蒙古2","内蒙古3","内蒙古4","内蒙古5","内蒙古6"],
    "战略发展部":["战略发展1","战略发展2","战略发展3","战略发展4","战略发展5","战略发展6"]
};

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
var selContent=$("#area").val();
var data="";
var seriesContent="";
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

//设置选择第二个选项框时的数据
function getProvinces(area){
    var nowSelProvince=$("#selectprovince").find("option:selected").text();
    if(nowSelProvince != "请选择"){
        data=ProvinceDetail[nowSelProvince];
    }
    return data;
}

function getSeriesData(area){
    var nowSelProvince=$("#selectprovince").find("option:selected").text();
    if(nowSelProvince != "请选择"){
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
}

//获取第二个选项框对应的内容
function getSelectvalue(value){
    if(value != "selectArea"){
        var nowSelProvince=province[value];
        return nowSelProvince;
    }
}

//第一个选项框选项发生变化：
$("#area").on("change",function(){
    var nowSelValue=$(this).find("option:selected").text();
    //设置第二个选项框显示
    if(nowSelValue == "选择区域"){
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
        //设置第二个选项框显示
        $("#selectprovince").css("display","block");

        //设置第二个选项框里面的内容
        var selectNum=$(this).val();
        var slProvinces=getSelectvalue(selectNum);
        var html="<option value='00' selected>请选择</option>";
        for(var i=0;i<slProvinces.length;i++){
            html+="<option value='"+i+"'>"+slProvinces[i]+"</option>";
        }
        $("#selectprovince").html(html);

        data=province[selectNum];
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

        // 设置数据
        $("#selectprovince").on("change",function(){
            if($(this).val() == "00"){
                data=province[selectNum];
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
                data=getProvinces(nowSelValue);
                seriesContent=getSeriesData(nowSelValue);
            }
        });
    }

});

//点击查询按钮时，更新图表的数据
$("#selectQueryBtn").click(function(){

    //现金收入
    cashEchart.xAxis[0].data = data;
    cashEchart.series=seriesContent;
    mychart.setOption(cashEchart);

    //合同额
    bargainEchart.xAxis[0].data = data;
    bargainEchart.series=seriesContent;
    bargainmychart.setOption(bargainEchart,true);

    //中标额
    winningEchart.xAxis[0].data = data;
    winningEchart.series=seriesContent;
    winningmychart.setOption(winningEchart,true);

    //运作中项目空间
    spaceEchart.xAxis[0].data = data;
    spaceEchart.series=seriesContent;
    spacemychart.setOption(spaceEchart,true);

    //GAAP收入
    GaapEchart.xAxis[0].data = data;
    GaapEchart.series=seriesContent;
    Gaapmychart.setOption(GaapEchart,true);
});

/*图表处理*/

//现金收入柱状图
var mychart=echarts.init(document.getElementById('cashEchart'));
var cashEchart={
    backgroundColor:"#F9FAFC",
    title:{
        text:"现金收入与销售目标完成率(万元)",
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
        top:"20"
    },
    grid:{
        show:true,
        top:"80",
        left:"100",
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
            "interval": 0
//                rotate:"45"
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
mychart.resize();
/*mychart.on("legendselectchanged",function(param){
    console.log(param);
});*/


//现金收入饼图
var mychartpie=echarts.init(document.getElementById('cashpie'));
var cashpie={
    backgroundColor:"#F9FAFC",
    title : {
        text: '现金收入占比情况',
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
mychart.resize();


//合同额柱状图
var bargainmychart=echarts.init(document.getElementById('bargainEchart'));
var bargainEchart={
    backgroundColor:"#F9FAFC",
    title:{
        text:"合同额统计表(万元)",
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
        top:"20"
    },
    grid:{
        show:true,
        top:"80",
        left:"100",
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
//                rotate:"45"
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
bargainmychart.setOption(bargainEchart,true);
bargainmychart.resize();
//合同额饼图
var bargainmychartpie=echarts.init(document.getElementById('bargainpie'));
var bargainpie={
    backgroundColor:"#F9FAFC",
    title : {
        text: '合同额占比情况',
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
bargainmychartpie.setOption(bargainpie);
bargainmychartpie.resize();

//中标额柱状图
var winningmychart=echarts.init(document.getElementById('winningEchart'));
var winningEchart={
    backgroundColor:"#F9FAFC",
    title:{
        text:"中标额统计表(万元)",
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
        top:"20"
    },
    grid:{
        show:true,
        top:"80",
        left:"100",
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
//                rotate:"45"
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
winningmychart.setOption(winningEchart,true);
winningmychart.resize();
//中标额饼图
var winningmychartpie=echarts.init(document.getElementById('winningpie'));
var winningpie={
    backgroundColor:"#F9FAFC",
    title : {
        text: '中标额占比情况',
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
winningmychartpie.setOption(winningpie);
winningmychartpie.resize();

//运作中项目空间柱状图
var spacemychart=echarts.init(document.getElementById('spaceEchart'));
var spaceEchart={
    backgroundColor:"#F9FAFC",
    title:{
        text:"运作中项目空间统计表(万元)",
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
        top:"20"
    },
    grid:{
        show:true,
        top:"80",
        left:"100",
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
//                rotate:"45"
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
spacemychart.setOption(spaceEchart,true);
spacemychart.resize();
//运作中项目空间饼图
var spacemychartpie=echarts.init(document.getElementById('spacepie'));
var spacepie={
    backgroundColor:"#F9FAFC",
    title : {
        text: '运作中项目空间占比情况',
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
spacemychartpie.setOption(spacepie);
spacemychartpie.resize();

//GAAP收入柱状图
var Gaapmychart=echarts.init(document.getElementById('GaapEchart'));
var GaapEchart={
    backgroundColor:"#F9FAFC",
    title:{
        text:"GAAP收入统计表(万元)",
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
        top:"20"
    },
    grid:{
        show:true,
        top:"80",
        left:"100",
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
//                rotate:"45"
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
Gaapmychart.setOption(GaapEchart,true);
Gaapmychart.resize();
//GAAP收入饼图
var Gaapmychartpie=echarts.init(document.getElementById('Gaappie'));
var Gaappie={
    backgroundColor:"#F9FAFC",
    title : {
        text: 'GAAP收入占比情况',
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
Gaapmychartpie.setOption(Gaappie);
Gaapmychartpie.resize();