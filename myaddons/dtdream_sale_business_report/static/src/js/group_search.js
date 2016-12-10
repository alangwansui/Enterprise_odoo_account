odoo.define('dtdream_sale_business_report.web.GroupByMenu', function (require) {
"use strict";

var GroupByMenu = require('web.GroupByMenu');
var Widget = require('web.Widget');
var core = require('web.core');
var search_inputs = require('web.search_inputs');
var Model = require('web.DataModel');
var QWeb = core.qweb;

return GroupByMenu.include({
    start: function () {
        var self = this;
        self._super.apply(this,arguments);
        var divider = this.$menu.find('.divider');
        this.fields_def.then(function () {

            if (this.data && JSON.parse(this.data).params.model == "dtdream.sale.business.report"){
                this.dtdream_sale_business_report = new Model('dtdream.sale.business.report');
                this.dtdream_sale_business_report.call('if_hide',[]).done(function (rec) {
                    if (rec){
                        self.$add_group.hide();
                        divider.hide()
                    }
                })
            }
        });
    },
});

});