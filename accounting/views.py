from django.shortcuts import render
from django.views.generic import TemplateView, FormView, CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from models import *
from django.contrib.auth.models import User
from forms import *
from decimal import *

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

        fiscal_year_data = []
        for fiscal_year in fiscal_years:
            months = Month.objects.filter(fiscal_year=fiscal_year)
            months_data = []
            for month in months:
                line_items = LineItem.objects.filter(month=month)
                predicted = Decimal('0.00')
                actual = Decimal('0.00')
                for line_item in line_items:
                    predicted += line_item.predicted_amount
                    actual += line_item.actual_amount
                months_data.extend(
                    [
                        {
                        'month': month,
                        'predicted': predicted,
                        'actual': actual,
                        'line_items': line_items,
                        }
                    ]
                )
            fiscal_year_data.extend(
                [
                    {
                    'fiscal_year': fiscal_year,
                    'months': months_data
                    }
                ]
                )

        context['fiscal_year_data'] = fiscal_year_data
        personnel = Personnel.objects.filter(business_unit=current)
        context['personnel'] = personnel
        contracts = Contract.objects.filter(business_unit=current)
        context['contracts'] = contracts

        return context


class ContractsView(LoginRequiredMixin, TemplateView):
    template_name = 'accounting/contracts.html'

    def get_context_data(self, **kwargs):
        context = super(ContractsView, self).get_context_data()
        business_units = BusinessUnit.objects.filter(user=self.request.user)
        context['business_units'] = business_units
        current = BusinessUnit.objects.get(pk=kwargs['pk'])
        context['current'] = current
        contracts = Contract.objects.filter(business_unit=current)
        context['contracts'] = contracts
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
        return reverse_lazy('accounting:dashboard', kwargs={'pk': self.kwargs["pk"]})


class FiscalYearUpdateView(LoginRequiredMixin, UpdateView):
    template_name_suffix = '_update_form'
    form_class = FiscalYearUpdateForm
    model = FiscalYear

    def get_object(self):
        return FiscalYear.objects.get(fiscal_year=self.kwargs['fiscal_year'])

    def get_success_url(self):
        return reverse_lazy('accounting:dashboard', kwargs=self.kwargs)

    def form_valid(self, form):
        response = super(FiscalYearUpdateView, self).form_valid(form)
        return response


class ContractCreateView(LoginRequiredMixin, CreateView):
    template_name = 'accounting/contract_create_form.html'
    model = Contract
    form_class = ContractCreateForm

    def get_context_data(self, *args, **kwargs):
        context = super(ContractCreateView, self).get_context_data()
        return context

    def get_success_url(self):
        return reverse_lazy('accounting:dashboard', kwargs=self.kwargs)

    def form_valid(self, form):
        response = super(ContractCreateView, self).form_valid(form)
        return response


class ContractDeleteView(LoginRequiredMixin, DeleteView):
    model = Contract
    template_name_suffix = '_delete_form'

    def get_object(self):
        return Contract.objects.get(pk=self.kwargs['contract'])

    def get_success_url(self):
        return reverse_lazy('accounting:dashboard', kwargs={'pk': self.kwargs["pk"]})


class ContractUpdateView(LoginRequiredMixin, UpdateView):
    template_name_suffix = '_update_form'
    form_class = ContractUpdateForm
    model = Contract

    def get_object(self):
        return Contract.objects.get(pk=self.kwargs['contract'])

    def get_success_url(self):
        return reverse_lazy('accounting:dashboard', kwargs=self.kwargs)

    def form_valid(self, form):
        response = super(ContractUpdateView, self).form_valid(form)
        return response


class ExpenseCreateView(LoginRequiredMixin, CreateView):
    template_name = 'accounting/expense_create_form.html'
    model = Expense
    form_class = ExpenseCreateForm

    def get_context_data(self, *args, **kwargs):
        context = super(ExpenseCreateView, self).get_context_data()
        return context

    def get_success_url(self):
        return reverse_lazy('accounting:dashboard', kwargs= { 'pk':self.kwargs['pk'] } )

    def form_valid(self, form):
        form.instance.month = Month.objects.get(pk=self.kwargs['month'])
        response = super(ExpenseCreateView, self).form_valid(form)

        return response


class ExpenseDeleteView(LoginRequiredMixin, DeleteView):
    model = Expense
    template_name_suffix = '_delete_form'

    def get_object(self):
        return Expense.objects.get(pk=self.kwargs['expense'])

    def get_success_url(self):
        return reverse_lazy('accounting:dashboard', kwargs={'pk': self.kwargs["pk"]})


class ExpenseUpdateView(LoginRequiredMixin, UpdateView):
    template_name_suffix = '_update_form'
    form_class = ExpenseUpdateForm
    model = Expense

    def get_object(self):
        return Expense.objects.get(pk=self.kwargs['expense'])

    def get_success_url(self):
        return reverse_lazy('accounting:dashboard', kwargs=self.kwargs)

    def form_valid(self, form):
        response = super(ExpenseUpdateView, self).form_valid(form)
        return response


class ExpensesView(LoginRequiredMixin, TemplateView):
    template_name = 'accounting/expenses.html'

    def get_context_data(self, **kwargs):
        context = super(ExpensesView, self).get_context_data()
        business_units = BusinessUnit.objects.filter(user=self.request.user)
        context['business_units'] = business_units
        current = BusinessUnit.objects.get(pk=kwargs['pk'])
        context['current'] = current

        expenses = Expense.objects.all()
        context['expenses'] = expenses

        return context