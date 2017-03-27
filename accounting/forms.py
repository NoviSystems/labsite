from collections import OrderedDict
from itertools import chain
from datetime import date

from django import forms
from django.db.models import DateField
from django.contrib.humanize.templatetags.humanize import intcomma
from django.utils.translation import ugettext as _
from django.utils.formats import number_format

from accounting import models
from accounting.utils import Month


class BaseForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(BaseForm, self).__init__(*args, **kwargs)

        model = self._meta.model
        for field in self.fields:
            model_field = model._meta.get_field(field)

            self.fields[field].widget.attrs.update({
                'class': 'form-control',
            })

            if isinstance(model_field, DateField):
                self.fields[field].widget.attrs.update({
                    'class': 'form-control datepicker',
                })


class BusinessUnitForm(BaseForm):
    class Meta:
        model = models.BusinessUnit
        fields = ['name', 'account_number']


class ContractForm(BaseForm):
    class Meta:
        model = models.Contract
        fields = [
            'contract_id',
            'name',
            'start_date',
            'amount',
            'type',
        ]


class InvoiceForm(BaseForm):

    def __init__(self, *args, contract, **kwargs):
        super().__init__(*args, **kwargs)
        self.contract = contract
        self.instance.contract = contract
        self.instance.business_unit = contract.business_unit

    def clean_invoice_date(self):
        date = self.cleaned_data['invoice_date']

        if date < self.contract.start_date:
            raise forms.ValidationError(
                _("Invoice must occur after or on the contract's start date (%(start_date)s)."),
                params={'start_date': str(self.contract.start_date)},
            )

        duplicate = self.contract.invoice_set.filter(invoice_date=date)
        if hasattr(self.instance, 'pk'):
            duplicate = duplicate.exclude(pk=self.instance.pk)

        if duplicate.exists():
            raise forms.ValidationError(_("Invoice already exists for this date."))

        return date

    def clean_predicted_date(self):
        date = self.cleaned_data['predicted_date']

        if date < self.contract.start_date:
            raise forms.ValidationError(
                _("Predicted payment date must occur after or on the contract's start date (%(start_date)s)."),
                params={'start_date': str(self.contract.start_date)},
            )

    def clean_predicted_amount(self):
        value = self.cleaned_data['predicted_amount']
        models.validate_positive(value)

        return value

    def clean_actual_amount(self):
        value = self.cleaned_data['actual_amount']
        models.validate_positive(value)

        return value

    class Meta:
        model = models.Invoice
        fields = [
            'invoice_date',
            'predicted_date',
            'predicted_amount',
        ]


