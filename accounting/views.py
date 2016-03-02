from django.shortcuts import render
from django.views.generic import TemplateView, FormView, CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from models import *
from django.contrib.auth.models import User
from forms import *
from decimal import *
import datetime 
import json
from django.shortcuts import redirect

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

        now = datetime.datetime.now()
        current_month = None
        for fiscal_year in fiscal_years:
            months = Month.objects.filter(fiscal_year=fiscal_year)
            for month in months:
                if month.month.month == now.month:
                    current_month = month
        context['current_month'] = current_month

        months = []
        predicted_totals = []
        actual_totals = []
        for fiscal_year in fiscal_years:
            mnths = Month.objects.filter(fiscal_year=fiscal_year)
            for month in mnths:
                months.append(month.month.strftime("%B"))
                expenses = Expense.objects.filter(month=month)
                invoices = Invoice.objects.filter(month=month)
                predicted = Decimal('0.00')
                actual = Decimal('0.00')
                for expense in expenses:
                    if expense.reconciled:
                        actual -= expense.actual_amount
                    else:
                        predicted -= expense.predicted_amount
                for invoice in invoices:
                    if invoice.reconciled:
                        actual += invoice.actual_amount
                    else:
                        predicted += invoice.predicted_amount
                predicted_totals.append(float(predicted))
                actual_totals.append(float(actual))
        context['months'] = json.dumps(months)
        print "P: ", predicted_totals
        print "A: ", actual_totals
        context['predicted_totals'] = json.dumps(predicted_totals)
        context['actual_totals'] = json.dumps(actual_totals)

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

        fiscal_years = FiscalYear.objects.filter(business_unit=current)

        now = datetime.datetime.now()
        current_month = None
        for fiscal_year in fiscal_years:
            months = Month.objects.filter(fiscal_year=fiscal_year)
            for month in months:
                if month.month.month == now.month:
                    current_month = month
        context['current_month'] = current_month

        contracts = Contract.objects.filter(business_unit=current)
        contract_invoices = []
        for contract in contracts:
            invoices = Invoice.objects.filter(contract=contract)
            contract_invoices.extend(
            [
                {
                    'contract': contract,
                    'invoices': invoices,
                }
            ]
            )
        context['contract_invoices'] = contract_invoices
        return context


class ExpensesView(LoginRequiredMixin, TemplateView):
    template_name = 'accounting/expenses.html'

    def get_context_data(self, **kwargs):
        context = super(ExpensesView, self).get_context_data()
        business_units = BusinessUnit.objects.filter(user=self.request.user)
        context['business_units'] = business_units
        current = BusinessUnit.objects.get(pk=kwargs['pk'])
        context['current'] = current
        fiscal_years = FiscalYear.objects.filter(business_unit=current)
        now = datetime.datetime.now()

        months_data = []
        current_month = None
        for fiscal_year in fiscal_years:
            months = Month.objects.filter(fiscal_year=fiscal_year)
            for month in months:
                if month.month.month == now.month:
                    current_month = month

        month = Month.objects.get(pk=kwargs['month'])
        month_data = {
            'month': month,
            'expenses': Expense.objects.filter(month=month),
            'incomes':Income.objects.filter(month=month),
        }


        context['months'] = months
        context['current_month'] = current_month
        context['month_data'] = month_data

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
        return reverse_lazy('accounting:contracts', kwargs=self.kwargs)

    def form_valid(self, form):
        form.instance.business_unit = BusinessUnit.objects.get(pk=self.kwargs['pk'])
        response = super(ContractCreateView, self).form_valid(form)
        return response


class ContractDeleteView(LoginRequiredMixin, DeleteView):
    model = Contract
    template_name_suffix = '_delete_form'

    def get_object(self):
        return Contract.objects.get(pk=self.kwargs['contract'])

    def get_success_url(self):
        return reverse_lazy('accounting:contracts', kwargs={'pk': self.kwargs["pk"]})


class ContractUpdateView(LoginRequiredMixin, UpdateView):
    template_name_suffix = '_update_form'
    form_class = ContractUpdateForm
    model = Contract

    def get_object(self):
        return Contract.objects.get(pk=self.kwargs['contract'])

    def get_success_url(self):
        return reverse_lazy('accounting:contracts', kwargs={'pk': self.kwargs["pk"]})

    def form_valid(self, form):
        response = super(ContractUpdateView, self).form_valid(form)
        return response


class InvoiceCreateView(LoginRequiredMixin, CreateView):
    template_name = 'accounting/invoice_create_form.html'
    model = Invoice
    form_class = InvoiceCreateForm

    def get_context_data(self, *args, **kwargs):
        context = super(InvoiceCreateView, self).get_context_data()
        return context

    def get_success_url(self):
        return reverse_lazy('accounting:contracts', kwargs={ 'pk':self.kwargs['pk'] } )

    def form_valid(self, form):
        month = Month.objects.get(fiscal_year__business_unit=self.kwargs['pk'], month__month=form.instance.date.month)
        form.instance.month = month
        form.instance.contract = Contract.objects.get(pk=self.kwargs['contract'])
        response = super(InvoiceCreateView, self).form_valid(form)
        return response


