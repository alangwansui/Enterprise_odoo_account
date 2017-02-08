odoo.define('dtdream_report.test', function (require) {
"use strict";
var data = require('web.data');
var core = require('web.core');
var csrf_token = core['csrf_token'];
var Model = require('web.Model');
var _t = core._t;
var FormView = require('web.FormView');
var rec_id;
FormView.include({
    // Stores all the parameters of the action.
    //load_record: function(record) {
    //    this._super.apply(this, arguments);
    //    var timer = window.setInterval(function(){
    //        if($('.apply_dis_sale_report th:eq(6)').length != 0){
    //            if (record.is_bus_shenpiren == false && record.is_pro_shenpiren == true){
    //                if(!$('.apply_dis_sale_report th:eq(6)').is(":hidden")){
    //                    $('.apply_dis_sale_report th:eq(6)').hide();
    //                    $('.apply_dis_sale_report td[data-field="apply_discount"]').hide();
    //                    clearInterval(timer);
    //                }
    //            }
    //            else
    //                clearInterval(timer);
    //        }
    //    },300)
    //},

    events: _.defaults({
        'click .dtdream_import': 'import_click',
        'change .dtdream_import_file' : 'onchange_file',
        'click .dtdream_download': 'download_click',
    }, FormView.prototype.events),

    download_click: function(kwargs) {
        window.open("../dtdream_sale_business_report/static/src/downloads/pro_list_module.xlsx")
    },

    import_click: function(kwargs) {
        rec_id = parseInt(window.location.href.split('=')[1].split('&')[0])
        var self=this;
        var context = self.getParent().action.context;
        context['params']['id'] = rec_id;
        self.do_action({
            type: 'ir.actions.client',
            tag: 'import',
            params: {
                model: "dtdream.product.line",
                context: context
            }
        }, {
            on_reverse_breadcrumb: function () {
                return self.reload();
            },
        });
        return false;


    },

     // XMLHttpRequest Level 2 file uploads (big hat tip to francois2metz)
    fileUploadXhr:function (a,options) {
        var options = options || {};
        var formdata = new FormData();

        for (var i=0; i < a.length; i++) {
            formdata.append(a[i].name, a[i].value);
        }

        if (options.extraData) {
            var serializedData = deepSerialize(options.extraData);
            for (i=0; i < serializedData.length; i++) {
                if (serializedData[i]) {
                    formdata.append(serializedData[i][0], serializedData[i][1]);
                }
            }
        }

        options.data = null;

        var s = $.extend(true, {}, $.ajaxSettings, options, {
            contentType: false,
            processData: false,
            cache: false,
            type: 'GET'
        });

        if (options.uploadProgress) {
            // workaround because jqXHR does not expose upload property
            s.xhr = function() {
                var xhr = $.ajaxSettings.xhr();
                if (xhr.upload) {
                    xhr.upload.addEventListener('progress', function(event) {
                        var percent = 0;
                        var position = event.loaded || event.position; /*event.position is deprecated*/
                        var total = event.total;
                        if (event.lengthComputable) {
                            percent = Math.ceil(position / total * 100);
                        }
                        options.uploadProgress(event, position, total, percent);
                    }, false);
                }
                return xhr;
            };
        }

        s.data = null;
        var beforeSend = s.beforeSend;
        s.beforeSend = function(xhr, o) {
            //Send FormData() provided by user
            if (options.formData) {
                o.data = options.formData;
            }
            else {
                o.data = formdata;
            }
            if(beforeSend) {
                beforeSend.call(this, xhr, o);
            }
        };
        return $.ajax(s);
    },

    onchange_file:function(rec){
        var a=[]
        a.push({name: 'file', value: $('.dtdream_import_file')[0].files[0]});
        var ajax_data = $.param(a,undefined)
        var options={
            url:"/dtdream_sale_business_report/set_file",
            type:"get",
            dataType:'script',
            data: ajax_data,
            success:function(result){
                alert(123)
            },
            error:function(err){
                console.log(err);
            }
        }
        this.fileUploadXhr(a,options)
    },

     // XMLHttpRequest Level 2 file uploads (big hat tip to francois2metz)
});
})