class InvoiceCreateForm(InvoiceForm):

    def save(self, *args, **kwargs):
        self.instance.invoice_id = None
        super().save(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()

        if self.contract.state != self.contract.STATES.NEW:
            raise forms.ValidationError(
                _("Cannot create an invoice for an active or completed contract.")
            )

        return cleaned_data


class NewInvoiceUpdateForm(InvoiceForm):
    """
    Use for invoices w/ new contracts.
    """


class ActiveInvoiceUpdateForm(InvoiceForm):
    """
    Use for invoices w/ active contracts.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        predicted = self.instance.predicted_amount
        predicted = "$%s" % intcomma(predicted)
        self.fields['actual_amount'].help_text = (
            "Predicted amount: %s" % predicted
        )

    class Meta:
        model = models.Invoice
        fields = [
            'state',
            'actual_amount',
        ]


class MonthlyReconcileForm(forms.ModelForm):
    models = [
        models.Expenses,
        models.FullTimePayroll,
        models.PartTimePayroll,
        models.CashBalance,
    ]

    def __init__(self, dirty, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dirty = dirty

    def clean(self):
        cleaned_data = super().clean()
        month = Month(cleaned_data['year'], cleaned_data['month'])

        # The month can only be reconciled if it's passed.
        # So, validate that next month is not in the future.
        if Month.next(month).as_date() > date.today():
            msg = _("Month cannot be reconciled until it has passed.")
            raise forms.ValidationError(msg, code='inactive')

        if self.dirty:
            msg = _("Changes need to be saved before the month can be reconciled.")
            raise forms.ValidationError(msg, code='dirty')

        for model in self.models:
            try:
                instance = model.objects.get(year=month.year, month=month.month)
            except model.DoesNotExist:
                instance = None

            if instance is None or \
               instance.predicted_amount is None or \
               instance.actual_amount is None:
                msg = _("All values for this month need to be submitted "
                        "before the month can be reconciled.")
                raise forms.ValidationError(msg, code='incomplete')

        return cleaned_data

    class Meta:
        model = models.MonthlyReconcile
        fields = ['month', 'year', 'business_unit']


class BalanceInput(forms.TextInput):
    # Base off of text widget, since we plan to use commas

    def __init__(self, attrs=None):
        super().__init__(attrs)
        self.attrs['is'] = 'balance-input'
        self.attrs['placeholder'] = '\u2013.\u2013\u2013'

    class Media:
        js = ('js/balance-input.js', )
        css = {
            'all': ('css/balance-input.css', )
        }


class BalanceField(forms.DecimalField):
    widget = BalanceInput

    def to_python(self, value):
        return super().to_python(value.replace(',', ''))

    def widget_attrs(self, widget):
        # TODO: Is there a better way to provide the initial to the input as an attr?
        # Note: This is not ideal - form's initial data could override this. However,
        #       we don't set initial data on the form so this is... acceptable.
        attrs = super().widget_attrs(widget)
        attrs['initial'] = '' if self.initial is None else self.initial
        return attrs


class MonthlyBalanceForm(forms.Form):
    headers = [
        'Misc. Expenses',
        'Full-time Payroll',
        'Part-time Payroll',
        'Cash Balance',
    ]
    models = OrderedDict((
        ('exp', models.Expenses),
        ('ftp', models.FullTimePayroll),
        ('ptp', models.PartTimePayroll),
        ('bal', models.CashBalance),
    ))

    def __init__(self, *args, business_unit, billing_month, fiscal_months, **kwargs):
        super().__init__(*args, **kwargs)

        self.business_unit = business_unit
        self.billing_month = billing_month
        self.fiscal_months = fiscal_months

        # build month fields & data, make accessible through `month_data` attribute
        self.month_data = []
        for month in self.fiscal_months:
            data = self.build_month_data(month)

            # don't add formatted values to form fields list
            for name, value in data.items():
                if isinstance(value, forms.Field):
                    self.fields[name] = value

            # fields => bound fields
            bound = [
                self[name] if isinstance(value, forms.Field) else value
                for name, value in data.items()
            ]

            # add fields & formatted values to month data
            self.month_data.append({
                'month': month, 'fields': bound,
            })

    @staticmethod
    def format_currency(value):
        if value is None:
            return ''
        return '$' + number_format(value, decimal_pos=0, force_grouping=True)

    def build_field(self, model, attr, value, month):
        # TODO: use model's field.formfield() to build our custom decimal field instead?
        is_past = (month < self.billing_month)
        is_future = (month > self.billing_month)

        if model is models.CashBalance and attr == 'predicted':
            return '---------'

        if (is_future and attr == 'actual') or is_past:
            return self.format_currency(value)

        return BalanceField(
            initial=value,
            required=False,
            max_digits=10,
            decimal_places=2,
        )

    def field_name(self, month, model_id, attr):
        name_fmt = '%s_%s_%s'
        month_id = '%d_%02d' % (month.year, month.month)

        return name_fmt % (month_id, model_id, attr)

    def build_month_data(self, month):
        """
        The design here could be better, but is what enables a simpler template layout.

        - if the month is past, the returned fields are actually formatted text values.
        - if the month is the current billing month, the fields are actual form fields.
        - if the month is in the future, only the predicted fields are provided.
        """
        fields = OrderedDict()
        for key, model in self.models.items():
            try:
                instance = model.objects.get(month=month.month, year=month.year)
                actual, predicted = instance.actual_amount, instance.predicted_amount
            except model.DoesNotExist:
                actual, predicted = None, None

            # round off past the decimal (cents not currently supported by interface)
            if predicted is not None:
                predicted = predicted.quantize(1)
            if actual is not None:
                actual = actual.quantize(1)

            # build fields or get formatted values
            fields[self.field_name(month, key, 'predicted')] = self.build_field(model, 'predicted', predicted, month)
            fields[self.field_name(month, key, 'actual')] = self.build_field(model, 'actual', actual, month)

        return fields

    def save_month_data(self, month, data):
        saved = []

        for key, model in self.models.items():
            predicted = data.pop(self.field_name(month, key, 'predicted'), None)
            actual = data.pop(self.field_name(month, key, 'actual'), None)

            update = {}
            if predicted is not None:
                update['predicted_amount'] = predicted
            if actual is not None:
                update['actual_amount'] = actual

            # noop if no updated values
            if not update:
                continue

            instance, created = model.objects.get_or_create(
                month=month.month, year=month.year,
                business_unit=self.business_unit,
                defaults=update)

            # instance exists, update fields manually
            if not created:
                for k, v in update.items():
                    setattr(instance, k, v)
                instance.save(update_fields=update.keys())

            saved.append(instance)

        return saved

    def save(self):
        # Only save fields that have changed
        cleaned_data = {key: self.cleaned_data[key] for key in self.changed_data}
        saved = [
            self.save_month_data(month, cleaned_data)
            for month in self.fiscal_months
        ]

        # Something went wrong if 'cleaned_data' is not empty
        assert not cleaned_data

        # 'saved' is a list of lists - this flattens the results
        return list(chain.from_iterable(saved))


class UserTeamRoleCreateForm(BaseForm):
    class Meta:
        model = models.UserTeamRole
        fields = '__all__'
        exclude = [
            'business_unit',
        ]


class UserTeamRoleUpdateForm(BaseForm):
    class Meta:
        model = models.UserTeamRole
        fields = '__all__'
        exclude = [
            'user',
            'business_unit',
        ]
