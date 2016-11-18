firstchartid=echarts.init(document.getElementById("firstchart")); //显示区域的id
option  =  {
    title:  {
        text:  '本年个人业务事项',
        top:'10%',
        left:'1%',
        textStyle:{
            fontSize:14,
        }
    },
    color:['#65B6A8','#F06C73','#C191E9','#76C470','#82A4DE',  '#F7AF6A','#65B6A8'],

    tooltip:  {
        trigger:  'axis'
    },
    legend:  {
        data:['申请项目','完成项目'],
        top:'10%',
        right:'1%',
    },
    grid:  {
        show:false,
        width:'90%',
         x:'5%',
        y:'35%',
        bottom:'15%',


    },
    xAxis:  {
        type:  'category',
        boundaryGap:  false,
        data:  ['1月','2月','3月','4月','5月','6月','7月','8月','9月','10月','11月','12月']

    },
    yAxis:  {
        type:  'value',
        splitLine:{
            show:true,
            lineStyle:{
                color:'#fff'
            }
        }
    },

    series:  [
        {
            name:'申请项目',
            type:'line',
            smooth:true,
            areaStyle: {normal: {
                color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{
                    offset: 0, color: 'rgba(101,182,168,.9)' // 0% 处的颜色
                }, {
                    offset: 1, color: 'rgba(101,182,168,0)' // 100% 处的颜色
                }], false)

            }},
            data:[4,  5,  10,  35,  23,  11,  23,  5,  10,  35,  23,2]
        },
        {
            name:'完成项目',
            type:'line',
            smooth:true,
            areaStyle: {normal: {
                color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{
                    offset: 0, color: 'rgba(240,108,115,.9)' // 0% 处的颜色
                }, {
                    offset: 1, color: 'rgba(240,108,115,0)' // 100% 处的颜色
                }], false)

            }},
            data:[1,12,  15,  9,  25,  23,  15,  24,  15,  0,  15,3]
        }

    ]
};
firstchartid.setOption(option);



relatechatsid=echarts.init(document.getElementById("relatechats")); //显示区域的id


option  =  {
    tooltip:  {
        trigger:  'item',
    },
    title:  {
        text:  '与我相关的项目',
        textStyle:{
            color:'#4a4a4a',
            fontSize:14,
            fontWeight:'normal',
        },
        top:'8%',
        left:'5%',
    },
    legend:  {
        orient:  'vertical',
        align:'left',
        bottom:'10%',
       data:[
            {
                name:'研发产品',
                icon:'pin',
            },
            {
                name:'产品推广',
                icon:'pin',
            },
            {
                name:'渠道活动',
                icon:'pin',
            },
            {
                name:'产品销售',
                icon:'pin',
            },
        ],

        right:'12%',
        textStyle:{
            fontStyle:'normal',
            fontSize:12,
        },
    },
    grid:{

    },

    color:['#65B6A8','#76C470','#82A4DE', '#C191E9', '#F06C73', '#F7AF6A','#65B6A8'],
    series:  [
        {
            name:'访问来源',
            type:'pie',
            radius:  ['35%',  '65%'],
            center: ['25%', '60%'],
            avoidLabelOverlap:  false,

            label:  {
                normal:  {
                    show:  false,
                    position:  'center'
                },
                emphasis:  {
                    show:  true,
                    textStyle:  {
                        fontSize:  '12',
                        fontWeight:  'normal',
                    }
                }
            },
            labelLine:  {
                normal:  {
                    show:  false,
                }
            },
            data:[
                {value:32,  name:'研发产品'},
                {value:30,  name:'产品开发'},
                {value:23,  name:'产品推广'},
                {value:13,  name:'渠道活动'},
                {value:5,  name:'产品销售'}
            ]
        }
    ]
};
relatechatsid.setOption(option);