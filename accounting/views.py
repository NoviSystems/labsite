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
from django.core.exceptions import ObjectDoesNotExist


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

        # Get all business units for a user
        business_units = BusinessUnit.objects.filter(user=self.request.user)
        context['business_units'] = business_units

        # Get the business unit the user is currently viewing
        current = BusinessUnit.objects.get(pk=kwargs['pk'])
        context['current'] = current

        # Get the fical years associated for the business unit
        fiscal_years = FiscalYear.objects.filter(business_unit=current)
        context['fiscal_years'] = fiscal_years

        # Finding the current month
        current_month = None
        now = datetime.datetime.now()

        cma = {
            'title': 'Cash Month Actual',
            'values': []
        }
        cmpr = {
            'title': 'Cash Month Projected',
            'values': []
        }
        ema = {
            'title': 'Expenses Month Actual',
            'values': []
        }
        emp = {
            'title': 'Expenses Month Projected',
            'values': []
        }
        ima = {
            'title': 'Recievables Month Actual',
            'values': []
        }
        imp = {
            'title': 'Recievables Month Projected',
            'values': []
        }
        pma = {
            'title': 'Payroll Month Actual',
            'values': []
        }
        pmp = {
            'title': 'Payroll Month Projected',
            'values': []
        }
        tama = {
            'title': 'Total Assets Projected',
            'values': []
        }
        tamp = {
            'title': 'Total Assets Actual',
            'values': []
        }

        # Month names used on graph and table
        months_names = []

        # Computes totals for the whole fiscal year
        months = []

        # moves through all fiscal years
        for fiscal_year in fiscal_years:

            # gets all months
            months = Month.objects.filter(fiscal_year=fiscal_year)

            # moves through all months
            for month in months:

                # gets current month
                if month.month.month == now.month:
                    current_month = month

                # gets all month names
                months_names.append(month.month.strftime("%B"))

                # payroll variables
                payroll_month_actual = Decimal('0.00')
                payroll_month_projected = Decimal('0.00')

                # add up payroll expenses for the month
                for payroll in Payroll.objects.filter(month=month):
                    if payroll.expense.reconciled:
                        payroll_month_actual += payroll.expense.actual_amount
                    payroll_month_projected += payroll.expense.predicted_amount

                # adds payroll values to month lists for table
                pma['values'].append(payroll_month_actual)
                pmp['values'].append(payroll_month_projected)

                # expenses variables
                expenses_month_actual = Decimal('0.00')
                expense_month_projected = Decimal('0.00')

                # add up all expense values 
                for expense in Expense.objects.filter(month=month):
                    if expense.reconciled:
                        expenses_month_actual += expense.actual_amount
                    expense_month_projected += expense.predicted_amount

                # subtract payroll values to get plain expense
                expenses_month_actual -= payroll_month_actual
                expense_month_projected -= payroll_month_projected

                # all the expenses to lists for table
                ema['values'].append(expenses_month_actual)
                emp['values'].append(expense_month_projected)

                # income variables
                income_month_actual = Decimal('0.00')
                income_month_projected = Decimal('0.00')

                # add up all income values
                for income in Income.objects.filter(month=month):
                    if income.reconciled:
                        income_month_actual += income.actual_amount
                    income_month_projected += income.predicted_amount

                # add income to lists for table
                ima['values'].append(income_month_actual)
                imp['values'].append(income_month_projected)

                # cash variables
                cash_month_actual = Decimal('0.00')
                cash_month_projected = Decimal('0.00')

                # compute cash values
                for cash in Cash.objects.filter(month=month):
                    if cash.reconciled:
                        cash_month_actual += cash.actual_amount
                    cash_month_projected += cash.predicted_amount
                
                # add cash to lists for table
                cmpr['values'].append(cash_month_projected)
                cma['values'].append(cash_month_actual)

                # income booked variables
                income_booked_projected = Decimal('0.00')

                # compute income booked projected
                for value in imp['values']:
                    income_booked_projected += value
                total_assets_month_projected = cash_month_projected + income_booked_projected
                tamp['values'].append(total_assets_month_projected)

                # computer income booked actual
                income_booked_actual = Decimal('0.00')
                for value in ima['values']:
                    income_booked_actual += value
                total_assets_month_actual = cash_month_actual + income_booked_actual
                tama['values'].append(total_assets_month_actual)

        # list of dashboard data
        dashboard_data = [ cma, cmpr, ema, emp, ima, imp, pma, pmp, tama, tamp ]
        
        # Context totals for the Graph values
        context['current_month'] = current_month
        context['months_names'] = months_names
        context['months'] = months
        context['months_j'] = json.dumps(months_names)
        context['predicted_totals'] = json.dumps( [float(value) for value in cmpr['values']] )
        context['actual_totals'] = json.dumps([float(value) for value in cma['values']])
        context['dashboard_data'] = dashboard_data

        # Personnel and Contracts totals
        personnel = Personnel.objects.filter(business_unit=current)
        context['personnel'] = personnel
        contracts = Contract.objects.filter(business_unit=current)
        context['contracts'] = contracts

        return context


