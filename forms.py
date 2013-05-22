from django import forms
from django.forms import ModelForm
from models import Order, AmountPaid

class OrderForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(OrderForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Order
        exclude = ["user", "date"]

class PaidForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(PaidForm, self).__init__(*args, **kwargs)
    class Meta:
        model = AmountPaid
	exclude = ["user", "date"]
