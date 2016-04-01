odoo.define('web_gantt.GanttView', function (require) {
"use strict";

var core = require('web.core');
var formats = require('web.formats');
var Model = require('web.Model');
var time = require('web.time');
var View = require('web.View');
var form_common = require('web.form_common');
var Dialog = require('web.Dialog');

var _t = core._t;
var _lt = core._lt;
var QWeb = core.qweb;


var GanttView = View.extend({
    display_name: _lt('Gantt'),
    icon: 'fa-tasks',
    template: 'GanttView',
    view_type: 'gantt',

    events: {
        'click .gantt_task_row .gantt_task_cell': 'create_on_click',
    },

    init: function () {
        this._super.apply(this, arguments);
        this.has_been_loaded = $.Deferred();
        this.chart_id = _.uniqueId();
        this.focus_date = moment(new Date());  // main date displayed on the gantt chart

        // Gantt configuration
        this.gantt_events = [];
        gantt.config.autosize = "y";
        gantt.config.round_dnd_dates = false;
        gantt.config.drag_links = false;
        gantt.config.drag_progress = false;
        gantt.config.grid_width = 250;
        gantt.config.row_height = 30;
        gantt.config.duration_unit = "hour";
        gantt.config.initial_scroll = false;
        gantt.config.preserve_scroll = true;
        gantt.config.columns = [{
            name: "text",
            label: _lt("Gantt View"),
            tree: true,
            width: '*'
        }];
        gantt.templates.grid_folder = function () {
            return "";
        };
        gantt.templates.grid_file = function () {
            return "";
        };
        gantt.templates.grid_indent = function () {
            return "<div class='gantt_tree_indent' style='width:20px;'></div>";
        };
        gantt.config.start_on_monday = moment().startOf("week").day();
    },

    view_loading: function (fields_view_get) {
        var self = this;
        this.fields_view = fields_view_get;
        this.$el.addClass(this.fields_view.arch.attrs.class);

        // Use scale_zoom attribute in xml file to specify zoom timeline (day,week,month,year),
        // by default month.
        var scale = fields_view_get.arch.attrs.scale_zoom;
        if (!_.contains(['day', 'week', 'month', 'year'], scale)) {
            self.scale = "month";
        }

        // The type of the view : 
        // gantt = classic gantt view (default)
        // consolidate = values of the first children are consolidated in the gantt's task
        // planning = children are displayed in the gantt's task
        this.type = this.fields_view.arch.attrs.type || 'gantt';

        // dnd by date
        if (fields_view_get.arch.attrs.round_dnd_dates) {
            gantt.config.round_dnd_dates = true;
        }

        // Configure the duration_unit
        if (fields_view_get.arch.attrs.duration_unit) {
            gantt.config.duration_unit = fields_view_get.arch.attrs.duration_unit;
        }
        
        // gather the fields to get
        var fields_to_gather = [
            "date_start",
            "date_delay",
            "date_stop",
            "consolidation",
            "progress"
        ];
        var fields = _.compact(_.map(fields_to_gather, function(key) {
            return fields_view_get.arch.attrs[key] || '';
        }));
        fields.push("name", "color");

        // consolidation exclude, get the related fields
        if (fields_view_get.arch.attrs.consolidation_exclude) {
            fields = fields.concat(fields_view_get.arch.attrs.consolidation_exclude);
        }

        this.fields_to_fetch = fields;  //FIXME: useless?

        // configure templates for dhtmlXGantt
        
        // the class of the task bar
        gantt.templates.task_class = function (start, end, task) {
            var classes = ["o_gantt_color" + task.color + "_0"];
            if (self.type === "consolidate" || self.type === "planning") {
                classes.push('consolidation');
                if (task.is_group) {
                    classes.push("has_child");
                } else {
                    classes.push("is_leaf");
                }
            }
            return classes.join(" ");
        };

        // the class for the rows
        gantt.templates.task_row_class = function (start, end, task) {
            var classes = ["level_" + task.$level];
            return classes;
        };

        // The class for the cells
        gantt.templates.task_cell_class = function (item, date) {
            var classes = "date_" + date.getTime();
            var today = new Date();
            if (self.scale !== "year" && (date.getDay() === 0 || date.getDay() === 6)) {
                classes += " weekend_task";
            }
            if (self.scale !== "day" && date.getDate() === today.getDate() && date.getMonth() === today.getMonth() && date.getYear() === today.getYear()) {
                classes += " today";
            }
            return classes;
        };

        gantt.templates.date_scale = null;

        // Task text format
        gantt.templates.task_text = function (start, end, task) {
            // default
            var text = "";
            // consolidation
            if (self.type === "consolidate" || self.type === "planning") {
                if (task.is_group) {
                    text = self._consolidation_children(task);
                } else {
                    text = task.consolidation + "<span class=\"half_opacity\"> " + self.fields[self.fields_view.arch.attrs.consolidation].string + "</span>";
                }
            }
            return text;
        };

        return self.alive(new Model(this.dataset.model)
                   .call('fields_get')).then(function (fields) {
                       self.fields = fields;
                       self.has_been_loaded.resolve();
                   });
    },

    destroy: function () {
        while (this.gantt_events.length)
            gantt.detachEvent(this.gantt_events.pop());

        this._super.apply(this, arguments);
    },

    do_show: function () {
        this.do_push_state({});
        return this._super.apply(this, arguments);
    },

    do_search: function (domains, contexts, group_bys) {
        var self = this;
        self.last_domains = domains;
        self.last_contexts = contexts;
        self.last_group_bys = group_bys;

        this.display_focus_date();
        // add the date range to the domain.
        var from_date = self.focus_date.clone().subtract(1, self.scale).startOf(self.scale);
        var to_date = self.focus_date.clone().add(3, self.scale).endOf(self.scale);
        domains = domains.concat([ [self.fields_view.arch.attrs.date_start, '<', to_date.format("YYYY-MM-DD")] ]);
        if (self.fields_view.arch.attrs.date_stop) {
            domains = domains.concat([
                '|',
                [self.fields_view.arch.attrs.date_stop, ">", from_date.format("YYYY-MM-DD")],
                [self.fields_view.arch.attrs.date_stop, '=', false]
            ]);
        }

        // define the width
        gantt.config.start_date = from_date;
        gantt.config.end_date = to_date.add(1, self.scale);

        // select the group by
        var n_group_bys = [];
        if (this.fields_view.arch.attrs.default_group_by) {
            n_group_bys = this.fields_view.arch.attrs.default_group_by.split(',');
        }
        if (group_bys.length) {
            n_group_bys = group_bys;
        }

        // Consolidation maximum options
        self.consolidation_max = false;
        if (self.fields_view.arch.attrs.consolidation_max) {
            var max = JSON.parse(self.fields_view.arch.attrs.consolidation_max);
            if (max[group_bys[0]]) {
                self.consolidation_max = max[group_bys[0]];
            }
        }

        var fields = self.fields_to_fetch.concat(n_group_bys);
        return $.when(this.has_been_loaded).then(function() {
            return new Model(self.dataset.model).query().filter(domains).context(contexts)
                .group_by(n_group_bys);
            }).then(function(data) {
                self.first_groups = data;
                return self.dataset.read_slice(fields, {
                    domain: domains,
                    context: contexts
            }).then(function(data) {
                return self.fetch_colors(data, n_group_bys);
            });
        });
    },

    fetch_colors: function (tasks, group_bys) {
        var self = this;
        if (self.type === 'gantt' || group_bys.length === 0) {
            return self.on_data_loaded(tasks, group_bys);
        }
        // Load the color for the group_bys
        // Prepare an object with the model in key, and an array of ids in value
        var model_ids = {};
        _.each(tasks, function (task) {
            _.each(group_bys, function (group) {
                var model = self.fields[group].relation;
                var id = task[group];
                if (model && id){
                    if (!model_ids[model]) {
                        model_ids[model] = [];
                    }
                    model_ids[model].push(id[0]);
                }
            });
        });
        // remove duplicate
        _.each(model_ids, function(ids, model){
            model_ids[model] = _.uniq(ids);
        });
        
        // Fetch the color for the specified ids in the specified model
        var color_by_group = {};
        var fetch = function (keys) {
            if (keys.length === 0) {
                return self.on_data_loaded(tasks, group_bys, color_by_group);
            } else {
                var key = _.first(keys);
                if (!key) {
                    return fetch(_.rest(keys)); // not a relation field
                }
                new Model(key)
                    .query(["color"])
                    .filter([ ['id', 'in', model_ids[key]] ])
                    .all()
                    .then(function (colors) {
                        if (!color_by_group[key]) {
                            color_by_group[key] = {};
                        }
                        _.each(colors, function (color) {
                            color_by_group[key][color.id] = color.color;
                        });
                        return fetch(_.rest(keys));
                    });
            }
        };
        var keys = [];
        for(var k in model_ids) {
            keys.push(k);
        }
        fetch(keys);
    },

    change_focus_date_left: function () {
        this.focus_date = this.focus_date.subtract(1, this.scale);
        this.display_focus_date();
        this.reload();
    },

    change_focus_date_right: function () {
        this.focus_date = this.focus_date.add(1, this.scale);
        this.display_focus_date();
        this.reload();
    },

    display_focus_date: function () {
        // range date
        // Format to display it
        var date_display;
        switch(this.scale) {
            case "day":
                date_display = this.focus_date.format("D MMM");
                break;
            case "week":
                var date_start = this.focus_date.clone().startOf("week").format("D MMM");
                var date_end = this.focus_date.clone().endOf("week").format("D MMM");
                date_display = date_start + " - " + date_end;
                break;
            case "month":
                date_display = this.focus_date.format("MMMM YYYY");
                break;
            case "year":
                date_display = this.focus_date.format("YYYY");
                break;
        }
        this.set({'title': 'Forecast (' + date_display + ')'});
    },

    change_scale_button: function (e) {
        this.scale = e.target.value;
        this.reload();
    },

    reload: function () {
        if (this.last_domains !== undefined) {
            return this.do_search(this.last_domains, this.last_contexts, this.last_group_bys);
        }
    },

    /**
     * Prepare the tasks and group by's to be handled by dhtmlxgantt and render
     * the view. This function also contains workaround to the fact that
     * the gantt view cannot be rendered in a documentFragment.
     */
    on_data_loaded: function (tasks, group_bys, color_by_group) {
        var self = this;

        // Prepare the tasks
        tasks = _.compact(_.map(tasks, function (task) {
            var task_start = time.auto_str_to_date(task[self.fields_view.arch.attrs.date_start]);
            if (!task_start) {
                return false;
            }

            var task_stop;
            var percent;
            if (self.fields_view.arch.attrs.date_stop) {
                task_stop = time.auto_str_to_date(task[self.fields_view.arch.attrs.date_stop]);
                if (!task_stop) {
                    task_stop = moment(task_start).clone().add(1, 'hours');
                }
            } else { // we assume date_duration is defined
                var tmp = formats.format_value(task[self.fields_view.arch.attrs.date_delay],
                                                    self.fields[self.fields_view.arch.attrs.date_delay]);
                if (!tmp) {
                    return false;
                }
                var m_task_start = moment(task_start).add(tmp, gantt.config.duration_unit);
                task_stop = m_task_start.toDate();
            }

            if (_.isNumber(task[self.fields_view.arch.attrs.progress])) {
                percent = task[self.fields_view.arch.attrs.progress] || 0;
            } else {
                percent = 100;
            }

            task.task_start = task_start;
            task.task_stop = task_stop;
            task.percent = percent;

            // Don't add the task that stops before the min_date
            // Usefull if the field date_stop is not defined in the gantt view
            if (self.min_date && task_stop < new Date(self.min_date)) {
                return false;
            }
            
            return task;
        }));
        
        // get the groups
        var split_groups = function(tasks, group_bys) {
            if (group_bys.length === 0) {
                return tasks;
            }
            // Create the group of the first level (with query.group_by())
            // TODO : this code is duplicate with the group created on the other level
            var groups = [];
            for (var g in self.first_groups) {
                var new_g = {tasks: [], __is_group: true,
                             group_start: false, group_stop: false, percent: [],
                             open: true};
                new_g.name = self.first_groups[g].attributes.value;
                new_g.create = [_.first(group_bys), self.first_groups[g].attributes.value];
                // the group color
                var model = self.fields[_.first(group_bys)].relation;
                if (model && _.has(color_by_group, model)) { 
                    new_g.consolidation_color = color_by_group[model][new_g.name[0]];
                }

                // folded or not
                if ((self.fields_view.arch.attrs.fold_last_level && group_bys.length <= 1) || 
                    self.last_contexts.fold_all ||
                    self.type === 'planning') {
                    new_g.open = false;
                }
                        
                groups.push(new_g);
            }
            _.each(tasks, function (task) {
                var group_name = task[_.first(group_bys)];
                var group = _.find(groups, function (group) {
                    return _.isEqual(group.name, group_name);
                });
                if (group === undefined) {
                    // Create the group of the other levels
                    group = {name:group_name, tasks: [], __is_group: true,
                             group_start: false, group_stop: false, percent: [],
                             open: true};
                    
                    // Add the group_by information for creation
                    group.create = [_.first(group_bys), task[_.first(group_bys)]];

                    // folded or not
                    if ((self.fields_view.arch.attrs.fold_last_level && group_bys.length <= 1) || 
                        self.last_contexts.fold_all ||
                        self.type === 'planning') {
                        group.open = false;
                    }

                    // the group color
                    var model = self.fields[_.first(group_bys)].relation;
                    if (model && _.has(color_by_group, model)) { 
                        group.consolidation_color = color_by_group[model][group_name[0]];
                    }
                        
                    groups.push(group);
                }
                if (!group.group_start || group.group_start > task.task_start) {
                    group.group_start = task.task_start;
                }
                if (!group.group_stop || group.group_stop < task.task_stop) {
                    group.group_stop = task.task_stop;
                }
                group.percent.push(task.percent);
                if (self.open_task_id === task.id && self.type !== 'planning') {
                    group.open = true; // Show the just created task
                }
                group.tasks.push(task);
            });
            _.each(groups, function (group) {
                group.tasks = split_groups(group.tasks, _.rest(group_bys));
            });
            return groups;
        };
        var groups = split_groups(tasks, group_bys);

        // If there is no task, add a dummy one
        if (groups.length === 0) {
            groups = [{
                'id': 1,
                'name': '',
                'task_start': self.focus_date,
                'task_stop': self.focus_date,
                'duration': 1,
            }];
        }

        // Creation of the chart
        var gantt_tasks = [];
        var generate_tasks = function(task, level, parent_id) {
            if ((task.__is_group && !task.group_start) || (!task.__is_group && !task.task_start)) {
                return;
            }
            if (task.__is_group) {
                // Only add empty group for the first level
                if (level > 0 && task.tasks.length === 0){
                    return;
                }

                var project_id = _.uniqueId("gantt_project_");
                var group_name = task.name ? formats.format_value(task.name, self.fields[group_bys[level]]) : "-";
                // progress
                var sum = _.reduce(task.percent, function(acc, num) { return acc+num; }, 0);
                var progress = sum / task.percent.length / 100 || 0;
                var t = {
                    'id': project_id,
                    'text': group_name,
                    'is_group': true,
                    'start_date': task.group_start,
                    'duration': gantt.calculateDuration(task.group_start, task.group_stop),
                    'progress': progress,
                    'create': task.create,
                    'open': task.open,
                    'consolidation_color': task.color,
                };
                if (parent_id) { t.parent = parent_id; }
                gantt_tasks.push(t);
                _.each(task.tasks, function(subtask) {
                    generate_tasks(subtask, level+1, project_id);
                });
            }
            else {
                // Consolidation
                gantt_tasks.push({
                    'id': "gantt_task_" + task.id,
                    'text': task.name,
                    'start_date': task.task_start,
                    'duration': gantt.calculateDuration(task.task_start, task.task_stop),
                    'progress': task.percent / 100,
                    'parent': parent_id,
                    'consolidation': task[self.fields_view.arch.attrs.consolidation],
                    'consolidation_exclude': task[self.fields_view.arch.attrs.consolidation_exclude],
                    'color': task.color,
                });
            }
        };
        _.each(groups, function(group) { generate_tasks(group, 0); });
        // horrible hack to make sure that something is in the dom with the required id.  The problem is that
        // the view manager render the view in a document fragment. More explaination : GED
        var temp_div_with_id;
        if (this.$div_with_id){
            temp_div_with_id = this.$div_with_id;
        }
        this.$div_with_id = $('<div>').attr('id', this.chart_id);
        this.$div_with_id.wrap('<div></div>');
        this.$div = this.$div_with_id.parent().css({
        });
        this.$div.prependTo(document.body);

        // Initialize the gantt chart
        while (this.gantt_events.length)
            gantt.detachEvent(this.gantt_events.pop());
        self.scale_zoom(self.scale);
        gantt.init(this.chart_id);
        gantt._click.gantt_row = undefined; // Remove the focus on click

        gantt.clearAll();
        gantt.showDate(self.focus_date);
        gantt.parse({"data": gantt_tasks});

        gantt.sort(function(a, b){
            if (gantt.hasChild(a.id) && !gantt.hasChild(b.id)){
                return -1;
            } else if (!gantt.hasChild(a.id) && gantt.hasChild(b.id)) {
                return 1;
            } else {
                return 0;
            }
        });

        // End of horrible hack
        var scroll_state = gantt.getScrollState();
        this.$el.append(this.$div.contents());
        gantt.scrollTo(scroll_state.x, scroll_state.y);
        this.$div.remove();
        if (temp_div_with_id) temp_div_with_id.remove();

        self._configure_gantt_chart(tasks, group_bys, gantt_tasks);
    },

    _configure_gantt_chart: function (tasks, group_bys, groups) {
        var self = this;
        this.gantt_events.push(gantt.attachEvent("onTaskClick", function (id, e) {
            // If we are in planning, we want a single click to open the task. If there is more than one task in the clicked range, the bar is unfold
            if (self.type === 'planning' && e.target.className.indexOf('inside_task_bar') > -1) {
                var ids = e.target.attributes.consolidation_ids.value;
                if (ids.indexOf(" ") > -1){
                    // There is more than one task
                    return true;
                } else {
                    // There is only one task
                    return self.on_task_display(gantt.getTask(ids));
                }
            }

            // If we are not in a planning, the bar is unfolded if children
            if(gantt.getTask(id).is_group) return true;
            
            // Case where the user want to make an action on a task click
            var attr = self.fields_view.arch.attrs;
            if(e.target.className == "gantt_task_content" || e.target.className == "gantt_task_drag task_left" || e.target.className == "gantt_task_drag task_right") {
                if(attr.action) {
                    var actual_id = parseInt(id.split("gantt_task_").slice(1)[0]);
                    if(attr.relative_field) {
                        new Model("ir.model.data").call("xmlid_lookup", [attr.action]).done(function(result) {
                            var add_context = {};
                            add_context["search_default_" + attr.relative_field] = actual_id;
                            self.do_action(result[2], {'additional_context': add_context});
                        });
                    }
                    return false;
                }
            }

            // If the user click on an empty row, it start a crate widget
            if (id.indexOf("unused") >= 0) {
                var task = gantt.getTask(id);
                var key = "default_"+task.create[0];
                var context = {};
                context[key] = task.create[1][0];
                self.on_task_create(context);
            } else {
                self.on_task_display(gantt.getTask(id));
            }
            return true;
        }));
        // Remove double click
        this.gantt_events.push(gantt.attachEvent("onTaskDblClick", function(){ return false; }));
        // Fold and unfold project bar when click on it
        this.gantt_events.push(gantt.attachEvent("onBeforeTaskSelected", function(id) {
            if(gantt.getTask(id).is_group){
                $("[task_id="+id+"] .gantt_tree_icon").click();
                return false;
            }
            return true;
        }));

        // Drag and drop
        var update_date_parent = function(id) {
            // Refresh parent when children are resize
            var start_date, stop_date;
            var clicked_task = gantt.getTask(id);
            if (!clicked_task.parent) {
                return;
            }

            var parent = gantt.getTask(clicked_task.parent);

            _.each(gantt.getChildren(parent.id), function(task_id){
                var task_start_date = gantt.getTask(task_id).start_date;
                var task_stop_date = gantt.getTask(task_id).end_date;
                if(!start_date) start_date = task_start_date;
                if(!stop_date) stop_date = task_stop_date;
                if(start_date > task_start_date) start_date = task_start_date;
                if(stop_date < task_stop_date) stop_date = task_stop_date;
            });
            parent.start_date = start_date;
            parent.end_date = stop_date;
            gantt.updateTask(parent.id);
            if (parent.parent) update_date_parent(parent.id);
        };
        /**
         * Triggered at the start of a task drag. We use this hook to store directly on the
         * tasks their current date start/end so that we can restore their state if the drag
         * is not successful.
         */
        this.gantt_events.push(gantt.attachEvent("onBeforeTaskDrag", function(id, mode, e){
            var task = gantt.getTask(id);
            task._original_start_date = task.start_date;
            task._original_end_date = task.end_date;
            this.lastX = e.pageX;
            if (task.is_group) {
                var attr = e.target.attributes.getNamedItem("consolidation_ids");
                if (attr) {
                    var children = attr.value.split(" ");
                    this.drag_child = children;
                    _.each(this.drag_child, function(child_id) {
                        var child = gantt.getTask(child_id);
                        child._original_start_date = child.start_date;
                        child._original_end_date = child.end_date;
                    });
                }
            }
            return true;
        }));
        this.gantt_events.push(gantt.attachEvent("onTaskDrag", function(id, mode, task, original, e){
            if(gantt.getTask(id).is_group){
                // var d is the number of millisecond for one pixel
                var d;
                if (self.scale === "day") d = 72000;
                if (self.scale === "week") d = 1728000;
                if (self.scale === "month") d = 3456000;
                if (self.scale === "year") d = 51840000;
                var diff = (e.pageX - this.lastX) * d;
                this.lastX = e.pageX;

                if (task.start_date > original.start_date){ task.start_date = original.start_date; }
                if (task.end_date < original.end_date){ task.end_date = original.end_date; }

                if (this.drag_child){
                    _.each(this.drag_child, function(child_id){
                        var child = gantt.getTask(child_id);
                        var nstart = +child.start_date + diff;
                        var nstop = +child.end_date + diff;
                        if (nstart < gantt.config.start_date || nstop > gantt.config.end_date){
                            return false;
                        }
                        child.start_date = new Date(nstart);
                        child.end_date = new Date(nstop);
                        gantt.updateTask(child.id);
                        update_date_parent(child_id);
                    });
                }
                gantt.updateTask(task.id);
                return false;
            }
            update_date_parent(id);
            return true;
        }));

        /**
         * This will call `on_task_changed`, which will write in the dataset. This write can fail
         * if, for example, constraints defined on the model are not met. In this case, we have to
         * replace the task at its original place.
         */
        this.gantt_events.push(gantt.attachEvent("onAfterTaskDrag", function(id){
            var update_task = function (task_id) {
                var task = gantt.getTask(task_id);
                self.on_task_changed(task).fail(function () {
                    task.start_date = task._original_start_date;
                    task.end_date = task._original_end_date;
                    gantt.updateTask(task_id);
                    delete task._original_start_date;
                    delete task._original_end_date;
                }).always(function () {
                    update_date_parent(task_id);
                });
            }

            // A group of tasks has been dragged
            if (gantt.getTask(id).is_group && this.drag_child) {
                _.each(this.drag_child, function(child_id) {
                    update_task(child_id);
                });
            }

            // A task has been dragged
            update_task(id);
        }));

        this.gantt_events.push(gantt.attachEvent("onGanttRender", function() {
            // show the focus date
            if(!self.open_task_id || self.type == 'planning'){
                gantt.showDate(self.focus_date);
            } else {
                if (gantt.isTaskExists("gantt_task_"+self.open_task_id)) {
                    gantt.showTask("gantt_task_"+self.open_task_id);
                    gantt.selectTask("gantt_task_" + self.open_task_id);
                }
            }

            self.open_task_id = undefined;

            return true;
        }));
    },

    scale_zoom: function (value) {
        gantt.config.step = 1;
        gantt.config.min_column_width = 50;
        gantt.config.scale_height = 50;
        var today = new Date();
        
        switch (value) {
            case "day":
                gantt.templates.scale_cell_class = function(date) {
                    if(date.getDay() === 0 || date.getDay() === 6) return "weekend_scale";
                };
                gantt.config.scale_unit = "day";
                gantt.config.date_scale = "%d %M";
                gantt.config.subscales = [{unit:"hour", step:1, date:"%H h"}];
                gantt.config.scale_height = 27;
                break;
            case "week":
                var weekScaleTemplate = function(date){
                    var dateToStr = gantt.date.date_to_str("%d %M %Y");
                    var endDate = gantt.date.add(gantt.date.add(date, 1, "week"), -1, "day");
                        return dateToStr(date) + " - " + dateToStr(endDate);
                };
                gantt.config.scale_unit = "week";
                gantt.templates.date_scale = weekScaleTemplate;
                gantt.config.subscales = [
                    {unit:"day", step:1, date:"%d, %D", css:function(date) {
                        if(date.getDay() === 0 || date.getDay() === 6) return "weekend_scale";
                        if(date.getMonth() === today.getMonth() && date.getDate() === today.getDate()) return "today";
                    } }
                ];
                break;
            case "month":
                gantt.config.scale_unit = "month";
                gantt.config.date_scale = "%F, %Y";
                gantt.config.subscales = [
                    {unit:"day", step:1, date:"%d", css:function(date) {
                        if (date.getDay() === 0 || date.getDay() === 6) {
                            return "weekend_scale";
                        }
                        if (date.getMonth() === today.getMonth() && date.getDate() === today.getDate()) {
                            return "today";
                        }
                    } }
                ];
                gantt.config.min_column_width = 25;
                break;
            case "year":
                gantt.config.scale_unit = "year";
                gantt.config.date_scale = "%Y";
                gantt.config.subscales = [
                    {unit:"month", step:1, date:"%M" }
                ];
                break;
        }
    },

    on_task_changed: function (task_obj) {
        // We first check that the fields aren't defined as readonly.
        if (this.fields[this.fields_view.arch.attrs.date_start].readonly || this.fields[this.fields_view.arch.attrs.date_stop].readonly) {
            Dialog.alert(this, _t('You are trying to write on a read-only field!'));
            return $.Deferred().reject();
        }
        if (this.fields_view.arch.attrs.date_stop === undefined) {
            // Using a duration field instead of date_stop
            Dialog.alert(this, _t('You have no date_stop field defined!'));
            return $.Deferred().reject();
        }

        // Now we try to write the new values in the dataset. Note that it may fail
        // if the constraints defined on the model aren't met.
        var self = this;
        var start = task_obj.start_date;
        var end = task_obj.end_date;
        var data = {};
        data[self.fields_view.arch.attrs.date_start] =
            time.auto_date_to_str(start, self.fields[self.fields_view.arch.attrs.date_start].type);
        if (self.fields_view.arch.attrs.date_stop) {
            data[self.fields_view.arch.attrs.date_stop] = 
                time.auto_date_to_str(end, self.fields[self.fields_view.arch.attrs.date_stop].type);
        } else { // we assume date_duration is defined
            var duration = gantt.calculateDuration(start, end);
            data[self.fields_view.arch.attrs.date_delay] = duration;
        }
        var task_id = parseInt(task_obj.id.split("gantt_task_").slice(1)[0], 10);
        return this.dataset.write(task_id, data);
    },

    /**
     * Dialog to edit/display a task.
     */
    on_task_display: function (task) {
        var self = this;
        var task_id = parseInt(_.last(task.id.split("_")), 10);
        self.open_task_id = task_id;
        new form_common.FormViewDialog(this, {
            res_model: this.dataset.model,
            res_id: task_id,
            view_id: +this.open_popup_action,
            context: this.dataset.context,
            buttons: [
                {text: _lt("Save"), classes: 'btn-primary', close: true, click: function () {
                    this.view_form.save().then(function () {
                        self.reload();
                    });
                }},
                {text: _lt("Delete"), classes: 'btn-default', close: true, click: function () {
                    $.when(self.dataset.unlink([task_id])).then(function () {
                        $.when(self.dataset.remove_ids([task_id])).then(function () {
                            self.open_task_id = false;
                            self.reload();
                        });
                    });
                }},
                {text: _lt("Close"), classes: 'btn-default', close: true}
            ]
        }).open();
    },

    /**
     * Dialog to create a task.
     */
    on_task_create: function (context) {
        var self = this;
        new form_common.FormViewDialog(this, {
            res_model: this.dataset.model,
            view_id: +this.open_popup_action,
            context: context,
            buttons: [
                {text: _lt("Create"), classes: 'btn-primary', close: true, click: function(){
                    this.view_form.save().then(function(){
                        self.reload();
                    });
                }},
                {text: _lt("Close"), classes: 'btn-default', close: true}
            ]
        }).open();
    },

    /**
     * Handler used when clicking on an empty cell. The behaviour is to create a new task
     * and apply some default values.
     */
    create_on_click: function (e) {
        var self = this;
        var id = e.target.parentElement.attributes.task_id.value;
        var task = gantt.getTask(id);
        
        var class_date = _.find(e.target.classList, function (e) {
            return e.indexOf("date_") > -1;
        });
        var start_date = moment(new Date(parseInt(class_date.split("_")[1], 10))).utc();

        var end_date;
        switch (self.scale) {
            case "day":
                end_date = start_date.clone().add(4, "hour");
                break;
            case "week":
                end_date = start_date.clone().add(2, "day");
                break;
            case "month":
                end_date = start_date.clone().add(4, "day");
                break;
            case "year":
                end_date = start_date.clone().add(2, "month");
                break;
        }

        var create = {};
        var get_create = function (item) {
            if (item.create) {
                create["default_"+item.create[0]] = item.create[1][0];
            }
            if (item.parent) {
                var parent = gantt.getTask(item.parent);
                get_create(parent);
            }
        };
        get_create(task);

        create["default_"+self.fields_view.arch.attrs.date_start] = start_date.format("YYYY-MM-DD HH:mm:ss");
        if(self.fields_view.arch.attrs.date_stop) {
            create["default_"+self.fields_view.arch.attrs.date_stop] = end_date.format("YYYY-MM-DD HH:mm:ss");
        } else { // We assume date_delay is given
            create["default_"+self.fields_view.arch.attrs.date_delay] = gantt.calculateDuration(start_date, end_date);
        }

        self.on_task_create(create);
    },

    _get_all_children: function (id) {
        var children = [];
        gantt.eachTask(function (task) {
            if (!task.is_group) {
                children.push(task.id);
            }
        }, id);
        return children;
    },

    _consolidation_children: function (parent) {
        var self = this;
        var group_bys = self.last_group_bys;
        var children = self._get_all_children(parent.id);

        // First step : create a list of object for the children. The contains (left, consolidation
        // value, consolidation color) where left is position in the bar, and consolidation value is
        // the number to add or remove, and the color is [color, sequence] from the last group_by
        // with these information.
        var leftParent = gantt.getTaskPosition(parent, parent.start_date, parent.end_date).left;
        var getTuple = function(acc, task_id) {
            var task = gantt.getTask(task_id);
            var position = gantt.getTaskPosition(task, task.start_date, task.end_date || task.start_date);
            var left = position.left - leftParent;
            var right = left + position.width;
            var start = {type: "start",
                         task: task,
                         left: left,
                         consolidation: task.consolidation,
                        };
            var stop = {type: "stop",
                        task: task,
                        left: right,
                        consolidation: -(task.consolidation),
                       };
            if (task.consolidation_exclude) {
                start.consolidation_exclude = true;
                start.color = task.consolidation_color;
                stop.consolidation_exclude = true;
                stop.color = task.consolidation_color;
            }
            acc.push(start);
            acc.push(stop);
            return acc;
        };
        var steps = _.reduce(children, getTuple, []);

        // Second step : Order it by "left"
        var orderSteps = _.sortBy(steps, function (el) {
            return el.left;
        });

        // Third step : Create the html for the bar
        // html : the final html code
        var html = "";
        // acc : the amount to display inside the task
        var acc = 0;
        // last_left : the left position of the previous task
        var last_left = 0;
        // exclude : A list of task that are not compatible with the other ones (must be hached)
        var exclude = [];
        // not_exclude : the number of task, that are compatible
        var not_exclude = 0;
        // The ids of the task (exclude and not_exclude)
        var ids = [];
        orderSteps.forEach(function (el) {
            var width = Math.max(el.left - last_left , 0);
            var padding_left = (width === 0) ? 0 : 4;
            if (not_exclude > 0 || exclude.length > 0) {
                var classes = [];
                //content
                var content;
                if (self.type === 'consolidate') {
                    var label = self.fields_view.arch.attrs.consolidation_label || self.fields[self.fields_view.arch.attrs.consolidation].string;
                    content = acc + "<span class=\"half_opacity\"> " + label + "</span>";
                    if (acc === 0 || width < 15 || (self.consolidation_max && acc === self.consolidation_max)) content = "";
                } else {
                    if (exclude.length + not_exclude > 1) {
                        content = exclude.length + not_exclude;
                    } else {
                        content = el.task.text;
                    }
                }
                //pointer
                var pointer = (exclude.length === 0 && not_exclude === 0) ? "none" : "all";
                // Color 
                if (exclude.length > 0) {
                    classes.push("o_gantt_color" + _.last(exclude) + "_0");
                    if (not_exclude) {
                        classes.push("exclude");
                    }
                } else {
                    var opacity = (self.consolidation_max) ? 5 - Math.floor(10*((acc/(2*self.consolidation_max)))) : 1;
                    if (acc === 0){
                        classes.push("transparent");
                    } else if ((self.consolidation_max) && acc > self.consolidation_max){
                        classes.push("o_gantt_color_red");
                    } else if (self.consolidation_max && parent.create[0] === group_bys[0]) {
                        classes.push("o_gantt_colorgreen_" + opacity);
                    } else if (parent.consolidation_color){
                        classes.push("o_gantt_color" + parent.consolidation_color + "_" + opacity);
                    } else {
                        classes.push("o_gantt_color7_" + opacity);
                    }
                }
                html += "<div class=\"inside_task_bar "+ classes.join(" ") +"\" consolidation_ids=\"" + 
                    ids.join(" ") + "\" style=\"pointer-events: "+pointer+"; padding-left: "+ padding_left + 
                    "px; left:"+(last_left )+"px; width:"+width+"px;\">"+content+"</div>";
            }
            acc = acc + el.consolidation;
            last_left = el.left;
            if(el.type === "start"){
                if (el.consolidation_exclude ) exclude.push(el.task.color);
                else not_exclude++;
                ids.push(el.task.id);
            } else {
                if(el.consolidation_exclude) exclude.pop();
                else not_exclude--;
                ids = _.without(ids, el.task.id);
            }
        });
        return html;
    },

    /**
     * Render the buttons according to the GanttView.buttons template and add listeners on it.
     * Set this.$buttons with the produced jQuery element
     * @param {jQuery} [$node] a jQuery node where the rendered buttons should be inserted
     * $node may be undefined, in which case they are inserted into this.options.$buttons
     */
    render_buttons: function($node) {
        var self = this;
        if ($node) {
            var $buttons = $(QWeb.render("GanttView.buttons", {'widget': this}));
            $buttons.appendTo($node);
            $buttons.find('.o_gantt_button_scale').bind('click', function (event) {
                return self.change_scale_button(event);
            });
            $buttons.find('.o_gantt_button_left').bind('click', function () {
                return self.change_focus_date_left();
            });
            $buttons.find('.o_gantt_button_right').bind('click', function () {
                return self.change_focus_date_right();
            });
            $buttons.find('.o_gantt_button_today').bind('click', function () {
                self.focus_date = moment(new Date());
                return self.reload();
            });
        }
    },
});

core.view_registry.add('gantt', GanttView);

return GanttView;
});
