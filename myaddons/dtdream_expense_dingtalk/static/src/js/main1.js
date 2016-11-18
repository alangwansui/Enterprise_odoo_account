odoo.define('project_timeshee.ui', function (require) {
    "use strict";
    var core = require('web.core');
    var session = require('web.session');
    var Widget = require('web.Widget');
    var time_module = require('web.time');
    var Model = require('web.Model');

    var QWeb = core.qweb;


    var ProjectTimesheet = Widget.extend({
        users: [],
        template: "app",
        init: function (parent) {
            var self = this;
            this._super(parent);
            this.load_template();
            this.ab = [1, 2, 3, 4, 5];
            console.log('my ');

            // this.users=[{
            //     'name':'fuck 1',
            // },{
            //     'name':'fuck 2',
            // }]

        },
        start: function (parent) {
            this._super(parent);
            var self = this;

            var def = new $.Deferred();

            new Model('res.users')
                .query(['name', 'login', 'user_email', 'signature'])
                .filter([['active', '=', true]])
                .limit(15)
                .all({'timeout': 3000, 'shadow': true})
                .then(function (partners) {
                    // do work with users records
                    // console.log(self);
                    if (self.render_data(partners,self.$el)){
                        def.resolve();
                    }else{
                        def.reject();
                    }
                    // var $users = $(QWeb.render('expense.users', {'users': partners}));
                    // $users.appendTo('.o_expense');
                    // console.log($users);
                    // def.resolve();
                }, function (err, event) {
                    event.preventDefault();
                    def.reject();
                }
            );

            return def;

            // var self = this;
            // var def = new $.Deferred();
            // // var fields = _.find(this.models, function (model) {
            // //     return model.model === 'res.users';
            // // }).fields;
            // new Model('res.users')
            //     .query(['name', 'login', 'user_email', 'signature'])
            //     .filter([['active', '=', true]])
            //     .limit(15)
            //     .all({'timeout': 3000, 'shadow': true})
            //     .then(function (partners) {
            //         if (self.db.add_partners(partners)) {   // check if the partners we got were real updates
            //             def.resolve();
            //         } else {
            //             def.reject();
            //         }
            //     }, function (err, event) {
            //         event.preventDefault();
            //         def.reject();
            //     });
            // return def;


        },
        render_data:function(users,$el){
            var $users = $(QWeb.render('expense.users', {'users': users}));
            $el.find('.o_expense').prepend($users);
            //         $users.appendTo('.o_expense');
        },
        load_template: function () {
            var xml = $.ajax({
                url: "static/src/xml/expense.xml",
                async: false // necessary as without the template there isn't much to do.
            }).responseText;
            QWeb.add_template(xml);
        },
    });

    return ProjectTimesheet;
});