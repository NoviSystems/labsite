from django.forms import ModelForm, BooleanField
from django.core.exceptions import FieldDoesNotExist
from models import *


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


class BusinessUnitCreateForm(BaseForm, ModelForm):

    def __init__(self, *args, **kwargs):
        super(BusinessUnitCreateForm, self).__init__(*args, **kwargs)

    class Meta:
        model = BusinessUnit
        fields = '__all__'
        exclude = [
            'user'
        ]


class BusinessUnitUpdateForm(BaseForm, ModelForm):

    def __init__(self, *args, **kwargs):
        super(BusinessUnitUpdateForm, self).__init__(*args, **kwargs)

    class Meta:
        model = BusinessUnit
        fields = '__all__'
        exclude = [
            'user'
        ]


class FiscalYearCreateForm(BaseForm, ModelForm):

    def __init__(self, *args, **kwargs):
        super(FiscalYearCreateForm, self).__init__(*args, **kwargs)

    class Meta:
        model = FiscalYear
        fields = '__all__'
        exclude = [
            'business_unit',
        ]
        help_texts = {
            'cash_amount': 'Current cash amount for Business Unit.',
        }


class FiscalYearUpdateForm(BaseForm, ModelForm):

    def __init__(self, *args, **kwargs):
        super(FiscalYearUpdateForm, self).__init__(*args, **kwargs)

    class Meta:
        model = FiscalYear
        fields = '__all__'
        exclude = [
            'business_unit'
        ]


class ContractCreateForm(BaseForm, ModelForm):

    def __init__(self, *args, **kwargs):
        super(ContractCreateForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Contract
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
        model = Contract
        fields = '__all__'
        exclude = [
            'business_unit'
        ]


class ExpenseCreateForm(BaseForm, ModelForm):

    reocurring = BooleanField(label='Reocurring', initial=False, required=False)

    def __init__(self, *args, **kwargs):
        super(ExpenseCreateForm, self).__init__(*args, **kwargs)
        self.fields['date_paid'].required = False

    class Meta:
        model = Expense
        fields = '__all__'
        exclude = [
            'actual_amount',
            'reconciled',
            'month',
            'date_payed',
            'business_unit',
        ]
        help_texts = {
            'date_payable': 'If this is today or a previous date, it will be entered as already payed',
        }


class ExpenseUpdateForm(BaseForm, ModelForm):

    def __init__(self, *args, **kwargs):
        super(ExpenseUpdateForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Expense
        fields = '__all__'
        exclude = [
            'business_unit',
            'month'
        ]


class InvoiceCreateForm(BaseForm, ModelForm):

    def __init__(self, *args, **kwargs):
        super(InvoiceCreateForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Invoice
        fields = [
            'predicted_amount',
            'date_payable'
        ]


class InvoiceUpdateForm(BaseForm, ModelForm):

    def __init__(self, *args, **kwargs):
        super(InvoiceUpdateForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Invoice
        fields = '__all__'
        exclude = [
            'number',
            'contract'
        ]


class SalaryCreateForm(BaseForm, ModelForm):

    def __init__(self, *args, **kwargs):
        super(SalaryCreateForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Salary
        fields = '__all__'
        exclude = [
            'business_unit'
        ]


class SalaryUpdateForm(BaseForm, ModelForm):

    def __init__(self, *args, **kwargs):
        super(SalaryUpdateForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Salary
        fields = '__all__'
        exclude = [
            'business_unit'
        ]


class PartTimeCreateForm(BaseForm, ModelForm):

    def __init__(self, *args, **kwargs):
        super(PartTimeCreateForm, self).__init__(*args, **kwargs)

    class Meta:
        model = PartTime
        fields = '__all__'
        exclude = [
            'business_unit',
            'hours_work'
        ]


class PartTimeUpdateForm(BaseForm, ModelForm):

    def __init__(self, *args, **kwargs):
        super(PartTimeUpdateForm, self).__init__(*args, **kwargs)

    class Meta:
        model = PartTime
        fields = '__all__'
        exclude = [
            'business_unit',
            'hours_work'
        ]


class IncomeCreateForm(BaseForm, ModelForm):

    reocurring = BooleanField(label='Reocurring', initial=False, required=False)

    def __init__(self, *args, **kwargs):
        super(IncomeCreateForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Income
        fields = '__all__'
        exclude = [
            'actual_amount',
            'reconciled',
            'month',
            'date_payed',
            'business_unit',

        ]


class IncomeUpdateForm(BaseForm, ModelForm):

    def __init__(self, *args, **kwargs):
        super(IncomeUpdateForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Income
        fields = '__all__'
        exclude = [

        ]


class CashUpdateForm(BaseForm, ModelForm):

    def __init__(self, *args, **kwargs):
        super(CashUpdateForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Cash
        fields = '__all__'
        exclude = [
            'name',
            'business_unit',
            'month',
            'predicted_amount',
        ]


class UserTeamRoleCreateForm(BaseForm, ModelForm):

    def __init__(self, *args, **kwargs):
        super(UserTeamRoleCreateForm, self).__init__(*args, **kwargs)

    class Meta:
        model = UserTeamRole
        fields = '__all__'
        exclude = [
            'business_unit',
        ]


class UserTeamRoleUpdateForm(BaseForm, ModelForm):

    def __init__(self, *args, **kwargs):
        super(UserTeamRoleUpdateForm, self).__init__(*args, **kwargs)

    class Meta:
        model = UserTeamRole
        fields = '__all__'
        exclude = [
            'user',
            'business_unit',
        ]
