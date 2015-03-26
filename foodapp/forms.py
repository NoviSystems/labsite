from django import forms
from foodapp import models
import datetime


class OrderForm(forms.ModelForm):

    class Meta:
        model = models.Order
        exclude = ['date']
        widgets = {
            'user': forms.HiddenInput(),
        }

    def clean_item(self):
        item = self.cleaned_data['item']
        user = self.cleaned_data['user']

        if item.once_a_day and models.Order.objects.filter(
            user=user,
            date=datetime.date.today,
            item=item
        ).exists():
            raise forms.ValidationError('This item has already been ordered.')

        return item


class PaidForm(forms.ModelForm):

    class Meta:
        model = models.AmountPaid
        exclude = ["user", "date"]
