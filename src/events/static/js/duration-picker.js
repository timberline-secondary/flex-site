/**
 * Created by Tartarus762 on 10/13/16.
 * https://github.com/Tartarus762/jquery-duration-picker
 *
 * Modified by Tylere Couture to parse django's DurationField text widget
 */
(function ($) {

    // Constructor for durationpicker 'class'
    var durationPicker = function (element, options) {
        this.settings = options;
        this.stages = get_stages(this.settings);
        this.template = generate_template(this.settings, this.stages);
        this.jqitem = $(this.template);
        this.jqchildren = this.jqitem.children();
        this.element = $(element);
        this.setup();
        this.resize();
        this.jqchildren.find(".durationpicker-duration").trigger('change');
        var _self = this;
    };

    durationPicker.prototype = {
        constructor: durationPicker,
        setup: function () {
            this.element.before(this.jqitem);
            this.element.hide();
            this.jqchildren.find(".durationpicker-duration").on('change', {ths: this}, function (ev) {
                var element = ev.data.ths.element;
                var value = "";
                // parsing the input
                $(this).parent().parent().find('input').each(function (i) {
                    var input = $(this);
                    var val = 0;
                    if (input.val() != null && input.val() != ""){
                        val = input.val();
                    }
                    // value += val + input.next().text() + ",";
                    value += val;
                    value += (i == 0 ? " ": ":");
                });
                value += "00"; // add second on the end for django DurationField
                // value = value.slice(0, -1);
                element.val(value);
            });

            // $(".durationpicker-duration").trigger();
            window.addEventListener('resize', this.resize);
        },
        resize: function() {
            // if (!this.settings.responsive) {
            //     return
            // }
            var padding = parseInt(this.jqitem.css('padding-left').split('px')[0]) + parseInt(this.jqitem.css('padding-right').split('px')[0]);
            var minwidth = padding;
            var minheight = padding;
            this.jqchildren.each(function () {
                var ths = $(this);
                minwidth = minwidth + ths.outerWidth();
                minheight = minheight + ths.outerHeight();
            });
            if (this.jqitem.parent().width() < minwidth) {
                this.jqchildren.each(function () {
                    var ths = $(this);
                    ths.css('display', 'block');
                });
                this.jqitem.css('height', minheight)
            }
            else {
                this.jqchildren.each(function () {
                    var ths = $(this);
                    ths.css('display', 'inline-block');
                });
            }
        },
        getitem: function () {
            return this.jqitem;
        },
        setvalues: function (values) {
            set_values(values, this)
        },
        disable: function () {
            this.jqchildren.children("input").each(function (index, item) {
                item.readOnly = true;
            });
        },
        enable: function () {
            this.jqchildren.children("input").each(function (index, item) {
                item.readOnly = false;
            });
        }
    };

    $.fn.durationPicker = function(options){
        if (options == undefined) {
            var settings = $.extend(true, {}, $.fn.durationPicker.defaults, options);
        }
        else {
            var settings = $.extend(true, {}, {classname: 'form-control', responsive: true}, options);
        }

        // return this.each(function () {
        return new durationPicker(this, settings);
        // })
    };

    function set_values(values, self){
        for (var value in Object.keys(values)){
            if (self.stages.indexOf(Object.keys(values)[value]) != -1){
                self.jqitem.find("#duration-" + (Object.keys(values)[value])).val(values[(Object.keys(values)[value])]);
            }
        }
    }

    function get_stages(settings){
        var stages = [];
        for (var key in Object.keys(settings)){
            if (['classname', 'responsive'].indexOf(Object.keys(settings)[key]) == -1) {
                stages.push(Object.keys(settings)[key]);
            }
        }
        return stages
    }

    function generate_template (settings, stages) {
        // var stages = [];
        // for (var key in Object.keys(settings)){
        //     if (['classname', 'responsive'].indexOf(Object.keys(settings)[key]) == -1) {
        //         stages.push(Object.keys(settings)[key]);
        //     }
        // }

        var html = '<div class="durationpicker-container ' + settings.classname + '">';
        for (var item in stages){
            html += '<div class="durationpicker-innercontainer"><input min="' + settings[stages[item]]['min'] + '" max="' + settings[stages[item]]['max'] + '" placeholder="0" type="number" id="duration-' + stages[item] + '" class="durationpicker-duration" ><span class="durationpicker-label">' + settings[stages[item]]['label'] + '</span></div>';
        }
        html += '</div>';

        return html
    }

    $.fn.durationPicker.defaults = {
        hours: {
        	label: "h",
        	min: 0,
        	max: 24,
            seperator: ":",
        },
        minutes: {
        	label: "m",
        	min: 0,
        	max: 59,
            seperator: ":",
        },
        seconds: {
        	label: "s",
        	min: 0,
        	max: 59,
            seperator: ":",
        },
        classname: 'form-control',
        responsive: true
    };

    $.fn.durationPicker.Constructor = durationPicker;

})(jQuery);