class DashboardMonthView(DashboardView):
    template_name = 'accounting/dashboard_month.html'

    def get_context_data(self, **kwargs):
        context = super(DashboardMonthView, self).get_context_data(**kwargs)
        month_data = {
            'month': Month.objects.get(pk=kwargs['month']),
        }
        context['month_data'] = month_data
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
        months = []
        for fiscal_year in fiscal_years:
            months.extend(Month.objects.filter(fiscal_year=fiscal_year))
            for month in months:
                if month.month.month == now.month:
                    current_month = month


        month = Month.objects.get(pk=kwargs['month'])
        try:
            cash = Cash.objects.get(month=month)
        except ObjectDoesNotExist:
            cash = None
        month_data = {
            'month': month,
            'expenses': Expense.objects.filter(month=month),
            'incomes':Income.objects.filter(month=month),
            'cash': cash
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

    def get_success_url(self):
        return reverse_lazy('accounting:dashboard', kwargs=self.kwargs)

    def form_valid(self, form):
        business_unit = BusinessUnit.objects.get(pk=self.kwargs['pk'])
        form.instance.business_unit = business_unit
        response = super(FiscalYearCreateView, self).form_valid(form)
        fiscal_year = form.instance
        cash_amount = form.instance.cash_amount
        populateCashPredicted(fiscal_year=fiscal_year, cash_amount=cash_amount)
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
        business_unit = BusinessUnit.objects.get(pk=self.kwargs['pk'])
        month = Month.objects.get(fiscal_year__business_unit=business_unit, month__month=form.instance.date.month)
        form.instance.month = month
        form.instance.contract = Contract.objects.get(pk=self.kwargs['contract'])
        try:
            predicted_amount = self.request.POST['predicted_amount']
            income = None
            try:
                income = Income.objects.create(
                    business_unit = business_unit,
                    month = month,
                    predicted_amount = predicted_amount,
                    name = form.instance.contract.organization_name,
                    data_payable = form.instance.date,
                )
                form.instance.income = income
            except:
                print "Could Not Create Income Object For Invoice"
        except KeyError:
            print "No Predicted Amount In Post Request"
        response = super(InvoiceCreateView, self).form_valid(form)
        updateCashPredicted(business_unit=business_unit)
        return response


class InvoiceDeleteView(LoginRequiredMixin, DeleteView):
    model = Invoice
    template_name_suffix = '_delete_form'

    def get_object(self):
        return Invoice.objects.get(pk=self.kwargs['invoice'])

    def get_success_url(self):
        return reverse_lazy('accounting:contracts', kwargs={'pk': self.kwargs["pk"]})

    def delete(self, request, *args, **kwargs):
        response = super(InvoiceDeleteView, self).delete(request, *args, **kwargs)
        business_unit = BusinessUnit.objects.get(pk=self.kwargs['pk'])
        updateCashPredicted(business_unit=business_unit)
        return response


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
        business_unit = BusinessUnit.objects.get(pk=self.kwargs['pk'])
        updateCashPredicted(business_unit=business_unit)
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
                        new_date_payable = date( m.month.year, m.month.month, form.instance.data_payable.day)
                        Expense.objects.create(
                            business_unit = form.instance.business_unit,
                            month = m,
                            predicted_amount = form.instance.predicted_amount,
                            name = form.instance.name,
                            data_payable = new_date_payable,
                        )
            return redirect('accounting:expenses', pk=self.kwargs['pk'], month=self.kwargs['month'] )
        except KeyError:
            print "Exception thrown"
            form.instance.month = month
        response = super(ExpenseCreateView, self).form_valid(form)
        business_unit = BusinessUnit.objects.get(pk=self.kwargs['pk'])
        updateCashPredicted(business_unit=business_unit)
        return response


class ExpenseDeleteView(LoginRequiredMixin, DeleteView):
    model = Expense
    template_name_suffix = '_delete_form'

    def get_object(self):
        return Expense.objects.get(pk=self.kwargs['expense'])

    def get_success_url(self):
        return reverse_lazy('accounting:expenses', kwargs={'pk': self.kwargs["pk"], 'month': self.kwargs['month']})

    def delete(self, request, *args, **kwargs):
        response = super(ExpenseDeleteView, self).delete(request, *args, **kwargs)
        business_unit = BusinessUnit.objects.get(pk=self.kwargs['pk'])
        updateCashPredicted(business_unit=business_unit)
        return response


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
        business_unit = BusinessUnit.objects.get(pk=self.kwargs['pk'])
        updateCashPredicted(business_unit=business_unit)
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


        personnel = Personnel.objects.filter(business_unit=current)
        context['personnel'] = personnel

        salary = Salary.objects.filter(business_unit=current)
        context['salary'] = salary

        part_time = PartTime.objects.filter(business_unit=current)
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
        business_unit = BusinessUnit.objects.get(pk=self.kwargs['pk'])
        form.instance.business_unit = business_unit
        response = super(SalaryCreateView, self).form_valid(form)
        updatePayroll(business_unit=business_unit)
        return response


class SalaryDeleteView(LoginRequiredMixin, DeleteView):
    model = Salary
    template_name_suffix = '_delete_form'

    def get_object(self):
        return Salary.objects.get(pk=self.kwargs['salary'])

    def get_success_url(self):
        return reverse_lazy('accounting:personnel', kwargs={'pk': self.kwargs["pk"]})

    def delete(self, request, *args, **kwargs):
        response = super(SalaryDeleteView, self).delete(request, *args, **kwargs)
        business_unit = BusinessUnit.objects.get(pk=self.kwargs['pk'])
        updatePayroll(business_unit=business_unit)
        updateCashPredicted(business_unit=business_unit)
        return response


class SalaryUpdateView(LoginRequiredMixin, UpdateView):
    template_name_suffix = '_update_form'
    form_class = SalaryUpdateForm
    model = Salary

    def get_object(self):
        return Salary.objects.get(pk=self.kwargs['salary'])

    def get_success_url(self):
        return reverse_lazy('accounting:personnel', kwargs={'pk': self.kwargs["pk"]})

    def form_valid(self, form):
        business_unit = BusinessUnit.objects.get(pk=self.kwargs['pk'])
        response = super(SalaryUpdateView, self).form_valid(form)
        updatePayroll(business_unit=business_unit)
        updateCashPredicted(business_unit=business_unit)
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
        business_unit = BusinessUnit.objects.get(pk=self.kwargs['pk'])
        form.instance.business_unit = business_unit
        form.instance.hours_work = 20
        response = super(PartTimeCreateView, self).form_valid(form)
        updatePayroll(business_unit=business_unit)
        updateCashPredicted(business_unit=business_unit)
        return response


class PartTimeDeleteView(LoginRequiredMixin, DeleteView):
    model = PartTime
    template_name = 'accounting/part_time_delete_form.html'

    def get_object(self):
        return PartTime.objects.get(pk=self.kwargs['part_time'])

    def get_success_url(self):
        return reverse_lazy('accounting:personnel', kwargs={'pk': self.kwargs["pk"]})

    def delete(self, request, *args, **kwargs):
        response = super(PartTimeDeleteView, self).delete(request, *args, **kwargs)
        business_unit = BusinessUnit.objects.get(pk=self.kwargs['pk'])
        updatePayroll(business_unit=business_unit)
        updateCashPredicted(business_unit=business_unit)
        return response


class PartTimeUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'accounting/part_time_update_form.html'
    form_class = PartTimeUpdateForm
    model = PartTime

    def get_object(self):
        return PartTime.objects.get(pk=self.kwargs['part_time'])

    def get_success_url(self):
        return reverse_lazy('accounting:personnel', kwargs= { 'pk':self.kwargs['pk'] } )

    def form_valid(self, form):
        business_unit = BusinessUnit.objects.get(pk=self.kwargs['pk'])
        response = super(PartTimeUpdateView, self).form_valid(form)
        updatePayroll(business_unit=business_unit)
        updateCashPredicted(business_unit=business_unit)
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

    def delete(self, request, *args, **kwargs):
        response = super(IncomeDeleteView, self).delete(request, *args, **kwargs)
        business_unit = BusinessUnit.objects.get(pk=self.kwargs['pk'])
        updateCashPredicted(business_unit=business_unit)
        return response


class IncomeUpdateView(LoginRequiredMixin, UpdateView):
    template_name_suffix = '_update_form'
    form_class = IncomeUpdateForm
    model = Income

    def get_object(self):
        return Income.objects.get(pk=self.kwargs['income'])

    def get_success_url(self):
        return reverse_lazy('accounting:expenses', kwargs= {'pk':self.kwargs['pk'], 'month': self.kwargs['month']} )

    def form_valid(self, form):
        business_unit = BusinessUnit.objects.get(pk=self.kwargs['pk'])
        response = super(IncomeUpdateView, self).form_valid(form)
        updateCashPredicted(business_unit=business_unit)
        return response


class CashUpdateView(LoginRequiredMixin, UpdateView):
    template_name_suffix = '_update_form'
    form_class = CashUpdateForm
    model = Cash

    def get_object(self):
        return Cash.objects.get(pk=self.kwargs['cash'])

    def get_success_url(self):
        return reverse_lazy('accounting:expenses', kwargs={'pk':self.kwargs['pk'], 'month': self.kwargs['month']})

    def form_valid(self, form):
        business_unit = BusinessUnit.objects.get(pk=self.kwargs['pk'])
        response = super(CashUpdateView, self).form_valid(form)
        updateCashPredicted(business_unit=business_unit)
        return response


def updatePayroll(business_unit):
    # for personnel in business unit
    # total up salary
    # total up part time
    payroll_amount = Decimal('0.00')
    salary = Salary.objects.filter(business_unit=business_unit)
    for salary in salary:
       payroll_amount += (salary.social_security_amount + salary.fed_health_insurance_amount + salary.retirement_amount + salary.medical_insurance_amount + salary.staff_benefits_amount + salary.fringe_amount)
    part_time = PartTime.objects.filter(business_unit=business_unit)
    for part_time in part_time:
        payroll_amount += part_time.hourly_amount * part_time.hours_work

    # for month in month in fiscal year
    # get payroll object
    # if payroll object expese is not reconciled
    # update its predicted value with the total
    fiscal_years = FiscalYear.objects.filter(business_unit=business_unit)
    for fiscal_year in fiscal_years:
        months = Month.objects.filter(fiscal_year=fiscal_year)
        for month in months:
            payroll = None
            try:
                payroll = Payroll.objects.get(month=month)
            except ObjectDoesNotExist:
                expense = Expense.objects.create(
                    business_unit = business_unit,
                    month = month,
                    name = 'Payroll',
                    data_payable = month.month
                )
                payroll = Payroll.objects.create(month=month, expense=expense)
            payroll.expense.predicted_amount = payroll_amount
            payroll.expense.save()


def populateCashPredicted(fiscal_year, cash_amount):
    cash_previous = Decimal(cash_amount)
    for month in Month.objects.filter(fiscal_year=fiscal_year):
        print month.month
        print "cash previous: ", cash_previous

        expense_month_projected = Decimal('0.00')
        for expense in Expense.objects.filter(month=month):
            expense_month_projected += expense.predicted_amount
        income_month_projected = Decimal('0.00')
        for income in Income.objects.filter(month=month):
            income_month_projected += income.predicted_amount
        cash = Cash.objects.get(month=month)
        
        print "cash predicted_amount: ", cash.predicted_amount
        cash.predicted_amount = cash_previous - expense_month_projected + income_month_projected
        print "new predicted_amount: ", cash.predicted_amount
        cash.save()
        print "post save predicted_amount: ", cash.predicted_amount
        if cash.reconciled:
            cash_previous = cash.actual_amount
        else:
            cash_previous = cash.predicted_amount


def updateCashPredicted(business_unit):
    fiscal_years = FiscalYear.objects.filter(business_unit=business_unit)
    for fiscal_year in fiscal_years:
        cash_previous = Decimal(fiscal_year.cash_amount)
        for month in Month.objects.filter(fiscal_year=fiscal_year):
            expense_month_projected = Decimal('0.00')
            for expense in Expense.objects.filter(month=month):
                expense_month_projected += expense.predicted_amount
            income_month_projected = Decimal('0.00')
            for income in Income.objects.filter(month=month):
                income_month_projected += income.predicted_amount
            cash = Cash.objects.get(month=month)
            cash.predicted_amount = cash_previous - expense_month_projected + income_month_projected
            cash.save()
            if cash.reconciled:
                cash_previous = cash.actual_amount
            else:
                cash_previous = cash.predicted_amount
