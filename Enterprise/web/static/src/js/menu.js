odoo.define('web.Menu', function (require) {
"use strict";

var core = require('web.core');
var Widget = require('web.Widget');
var SystrayMenu = require('web.SystrayMenu');
var UserMenu = require('web.UserMenu');

SystrayMenu.Items.push(UserMenu);

var QWeb = core.qweb;

var Menu = Widget.extend({
    template: 'Menu',
    events: {
        'click .o_menu_toggle': function (ev) {
            ev.preventDefault();
            this.trigger_up((this.appswitcher_displayed)? 'hide_app_switcher' : 'show_app_switcher');
        },
        'mouseover .o_menu_sections > li:not(.open)': function(e) {
            var $opened = this.$('.o_menu_sections > li.open');
            if($opened.length) {
                $opened.removeClass('open');
                $(e.currentTarget).addClass('open').find('> a').focus();
            }
        },
    },
    init: function (parent, menu_data) {
        var self = this;
        this._super.apply(this, arguments);
        this.appswitcher_displayed = true;
        this.backbutton_displayed = false;

        this.$menu_sections = {};
        this.menu_data = menu_data;

        // Prepare navbar's menus
        var $menu_sections = $(QWeb.render('Menu.sections', {'menu_data': this.menu_data}));
        $menu_sections.filter('section').each(function () {
            self.$menu_sections[parseInt(this.className, 10)] = $(this).children('li');
        });

        // Bus event
        core.bus.on('change_menu_section', this, this.change_menu_section);
    },
    start: function () {
        var self = this;

        this.$menu_toggle = this.$('.o_menu_toggle');
        this.$menu_brand_placeholder = this.$('.o_menu_brand');
        this.$section_placeholder = this.$('.o_menu_sections');

        core.bus.on('keyup', this, this._hide_app_switcher);

        // Navbar's menus event handlers
        var menu_ids = _.keys(this.$menu_sections);
        var primary_menu_id, $section;
        for(var i = 0; i < menu_ids.length; i++) {
            primary_menu_id = menu_ids[i];
            $section = this.$menu_sections[primary_menu_id];
            $section.on('click', 'a[data-menu]', self, function (ev) {
                ev.preventDefault();
                var menu_id = $(ev.currentTarget).data('menu');
                var action_id = $(ev.currentTarget).data('action-id');
                self._on_secondary_menu_click(menu_id, action_id);
            });
        };

        // Systray Menu
        this.systray_menu = new SystrayMenu(this);
        this.systray_menu.attachTo(this.$('.oe_systray'));

        return this._super.apply(this, arguments);
    },
    destroy: function () {
        this._super.apply(this, arguments);
        core.bus.off('keyup', this, this._hide_app_switcher);
    },
    _hide_app_switcher: function (ev) {
        if (ev.keyCode === $.ui.keyCode.ESCAPE && this.backbutton_displayed) {
            this.trigger_up('hide_app_switcher');
        }
    },
    toggle_mode: function (appswitcher, overapp) {
        this.appswitcher_displayed = !!appswitcher;
        this.backbutton_displayed = this.appswitcher_displayed && !!overapp;

        this.$menu_toggle.find('i').toggleClass('fa-chevron-left', this.appswitcher_displayed)
                                   .toggleClass('fa-th', !this.appswitcher_displayed);

        this.$menu_toggle.toggleClass('hidden', this.appswitcher_displayed && !this.backbutton_displayed);
        this.$menu_brand_placeholder.toggleClass('hidden', this.appswitcher_displayed);
        this.$section_placeholder.toggleClass('hidden', this.appswitcher_displayed);
    },
    change_menu_section: function (primary_menu_id) {
        if (!this.$menu_sections[primary_menu_id]) {
            return; // unknown menu_id
        }

        if (this.current_primary_menu) {
            this.$menu_sections[this.current_primary_menu].detach();
        }

        // Get back the application name
        for (var i = 0; i < this.menu_data.children.length; i++) {
            if (this.menu_data.children[i].id === primary_menu_id) {
                this.$menu_brand_placeholder.text(this.menu_data.children[i].name);
                break;
            }
        }

        this.$menu_sections[primary_menu_id].appendTo(this.$section_placeholder);
        this.current_primary_menu = primary_menu_id;
    },
    _trigger_menu_clicked: function(menu_id, action_id) {
        this.trigger_up('menu_clicked', {
            id: menu_id,
            action_id: action_id,
            previous_menu_id: this.current_secondary_menu || this.current_primary_menu,
        });
    },
    _on_secondary_menu_click: function(menu_id, action_id) {
        var self = this;

        // It is still possible that we don't have an action_id (for example, menu toggler)
        if (action_id) {
            self._trigger_menu_clicked(menu_id, action_id);
            this.current_secondary_menu = menu_id;
        }
    },
    /**
     * Helpers used by web_client in order to restore the state from
     * an url (by restore, read re-synchronize menu and action manager)
     */
    action_id_to_primary_menu_id: function (action_id) {
        var primary_menu_id, found;
        for (var i = 0; i < this.menu_data.children.length && !primary_menu_id; i++) {
            found = this._action_id_in_subtree(this.menu_data.children[i], action_id);
            if (found) {
                primary_menu_id = this.menu_data.children[i].id;
            }
        }
        return primary_menu_id;
    },
    _action_id_in_subtree: function (root, action_id) {
        if (root.action && root.action.split(',')[1] == action_id) {
            return true;
        }
        var found;
        for (var i = 0; i < root.children.length && !found; i++) {
            found = this._action_id_in_subtree(root.children[i], action_id);
        }
        return found;
    },
    menu_id_to_action_id: function (menu_id, root) {
        if (!root) {root = $.extend(true, {}, this.menu_data)}

        if (root.id == menu_id) {
            return root.action.split(',')[1] ;
        }
        for (var i = 0; i < root.children.length; i++) {
            var action_id = this.menu_id_to_action_id(menu_id, root.children[i]);
            if (action_id !== undefined) {
                return action_id;
            }
        }
        return undefined;
    },
});

return Menu;
});
