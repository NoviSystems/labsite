from django.shortcuts import render
from django.views.generic import TemplateView, FormView, CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from models import *
from django.contrib.auth.models import User
from forms import *


class HomePageView(LoginRequiredMixin, TemplateView):
    template_name = 'accounting/home.html'

    def get_context_data(self, **kwargs):
        context = super(HomePageView, self).get_context_data()
        business_units = BusinessUnit.objects.filter(user=self.request.user)
        context['business_units'] = business_units
        return context


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'accounting/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super(DashboardView, self).get_context_data()
        business_units = BusinessUnit.objects.filter(user=self.request.user)
        context['business_units'] = business_units
        current = BusinessUnit.objects.get(pk=kwargs['pk'])
        context['current'] = current
        fiscal_years = FiscalYear.objects.filter(business_unit=current)
        context['fiscal_years'] = fiscal_years
        return context


class BusinessUnitCreateView(LoginRequiredMixin, CreateView):
    template_name = 'accounting/businessunit_create_form.html'
    form_class = BusinessUnitCreateForm
    model = BusinessUnit

    def get_success_url(self):
	   return reverse_lazy('accounting:home')

    def form_valid(self, form):
	response = super(BusinessUnitCreateView, self).form_valid(form)
	form.instance.user.add(self.request.user)
	return response


class BusinessUnitDeleteView(LoginRequiredMixin, DeleteView):
    model = BusinessUnit
    template_name_suffix = '_delete_form'

    def get_object(self):
        return BusinessUnit.objects.get(pk=self.kwargs['business_unit'])

    def get_success_url(self):
        return reverse_lazy('accounting:home')


class BusinessUnitUpdateView(LoginRequiredMixin, UpdateView):
    template_name_suffix = '_update_form'
    form_class = BusinessUnitUpdateForm
    model = BusinessUnit

    def get_object(self):
        return BusinessUnit.objects.get(pk=self.kwargs['business_unit'])

    def get_success_url(self):
        return reverse_lazy('accounting:home')

    def form_valid(self, form):
        response = super(BusinessUnitUpdateView, self).form_valid(form)
        return response


class FiscalYearCreateView(LoginRequiredMixin, CreateView):
    template_name = 'accounting/fiscalyear_create_form.html'
    model = FiscalYear
    form_class = FiscalYearCreateForm

    def get_context_data(self, *args, **kwargs):
        context = super(FiscalYearCreateView, self).get_context_data()
        context['business_unit'] = BusinessUnit.objects.get(pk=self.kwargs['pk'])
        return context

    def get_success_url(self):
        return reverse_lazy('accounting:dashboard', kwargs=self.kwargs)

    def form_valid(self, form):
        form.instance.business_unit = BusinessUnit.objects.get(pk=self.kwargs['pk'])
        response = super(FiscalYearCreateView, self).form_valid(form)
        return response


class FiscalYearDeleteView(LoginRequiredMixin, DeleteView):
    model = FiscalYear
    template_name_suffix = '_delete_form'

    def get_object(self):
        return FiscalYear.objects.get(pk=self.kwargs['fiscal_year'])

    def get_success_url(self):
        return reverse_lazy('accounting:dashboard', kwargs=self.kwargs)


class FiscalYearUpdateView(LoginRequiredMixin, UpdateView):
    template_name_suffix = '_update_form'
    form_class = FiscalYearUpdateForm
    model = FiscalYear

    def get_object(self):
        return FiscalYear.objects.get(pk=self.kwargs['fiscal_year'])

    def get_success_url(self):
        return reverse_lazy('accounting:dashboard', kwargs=self.kwargs)

    def form_valid(self, form):
        response = super(FiscalYearUpdateView, self).form_valid(form)
        return response