/*
odoo.define('dtdream_contract.test', function(require) {
    var Sidebar = require('web.Sidebar');
    var core = require('web.core');
    var FormView = require('web.FormView');
    Sidebar.include({
        on_attachments_loaded: function(attachments) {
            alert(123);
        //to display number in name if more then one attachment which has same name.
        var self = this;
        _.chain(attachments)
             .groupBy(function(attachment) { return attachment.name; })
             .each(function(attachment){
                 if(attachment.length > 1)
                     _.map(attachment, function(attachment, i){
                         attachment.name = _.str.sprintf(_t("%s (%s)"), attachment.name, i+1);
                     });
              });
        self._super(attachments);
    },
    });
});

*/
