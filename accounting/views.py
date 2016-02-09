from django.shortcuts import render
from django.views.generic import TemplateView
from django.core.urlresolvers import reverse_lazy

# Create your views here.
class TestView(TemplateView):
    template_name = 'accounting/home.html'
    success_url = reverse_lazy('accounting-home')

    def get_context_data(self, **kwargs):
        context = super(TestView, self).get_context_data()
        return context