from django.shortcuts import render
from django.views.generic import TemplateView
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from models import *
from django.contrib.auth.models import User


# Create your views here.
class TestView(LoginRequiredMixin, TemplateView):
    template_name = 'accounting/home.html'
    success_url = reverse_lazy('accounting-home')

    def get_context_data(self, **kwargs):
        context = super(TestView, self).get_context_data()
        business_units = BusinessUnit.objects.filter(user=self.request.user)
        context['business_units'] = business_units
        return context
