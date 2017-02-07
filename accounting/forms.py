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
            'state',
            'type',
        ]


class ExpenseCreateForm(BaseForm, ModelForm):
    recurring = BooleanField(label='recurring', initial=False, required=False)

    class Meta:
        model = models.Expense
        fields = '__all__'
        exclude = [
            'actual_amount',
            'reconciled',
            'month',
            'date_paid',
            'business_unit',
            'expense_type',
        ]
        help_texts = {
            'date_payable': 'If this is today or a previous date, it will be entered as already paid',
        }


class ExpenseUpdateForm(BaseForm, ModelForm):
    class Meta:
        model = models.Expense
        fields = '__all__'
        exclude = [
            'business_unit',
            'month',
            'reconciled',
            'expense_type',
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


class IncomeCreateForm(BaseForm, ModelForm):
    recurring = BooleanField(label='recurring', initial=False, required=False)

    class Meta:
        model = models.Income
        fields = '__all__'
        exclude = [
            'actual_amount',
            'reconciled',
            'month',
            'date_paid',
            'business_unit',
        ]


class IncomeUpdateForm(BaseForm, ModelForm):
    class Meta:
        model = models.Income
        fields = '__all__'
        exclude = [
            'reconciled',
        ]


class UserTeamRoleCreateForm(BaseForm, ModelForm):
    class Meta:
        model = models.UserTeamRole
        fields = '__all__'
        exclude = [
            'business_unit',
        ]


class UserTeamRoleUpdateForm(BaseForm, ModelForm):
    class Meta:
        model = models.UserTeamRole
        fields = '__all__'
        exclude = [
            'user',
            'business_unit',
        ]


class PayrollExpenseCreateForm(BaseForm, ModelForm):
    class Meta:
        model = models.Expense
        fields = '__all__'
        exclude = [
            'predicted_amount',
            'name',
            'reconciled',
            'month',
            'date_paid',
            'business_unit',
            'expense_type',
            'recurring',
        ]


class CashCreateForm(BaseForm, ModelForm):
    class Meta:
        model = models.Cash
        fields = [
            'actual_amount',
        ]


class CashUpdateForm(BaseForm, ModelForm):
    class Meta:
        model = models.Cash
        fields = [
            'actual_amount',
        ]
