from django import forms
from django.db.models import DateField
from django.contrib.humanize.templatetags.humanize import intcomma
from django.utils.translation import ugettext as _

from accounting import models


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
