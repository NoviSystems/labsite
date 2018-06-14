
import datetime
import random

from django import forms
from django.forms import ModelForm
from django.forms.formsets import BaseFormSet


from worklog.models import WorkItem, Job


class WorkItemBaseFormSet(BaseFormSet):

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("logged_in_user")
        super(WorkItemBaseFormSet, self).__init__(*args, **kwargs)

    def _construct_form(self, *args, **kwargs):
        # inject user in each form on the formset
        kwargs['user'] = self.user
        return super(WorkItemBaseFormSet, self)._construct_form(*args, **kwargs)


class BadWorkItemForm(Exception):
    pass


class WorkItemForm(ModelForm):

    job = forms.ModelChoiceField(queryset=Job.objects.none(), empty_label="None")  # empty queryset, overridden in ctor

    job.widget.attrs['class'] = 'form-control'

    class Meta:
        model = WorkItem
        fields = ['job', 'hours', 'text']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user")
        super(WorkItemForm, self).__init__(*args, **kwargs)
        queryset = Job.objects.available_to(user) & Job.objects.open_on(datetime.date.today())
        queryset = queryset.order_by('name')
        self.fields["job"].queryset = queryset

        self.fields["hours"].widget.attrs['class'] = 'form-control'
        self.fields["text"].widget.attrs['class'] = 'form-control'

        self.fields["hours"].widget.attrs['placeholder'] = 'Hours Worked'
        self.fields["text"].widget.attrs['placeholder'] = 'Work Description'

        self.fields["text"].widget.attrs['rows'] = '6'

    def clean(self):  # noqa: C901
        cleaned_data = super(WorkItemForm, self).clean()
        try:
            hours = cleaned_data["hours"]
        except KeyError:
            hours = 0

        try:
            text = cleaned_data["text"]
        except KeyError:
            text = None

        try:
            job = cleaned_data["job"]
        except KeyError:
            job = None

        # Only allows non-zero, non-negative hours to be entered in half hour increments.
        if (hours % 1 != 0) and (hours % 1 % .25 != 0):
            message_list = ["Please, Hammer, don't hurt 'em! Use 15-minute increments.",
                            "All your mantissa are belong to us. 15-minute increments only. Please.",
                            "You thought we wouldn't notice that you didn't use 15-minute increments. You were wrong. Try again, jerk.",  # noqa: E501
                            "Hey buddy. How's it going? Listen, not a huge deal, but we've got this thing where we use 15-minute increments.",  # noqa: E501
                            "If you could go ahead and use 15-minute increments, that would be grrrreeaat."]
            error_message = message_list[random.randint(0, len(message_list) - 1)]
            self._errors["hours"] = self.error_class([error_message])
            if hours:
                del cleaned_data["hours"]
        elif hours < 0:
            error_message = ("We here at <Insert Company Name here> would like you to "
                             "have a non-negative work experience. Please enter a "
                             "non-negative number of hours.")
            self._errors["hours"] = self.error_class([error_message])
            if hours:
                del cleaned_data["hours"]
        elif not hours:
            error_message = ("If you work at <Insert Company Name here>, you're "
                             "more hero than zero. Enter an hero number of hours.")
            self._errors["hours"] = self.error_class([error_message])
            if hours:
                del cleaned_data["hours"]

        # Custom error messages for empty fields
        if text is None or text == "":
            error_message = "This is where you describe the work you did, as if you did any."
            self._errors["text"] = self.error_class([error_message])
            if text:
                del cleaned_data["text"]

        if job is None or job == "":
            error_message = ("i.e., the thing you're supposed to wear pants for, "
                             "but you probably don't, since you're a programmer.")
            self._errors["job"] = self.error_class([error_message])
            if job:
                del cleaned_data["job"]

        return cleaned_data