class InvoiceDeleteView(LoginRequiredMixin, DeleteView):
    model = Invoice
    template_name_suffix = '_delete_form'

    def get_object(self):
        return Invoice.objects.get(pk=self.kwargs['invoice'])

    def get_success_url(self):
        return reverse_lazy('accounting:contracts', kwargs={'pk': self.kwargs["pk"]})


class InvoiceUpdateView(LoginRequiredMixin, UpdateView):
    template_name_suffix = '_update_form'
    form_class = InvoiceUpdateForm
    model = Invoice

    def get_object(self):
        return Invoice.objects.get(pk=self.kwargs['invoice'])

    def get_success_url(self):
        return reverse_lazy('accounting:contracts', kwargs= { 'pk':self.kwargs['pk'] } )

    def form_valid(self, form):
        response = super(InvoiceUpdateView, self).form_valid(form)
        return response


class ExpenseCreateView(LoginRequiredMixin, CreateView):
    template_name = 'accounting/expense_create_form.html'
    model = Expense
    form_class = ExpenseCreateForm

    def get_context_data(self, *args, **kwargs):
        context = super(ExpenseCreateView, self).get_context_data()
        return context

    def get_success_url(self):
        return reverse_lazy('accounting:expenses', kwargs= { 'pk':self.kwargs['pk'], 'month': self.kwargs['month']} )

    def form_valid(self, form):
        form.instance.business_unit = BusinessUnit.objects.get(pk=self.kwargs['pk'])
        month = Month.objects.get(pk=self.kwargs['month'])
        try:
            if self.request.POST['reocurring']:
                months = Month.objects.filter(fiscal_year=month.fiscal_year)
                for m in months:
                    if m.month >= month.month:
                        Expense.objects.create(
                            business_unit = form.instance.business_unit,
                            month = m,
                            predicted_amount = form.instance.predicted_amount,
                            name = form.instance.name,
                            data_payable = form.instance.data_payable,
                        )
            return redirect('accounting:expenses', pk=self.kwargs['pk'], month=self.kwargs['month'] )
        except KeyError:
            print "Exception thrown"
            form.instance.month = month
        response = super(ExpenseCreateView, self).form_valid(form)

        return response


class ExpenseDeleteView(LoginRequiredMixin, DeleteView):
    model = Expense
    template_name_suffix = '_delete_form'

    def get_object(self):
        return Expense.objects.get(pk=self.kwargs['expense'])

    def get_success_url(self):
        return reverse_lazy('accounting:expenses', kwargs={'pk': self.kwargs["pk"], 'month': self.kwargs['month']})


class ExpenseUpdateView(LoginRequiredMixin, UpdateView):
    template_name_suffix = '_update_form'
    form_class = ExpenseUpdateForm
    model = Expense

    def get_object(self):
        return Expense.objects.get(pk=self.kwargs['expense'])

    def get_success_url(self):
        return reverse_lazy('accounting:expenses', kwargs= {'pk':self.kwargs['pk'], 'month': self.kwargs['month']} )

    def form_valid(self, form):
        response = super(ExpenseUpdateView, self).form_valid(form)
        return response


class PersonnelView(LoginRequiredMixin, TemplateView):
    template_name = 'accounting/personnel.html'

    def get_context_data(self, **kwargs):
        context = super(PersonnelView, self).get_context_data()
        business_units = BusinessUnit.objects.filter(user=self.request.user)
        context['business_units'] = business_units
        current = BusinessUnit.objects.get(pk=kwargs['pk'])
        context['current'] = current

        fiscal_years = FiscalYear.objects.filter(business_unit=current)

        now = datetime.datetime.now()
        current_month = None
        for fiscal_year in fiscal_years:
            months = Month.objects.filter(fiscal_year=fiscal_year)
            for month in months:
                if month.month.month == now.month:
                    current_month = month
        context['current_month'] = current_month


        personnel = Personnel.objects.all()
        context['personnel'] = personnel

        salary = Salary.objects.all()
        context['salary'] = salary

        part_time = PartTime.objects.all()
        context['part_time'] = part_time

        return context


class SalaryCreateView(LoginRequiredMixin, CreateView):
    template_name = 'accounting/salary_create_form.html'
    model = Salary
    form_class = SalaryCreateForm

    def get_context_data(self, *args, **kwargs):
        context = super(SalaryCreateView, self).get_context_data()
        return context

    def get_success_url(self):
        return reverse_lazy('accounting:personnel', kwargs= { 'pk':self.kwargs['pk'] } )

    def form_valid(self, form):
        form.instance.business_unit = BusinessUnit.objects.get(pk=self.kwargs['pk'])
        response = super(SalaryCreateView, self).form_valid(form)

        return response


