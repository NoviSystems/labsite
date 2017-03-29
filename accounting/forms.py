from collections import OrderedDict
from itertools import chain
from datetime import date

from django import forms
from django.db.models import DateField
from django.utils.formats import date_format
from django.utils.translation import ugettext as _

from accounting import models
from accounting.utils import Month, format_currency


empty = object()


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

    def clean_expected_invoice_date(self):
        date = self.cleaned_data['expected_invoice_date']

        if date < self.contract.start_date:
            raise forms.ValidationError(
                _("Invoice must occur after or on the contract's start date (%(start_date)s)."),
                params={'start_date': str(self.contract.start_date)},
            )

        duplicate = self.contract.invoice_set.filter(expected_invoice_date=date)
        if hasattr(self.instance, 'pk'):
            duplicate = duplicate.exclude(pk=self.instance.pk)

        if duplicate.exists():
            raise forms.ValidationError(_("Invoice already exists for this date."))

        return date

    def clean_expected_payment_date(self):
        date = self.cleaned_data['expected_payment_date']

        if date < self.contract.start_date:
            raise forms.ValidationError(
                _("Expected payment date must occur after or on the contract's start date (%(start_date)s)."),
                params={'start_date': str(self.contract.start_date)},
            )

        return date

    def clean_expected_amount(self):
        value = self.cleaned_data['expected_amount']
        models.validate_positive(value)

        return value

    def clean_actual_amount(self):
        value = self.cleaned_data['actual_amount']
        models.validate_positive(value)

        return value

    class Meta:
        model = models.Invoice
        fields = [
            'expected_invoice_date',
            'expected_payment_date',
            'expected_amount',
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

        # expected invoice date
        expected = self.instance.expected_invoice_date
        self.fields['actual_invoice_date'].help_text = (
            "Expected date: %s" % date_format(expected)
        )

        # expected payment date
        expected = self.instance.expected_payment_date
        self.fields['actual_payment_date'].help_text = (
            "Expected date: %s" % date_format(expected)
        )

        # expected amount
        expected = self.instance.expected_amount
        self.fields['actual_amount'].help_text = (
            "Expected amount: %s" % format_currency(expected, html=False)
        )

    class Meta:
        model = models.Invoice
        fields = [
            'state',
            'actual_invoice_date',
            'actual_payment_date',
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
               instance.expected_amount is None or \
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
        js = ('js/accounting/balance-input.js', )
        css = {
            'all': ('css/accounting/balance-input.css', )
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

    def build_field(self, model, attr, value, month):
        # TODO: use model's field.formfield() to build our custom decimal field instead?
        is_past = (month < self.billing_month)
        is_future = (month > self.billing_month)

        if model is models.CashBalance and attr == 'expected':
            return format_currency(value) or '---------'

        if (is_future and attr == 'actual') or is_past:
            return format_currency(value)

        if self.billing_month >= Month(date.today()) and attr == 'actual':
            # You should only be able to input actuals once the billing month has passed.
            # eg, you would enter March's actuals in April.
            return ''

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
        - if the month is in the future, only the expected fields are provided.
        """
        fields = OrderedDict()
        for key, model in self.models.items():
            try:
                instance = model.objects.get(month=month.month, year=month.year)
                actual, expected = instance.actual_amount, instance.expected_amount
            except model.DoesNotExist:
                actual, expected = None, None

            # build fields or get formatted values
            fields[self.field_name(month, key, 'expected')] = self.build_field(model, 'expected', expected, month)
            fields[self.field_name(month, key, 'actual')] = self.build_field(model, 'actual', actual, month)

        return fields

    def save_month_data(self, month, data):
        saved = []

        for key, model in self.models.items():
            expected = data.pop(self.field_name(month, key, 'expected'), empty)
            actual = data.pop(self.field_name(month, key, 'actual'), empty)

            update = {}
            if expected is not empty:
                update['expected_amount'] = expected
            if actual is not empty:
                update['actual_amount'] = actual

            # noop if no updated values
            if not update:
                continue

            # handle expected_amount clearing
            # since the field has a not-null constraint, it's necessary to delete the instance
            # if the actual_amount has not been set, then this is safe to do
            # if the actual is set, then we either have to noop and keep both or delete and remove both
            if expected is None:
                instance = model.objects.get(
                    month=month.month, year=month.year,
                    business_unit=self.business_unit)

                # we can safely delete if actual is not set
                if instance.actual_amount is None:
                    instance.delete()
                    saved.append(instance)

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
