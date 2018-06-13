"use strict";

function Form(properties) {

    if (properties) {
        this.fields = properties['fields'];
        this.selector = properties['selector'];
    }

    this.submit = function() {
        throw "NotImplementedError";
    }
}



function WorkItemForm(workItem, selector, formset) {

    this.selector = '#' + selector

    this.job = new SelectField('job', workItem.job.id, this.selector);
    this.hours = new WorkItemInputField('hours', workItem.hours, 'text', this.selector);
    this.text = new WorkItemTextareaField('text', workItem.text, this.selector);
    this.button = new ButtonField(new DeleteFormButton(this.selector));

    this.formset = formset;

    this.workItem = workItem;

    var fields = {
        job: this.job,
        hours: this.hours,
        text: this.text,
        button: this.button
    };

    this.context = {
        id: this.selector.substring(1, this.selector.length),
        job: {
            class: 'col-md-2',
            value: this.job.toHtml()
        },
        hours: {
            class: 'col-md-2',
            value: this.hours.toHtml()
        },
        text: {
            class: 'col-md-4',
            value: this.text.toHtml()
        },
        button: {
            value: this.button.toHtml()
        }
    }

    Form.call(this, {"fields": fields, "selector": this.selector});

    this.populateJobs = function() {

        for (var i in jobList) {
            this.job.addOption(jobList[i].id, jobList[i].name);
            $(this.selector + ' .job').append(this.job.options[i].toHtml());
        }

        if (this.job.value) {
            $(this.selector + ' .job').val(this.job.value);
        }
    }

    this.buildWorkItem = function() {
        this.workItem.user = worklog.userid;
        if (!this.workItem.date)
            this.workItem.date = worklog.date;
        this.workItem.job.id = $(this.selector + ' .job').val();
        this.workItem.hours = $(this.selector + ' .hours').val();
        this.workItem.text = $(this.selector + ' .text').val();
    }

    this.post = function() {

        var selector = this.selector;
        var form = this;

        this.buildWorkItem();

        $.ajax({
            type: 'POST',
            url: '/worklog/api/workitems/',
            cache: false,
            data: this.workItem.flatten(),
            success: function(data) {

                formTable.removeForm(selector, 'slow', $(window).width() < 600);
                displayTable.addWorkItem(new WorkItem($.parseJSON(data)));
            },
            error: function (data){
                var response = $.parseJSON(data.responseText);
                for (var key in response) {
                    form.appendErrorMessageToField(response[key], key);
                    $(selector).addClass('danger');
                    $(selector).on('click', function() {
                        $(this).removeClass('danger');
                    });
                }
            },
            dataType: 'text'
        });
    }

    this.put = function(errorCallback) {

        var selector = this.selector;
        var form = this;

        this.buildWorkItem();

        if (!errorCallback) {
            var errorCallback = function(data, status) {
                var response = $.parseJSON(data.responseText);
                var row = displayTable.rowsBySelector[selector];

                if (!row) {
                    row = workItemFormSet.getForm(selector);
                }


                for (var key in response) {
                    row.appendErrorMessageToField(response[key], key);
                    $(selector).addClass('danger', function() {
                        $(selector).addClass('workitem-fade', function() {
                            $(selector).removeClass('danger', function() {
                                window.setTimeout(function() {
                                    $(selector).removeClass('workitem-fade');
                                }, 2000);
                            });
                        });
                    });
                }
            }
        }

        $.ajax({
            type: 'PUT',
            url: '/worklog/api/workitems/' + workItem.id + '/',
            cache: false,
            data: this.workItem.flatten(),
            success: function(data, status) {

                if ($(this.selector).hasClass('danger')) {
                    $(this.selector).removeClass('danger');
                }

                displayTable.restoreRow(new WorkItem($.parseJSON(data)));

                if ($(window).width() < 600) {
                    $('.bs-edit-modal-sm .modal-body').children().remove();
                    $('.bs-edit-modal-sm').modal('toggle');
                }

                $(selector).addClass('success', function() {
                    $(selector).addClass('workitem-fade', function() {
                        $(selector).removeClass('success', function() {
                            window.setTimeout(function () {
                                $(selector).removeClass('workitem-fade');
                            }, 2000);
                        });
                    });
                });
            },
            error: function(data) {
                var response = $.parseJSON(data.responseText);
                var row = displayTable.rowsBySelector[selector];

                if (!row) {
                    row = workItemFormSet.getForm(selector);
                }

                for (var key in response) {
                    row.appendErrorMessageToField(response[key], key);
                    $(selector).addClass('danger', function() {
                        $(selector).addClass('workitem-fade', function() {
                            $(selector).removeClass('danger', function() {
                                window.setTimeout(function() {
                                    $(selector).removeClass('workitem-fade');
                                }, 2000);
                            });
                        });
                    });
                }
            },
            dataType: 'text'
        });
    }

    this.delete = function() {

    }

    this.appendErrorMessageToField = function(message, field) {
        var erroneousField = this.selector + ' .' + field;
        $(this.selector).addClass('has-error');


        if ($(erroneousField).siblings().length !== 0) {
            $(erroneousField).siblings('label').text(message);
        } else {
            $(erroneousField).after('<label class="control-label" for="' + erroneousField + '" id="label-' + this.selector[13] + '">' + message + '</label>');
        }
    }
}

WorkItemForm.prototype = new Form();
WorkItemForm.prototype.constructor = WorkItemForm;
