import datetime

from django import forms

from foodapp import models


class OrderBaseForm(forms.ModelForm):

    class Meta:
        model = models.Order
        fields = ('item', 'quantity')


class OrderForm(OrderBaseForm):

    def __init__(self, user, *args, **kwargs):
        super(OrderBaseForm, self).__init__(*args, **kwargs)
        self.user = user

    class Meta(OrderBaseForm.Meta):
        fields = OrderBaseForm.Meta.fields

    def clean_item(self):
        item = self.cleaned_data['item']

        if item.once_a_day and models.Order.objects.filter(
            user=self.user,
            date=datetime.date.today(),
            item=item
        ).exists():
            raise forms.ValidationError('This item has already been ordered.')

        return item


class PaidForm(forms.ModelForm):

    class Meta:
        model = models.AmountPaid
        fields = ('amount',)
