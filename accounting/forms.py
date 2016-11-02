from django.forms import ModelForm, BooleanField, ValidationError
from django.core.exceptions import FieldDoesNotExist

from accounting import models


class BaseForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(BaseForm, self).__init__(*args, **kwargs)

        for field in self.fields:
            try:
                placeholder = self.instance._meta.get_field(field).verbose_name
            except FieldDoesNotExist:
                placeholder = ''

            self.fields[field].widget.attrs.update({
                'placeholder': placeholder,
                'class': 'form-control',
            })

            if 'date' in self.fields[field].label.lower():
                self.fields[field].widget.attrs.update({
                    'class': 'form-control datepicker',
                })


class BusinessUnitCreateForm(BaseForm, ModelForm):

    def __init__(self, *args, **kwargs):
        super(BusinessUnitCreateForm, self).__init__(*args, **kwargs)

    class Meta:
        model = models.BusinessUnit
        fields = '__all__'
        exclude = [
            'user'
        ]


class BusinessUnitUpdateForm(BaseForm, ModelForm):

    def __init__(self, *args, **kwargs):
        super(BusinessUnitUpdateForm, self).__init__(*args, **kwargs)

    class Meta:
        model = models.BusinessUnit
        fields = '__all__'
        exclude = [
            'user'
        ]


class ContractCreateForm(BaseForm, ModelForm):

    def __init__(self, *args, **kwargs):
        super(ContractCreateForm, self).__init__(*args, **kwargs)

    class Meta:
        model = models.Contract
        fields = '__all__'
        exclude = [
            'department',
            'contract_number',
            'business_unit'
        ]


class ContractUpdateForm(BaseForm, ModelForm):

    def __init__(self, *args, **kwargs):
        super(ContractUpdateForm, self).__init__(*args, **kwargs)

    class Meta:
        model = models.Contract
        fields = '__all__'
        exclude = [
            'business_unit'
        ]


class ExpenseCreateForm(BaseForm, ModelForm):

    recurring = BooleanField(label='recurring', initial=False, required=False)

    def __init__(self, *args, **kwargs):
        super(ExpenseCreateForm, self).__init__(*args, **kwargs)

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

    def __init__(self, *args, **kwargs):
        super(ExpenseUpdateForm, self).__init__(*args, **kwargs)

    class Meta:
        model = models.Expense
        fields = '__all__'
        exclude = [
            'business_unit',
            'month',
            'reconciled',
            'expense_type',
        ]


class InvoiceCreateForm(BaseForm, ModelForm):

    def __init__(self, *args, **kwargs):
        super(InvoiceCreateForm, self).__init__(*args, **kwargs)

    class Meta:
        model = models.Invoice
        fields = [
            'predicted_amount',
            'date_payable',
        ]


class InvoiceUpdateForm(BaseForm, ModelForm):

    def __init__(self, *args, **kwargs):
        super(InvoiceUpdateForm, self).__init__(*args, **kwargs)

    class Meta:
        model = models.Invoice
        fields = '__all__'
        exclude = [
            'business_unit',
            'name',
            'number',
            'contract',
            'reconciled',
        ]
        help_texts = {
            'transition_state': 'Invoices are marked reconciled when Actual Amount and Date Paid are filled and Tansition State is Recieved.'
        }


class FullTimeCreateForm(BaseForm, ModelForm):

    def __init__(self, *args, **kwargs):
        super(FullTimeCreateForm, self).__init__(*args, **kwargs)

    class Meta:
        model = models.FullTime
        fields = '__all__'
        exclude = [
            'business_unit'
        ]


class FullTimeUpdateForm(BaseForm, ModelForm):

    def __init__(self, *args, **kwargs):
        super(FullTimeUpdateForm, self).__init__(*args, **kwargs)

    class Meta:
        model = models.FullTime
        fields = '__all__'
        exclude = [
            'business_unit'
        ]


class PartTimeCreateForm(BaseForm, ModelForm):

    def __init__(self, *args, **kwargs):
        super(PartTimeCreateForm, self).__init__(*args, **kwargs)

    class Meta:
        model = models.PartTime
        fields = '__all__'
        exclude = [
            'business_unit',
            'hours_work'
        ]


class PartTimeUpdateForm(BaseForm, ModelForm):

    def __init__(self, *args, **kwargs):
        super(PartTimeUpdateForm, self).__init__(*args, **kwargs)

    class Meta:
        model = models.PartTime
        fields = '__all__'
        exclude = [
            'business_unit',
            'hours_work'
        ]


class IncomeCreateForm(BaseForm, ModelForm):

    recurring = BooleanField(label='recurring', initial=False, required=False)

    def __init__(self, *args, **kwargs):
        super(IncomeCreateForm, self).__init__(*args, **kwargs)

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

    def __init__(self, *args, **kwargs):
        super(IncomeUpdateForm, self).__init__(*args, **kwargs)

    class Meta:
        model = models.Income
        fields = '__all__'
        exclude = [
            'reconciled',
        ]


class UserTeamRoleCreateForm(BaseForm, ModelForm):

    def __init__(self, *args, **kwargs):
        super(UserTeamRoleCreateForm, self).__init__(*args, **kwargs)

    class Meta:
        model = models.UserTeamRole
        fields = '__all__'
        exclude = [
            'business_unit',
        ]


class UserTeamRoleUpdateForm(BaseForm, ModelForm):

    def __init__(self, *args, **kwargs):
        super(UserTeamRoleUpdateForm, self).__init__(*args, **kwargs)

    class Meta:
        model = models.UserTeamRole
        fields = '__all__'
        exclude = [
            'user',
            'business_unit',
        ]


class PayrollExpenseCreateForm(BaseForm, ModelForm):

    def __init__(self, *args, **kwargs):
        super(PayrollExpenseCreateForm, self).__init__(*args, **kwargs)

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
    def __init__(self, *args, **kwargs):
        super(CashCreateForm, self).__init__(*args, **kwargs)

    class Meta:
        model = models.Cash
        fields = [
            'actual_amount',
        ]


class CashUpdateForm(BaseForm, ModelForm):
    def __init__(self, *args, **kwargs):
        super(CashUpdateForm, self).__init__(*args, **kwargs)

    class Meta:
        model = models.Cash
        fields = [
            'actual_amount',
        ]
