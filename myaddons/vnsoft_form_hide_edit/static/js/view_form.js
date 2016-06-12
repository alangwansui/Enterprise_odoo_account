
openerp.vnsoft_form_hide_edit = function(instance){
    console.log(instance)
    instance.web.FormView.include({
            do_push_state: function (state) {
                var self = this;
                this._super.apply(this, arguments);
                if(this.options.action){
                     var no_edit = this.options.action.context.form_no_edit
                    if(no_edit!=undefined && no_edit.length>0){
                        var no_edit_result = this.compute_domain(no_edit);
                        if(this.get("actual_mode")=="view") {
                            if(no_edit_result==true){
                                this.$buttons.find(".o_form_button_edit").hide()
                            }else{
                                this.$buttons.find(".o_form_button_edit").show()
                            }
                        }
                        else if(this.get("actual_mode")=="edit") {
                            if(no_edit_result==true){
                                this.$buttons.find(".o_form_button_edit").hide()
                            }else{
                                this.$buttons.find(".o_form_button_edit").show()
                            }
                        }
                    }
                }
            }
        }
    );

    //instance.web.TreeView.include({
    //    init: function () {
    //        console.log('listview')
    //        var self = this;
    //        this._super.apply(this, arguments);
    //        var no_create = this.options.action.context.list_no_create
    //        if(no_create!=undefined){
    //            this.ViewManager.__parentedParent.__parentedParent.$el.find('.o_list_button_add').hide()
    //        }
    //    }
    //});




}