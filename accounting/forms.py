from django.forms import ModelForm, EmailField, TextInput, Select, BooleanField
from django.contrib.auth.models import User
from models import *


class BusinessUnitCreateForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(BusinessUnitCreateForm, self).__init__(*args, **kwargs)

    class Meta:
        model = BusinessUnit
        fields = '__all__'
        exclude = [
        	'user'
        ]


class BusinessUnitUpdateForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(BusinessUnitUpdateForm, self).__init__(*args, **kwargs)

    class Meta:
        model = BusinessUnit
        fields = '__all__'
        exclude = [
        	'user'
        ]


class FiscalYearCreateForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(FiscalYearCreateForm, self).__init__(*args, **kwargs)

    class Meta:
        model = FiscalYear
        fields = '__all__'
        exclude = [
            'business_unit'
        ]


class FiscalYearUpdateForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(FiscalYearUpdateForm, self).__init__(*args, **kwargs)

    class Meta:
        model = FiscalYear
        fields = '__all__'
        exclude = [
            'business_unit'
        ]

class ContractCreateForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(ContractCreateForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Contract
        fields = '__all__'
        exclude = [
            'business_unit'
        ]


class ContractUpdateForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(ContractUpdateForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Contract
        fields = '__all__'
        exclude = [
            
        ]


class ExpenseCreateForm(ModelForm):

    reocurring = BooleanField(label='Reocurring', initial=False, required=False)

    def __init__(self, *args, **kwargs):
        super(ExpenseCreateForm, self).__init__(*args, **kwargs)

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


class ExpenseUpdateForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(ExpenseUpdateForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Expense
        fields = '__all__'
        exclude = [
            'business_unit',
            'month'
        ]

class InvoiceCreateForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(InvoiceCreateForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Invoice
        fields = '__all__'
        exclude = [
            'actual_amount',
            'reconciled',
            'month',
            'contract'
        ]


class InvoiceUpdateForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(InvoiceUpdateForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Invoice
        fields = '__all__'
        exclude = [
            'contract'
        ]


class SalaryCreateForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(SalaryCreateForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Salary
        fields = '__all__'
        exclude = [
            'business_unit'
        ]


class SalaryUpdateForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(SalaryUpdateForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Salary
        fields = '__all__'
        exclude = [
            
        ]


class PartTimeCreateForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(PartTimeCreateForm, self).__init__(*args, **kwargs)

    class Meta:
        model = PartTime
        fields = '__all__'
        exclude = [
            'business_unit',
            'hours_work'
        ]


class PartTimeUpdateForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(PartTimeUpdateForm, self).__init__(*args, **kwargs)

    class Meta:
        model = PartTime
        fields = '__all__'
        exclude = [
        ]