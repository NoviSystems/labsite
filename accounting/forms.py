from django.forms import ModelForm, EmailField, TextInput, Select
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

    def __init__(self, *args, **kwargs):
        super(ExpenseCreateForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Expense
        fields = '__all__'
        exclude = [
            
        ]


class ExpenseUpdateForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(ExpenseUpdateForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Expense
        fields = '__all__'
        exclude = [
            
        ]