class SalaryDeleteView(LoginRequiredMixin, DeleteView):
    model = Salary
    template_name_suffix = '_delete_form'

    def get_object(self):
        return Salary.objects.get(pk=self.kwargs['salary'])

    def get_success_url(self):
        return reverse_lazy('accounting:personnel', kwargs={'pk': self.kwargs["pk"]})


class SalaryUpdateView(LoginRequiredMixin, UpdateView):
    template_name_suffix = '_update_form'
    form_class = SalaryUpdateForm
    model = Salary

    def get_object(self):
        return Salary.objects.get(pk=self.kwargs['salary'])

    def get_success_url(self):
        return reverse_lazy('accounting:personnel', kwargs=self.kwargs)

    def form_valid(self, form):
        response = super(SalaryUpdateView, self).form_valid(form)
        return response


class PartTimeCreateView(LoginRequiredMixin, CreateView):
    template_name = 'accounting/part_time_create_form.html'
    model = PartTime
    form_class = PartTimeCreateForm

    def get_context_data(self, *args, **kwargs):
        context = super(PartTimeCreateView, self).get_context_data()
        return context

    def get_success_url(self):
        return reverse_lazy('accounting:personnel', kwargs= { 'pk':self.kwargs['pk'] } )

    def form_valid(self, form):
        form.instance.business_unit = BusinessUnit.objects.get(pk=self.kwargs['pk'])
        form.instance.hours_work = 20
        response = super(PartTimeCreateView, self).form_valid(form)

        return response


class PartTimeDeleteView(LoginRequiredMixin, DeleteView):
    model = PartTime
    template_name = 'accounting/part_time_delete_form.html'

    def get_object(self):
        return PartTime.objects.get(pk=self.kwargs['part_time'])

    def get_success_url(self):
        return reverse_lazy('accounting:personnel', kwargs={'pk': self.kwargs["pk"]})


class PartTimeUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'accounting/part_time_update_form.html'
    form_class = PartTimeUpdateForm
    model = PartTime

    def get_object(self):
        return PartTime.objects.get(pk=self.kwargs['part_time'])

    def get_success_url(self):
        return reverse_lazy('accounting:personnel', kwargs=self.kwargs)

    def form_valid(self, form):
        response = super(PartTimeUpdateView, self).form_valid(form)
        return response


class IncomeCreateView(LoginRequiredMixin, CreateView):
    template_name = 'accounting/income_create_form.html'
    model = Income
    form_class = IncomeCreateForm

    def get_context_data(self, *args, **kwargs):
        context = super(IncomeCreateView, self).get_context_data()
        return context

    def get_success_url(self):
        return reverse_lazy('accounting:expenses', kwargs= { 'pk':self.kwargs['pk'], 'month': self.kwargs['month']} )

    def form_valid(self, form):
        form.instance.business_unit = BusinessUnit.objects.get(pk=self.kwargs['pk'])
        month = Month.objects.get(pk=self.kwargs['month'])
        try:
            if self.request.POST['reocurring']:
                months = Month.objects.filter(fiscal_year=month.fiscal_year)
                for m in months:
                    if m.month >= month.month:
                        Income.objects.create(
                            business_unit = form.instance.business_unit,
                            month = m,
                            predicted_amount = form.instance.predicted_amount,
                            name = form.instance.name,
                            data_payable = form.instance.data_payable,
                        )
            return redirect('accounting:expenses', pk=self.kwargs['pk'], month=self.kwargs['month'] )
        except KeyError:
            print "Exception thrown"
            form.instance.month = month
        response = super(IncomeCreateView, self).form_valid(form)

        return response


class IncomeDeleteView(LoginRequiredMixin, DeleteView):
    model = Income
    template_name_suffix = '_delete_form'

    def get_object(self):
        return Income.objects.get(pk=self.kwargs['income'])

    def get_success_url(self):
        return reverse_lazy('accounting:expenses', kwargs={'pk': self.kwargs["pk"], 'month': self.kwargs['month']})


class IncomeUpdateView(LoginRequiredMixin, UpdateView):
    template_name_suffix = '_update_form'
    form_class = IncomeUpdateForm
    model = Income

    def get_object(self):
        return Income.objects.get(pk=self.kwargs['income'])

    def get_success_url(self):
        return reverse_lazy('accounting:expenses', kwargs= {'pk':self.kwargs['pk'], 'month': self.kwargs['month']} )

    def form_valid(self, form):
        response = super(IncomeUpdateView, self).form_valid(form)
        return response
