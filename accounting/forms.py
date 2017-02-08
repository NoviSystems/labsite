from django.db.models import DateField
from django import forms

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
    class Meta:
        model = models.Invoice
        fields = [
            'invoice_id',
            'name',
            'month',
            'year',
            'predicted_amount',
            'actual_amount',
            'state',
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
