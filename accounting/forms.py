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