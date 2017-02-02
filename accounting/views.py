import json
from datetime import date
from dateutil.rrule import rrule, MONTHLY
from calendar import monthrange
from decimal import Decimal

from django.shortcuts import redirect
from django.db.models import Max, Sum
from django.db.transaction import atomic
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse, reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import Http404
from django.views.generic import TemplateView, CreateView, UpdateView, DeleteView

from accounting import models
from accounting import forms


class PermissionsMixin(LoginRequiredMixin, object):

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated():
            try:
                self.team_roles = models.UserTeamRole.objects.filter(user=self.request.user)
                self.business_units = []
                for team_role in self.team_roles:
                    self.business_units.append(team_role.business_unit)
            except ObjectDoesNotExist:
                self.team_roles = None
                self.business_units = None
        else:
            self.team_roles = None
        return super(PermissionsMixin, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super(PermissionsMixin, self).get_context_data(*args, **kwargs)
        context['business_units'] = self.business_units
        return context


class SetUpMixin(object):
    success_url_name = None

    def get_fiscal_year(self, calendar_date):
        calendar_year = calendar_date.year

        # if we're in the first half of the calendar year, then we're in the previous fiscal year
        if calendar_date < date(calendar_year, 7, 1):
            return calendar_year - 1
        return calendar_year

    def get_object_fiscal_year(self):
        pass

    @atomic
    def dispatch(self, request, *args, **kwargs):
        self.current_business_unit = models.BusinessUnit.objects.get(pk=kwargs['business_unit'])
        self.now = date.today()

        fiscal_year = self.get_fiscal_year(self.now)

        self.start_year = date(fiscal_year, 7, 1)
        self.end_year = date(fiscal_year+1, 6, 30)

        return super(SetUpMixin, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super(SetUpMixin, self).get_context_data(*args, **kwargs)
        try:
            context['is_viewer'] = self.is_viewer
        except AttributeError:
            context['is_viewer'] = False
        context['current_business_unit'] = self.current_business_unit

        if 'start_year' in self.kwargs and 'end_year' in self.kwargs:
            self.start_year = date(int(self.kwargs['start_year']), 7, 1)
            self.end_year = date(int(self.kwargs['end_year']), 6, 30)

        context['start_year'] = self.start_year.year
        context['end_year'] = self.end_year.year
        return context

    def get_success_url_kwargs(self):
        return {
            'business_unit': self.kwargs['business_unit']
        }

    def get_success_url(self):
        return reverse(self.success_url_name, kwargs=self.get_success_url_kwargs())


class ViewerMixin(SetUpMixin, PermissionsMixin, UserPassesTestMixin):

    def test_func(self):
        try:
            bu_role = models.UserTeamRole.objects.get(user=self.request.user, business_unit=self.current_business_unit).role
            if self.request.user.is_superuser:
                return True
            elif bu_role == 'MANAGER':
                return True
            elif bu_role == 'VIEWER':
                self.is_viewer = True
                return True
            else:
                raise Http404()
        except ObjectDoesNotExist:
            raise Http404()


class ManagerMixin(SetUpMixin, PermissionsMixin, UserPassesTestMixin):

    def test_func(self):
        try:
            bu_role = models.UserTeamRole.objects.get(user=self.request.user, business_unit=self.current_business_unit).role
            if self.request.user.is_superuser:
                return True
            elif bu_role == 'MANAGER':
                return True
            else:
                raise Http404()
        except ObjectDoesNotExist:
            raise Http404()


class HomePageView(PermissionsMixin, TemplateView):
    template_name = 'accounting/home.html'

    def get_context_data(self, **kwargs):
        context = super(HomePageView, self).get_context_data()
        context['business_units'] = self.business_units
        return context


class DashboardView(ViewerMixin, TemplateView):
    template_name = 'accounting/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super(DashboardView, self).get_context_data()
        cma = {'title': 'Cash Month Actual', 'values': {}}
        cmpr = {'title': 'Cash Month Projected', 'values': {}}
        ema = {'title': 'Expenses Month Actual', 'values': {}}
        emp = {'title': 'Expenses Month Projected', 'values': {}}
        ima = {'title': 'Receivables Month Actual', 'values': {}}
        imp = {'title': 'Receivables Month Projected', 'values': {}}
        pma = {'title': 'Payroll Month Actual', 'values': {}}
        pmp = {'title': 'Payroll Month Projected', 'values': {}}
        tama = {'title': 'Total Assets Actual', 'values': {}}
        tamp = {'title': 'Total Assets Projected', 'values': {}}

        months = [month for month in rrule(MONTHLY, dtstart=self.start_year, until=self.end_year)]
        month_names = []

        last_cash = Decimal('0.00')
        cash_month_projected = Decimal('0.00')
        payroll_month_projected = calculatePayrollProjectedAmount(self.current_business_unit)

        for month in months:

            start_date = '{}-{}-{}'.format(month.year, month.month, '01')
            end_date = '{}-{}-{}'.format(month.year, month.month, monthrange(month.year, month.month)[1])

            month_name = month.strftime("%B")
            month_names.append(month_name)

            try:
                previous_month = month
                if previous_month.month == 1:
                    previous_month = date(previous_month.year - 1, 12, monthrange(previous_month.year - 1, 12)[1])
                else:
                    previous_month = date(previous_month.year, previous_month.month - 1, monthrange(previous_month.year, previous_month.month - 1)[1])
                last_cash = models.Cash.objects.get(business_unit=self.current_business_unit.pk, date_associated=('{}-{}-{}'.format(previous_month.year, previous_month.month, monthrange(previous_month.year, previous_month.month)[1]))).actual_amount
            except ObjectDoesNotExist:
                last_cash = cash_month_projected

            try:
                cash_month_actual = models.Cash.objects.get(business_unit=self.current_business_unit.pk, date_associated=(end_date)).actual_amount
                cash_month_projected = last_cash
            except ObjectDoesNotExist:
                cash_month_actual = Decimal('0.00')
                cash_month_projected = last_cash

            payroll_month_actual = models.Expense.objects.filter(expense_type='PAYROLL', reconciled=True, business_unit=self.current_business_unit, date_payable__range=[start_date, end_date]).aggregate(Sum('actual_amount'))['actual_amount__sum']
            if payroll_month_actual is None:
                payroll_month_actual = Decimal('0.00')
            pma['values'][month_name] = payroll_month_actual
            pmp['values'][month_name] = payroll_month_projected

            expenses_month_actual = Decimal('0.00')
            expenses_month_projected = Decimal('0.00')
            for expense in models.Expense.objects.filter(expense_type='GENERAL', business_unit=self.current_business_unit, date_payable__range=[start_date, end_date]):
                if expense.reconciled:
                    expenses_month_actual += expense.actual_amount
                else:
                    expenses_month_projected += expense.predicted_amount
            ema['values'][month_name] = expenses_month_actual
            emp['values'][month_name] = expenses_month_projected

            income_month_actual = Decimal('0.00')
            income_month_projected = Decimal('0.00')
            for income in models.Income.objects.filter(business_unit=self.current_business_unit, date_payable__range=[start_date, end_date]):
                if income.reconciled:
                    income_month_actual += income.actual_amount
                else:
                    income_month_projected += income.predicted_amount
            ima['values'][month_name] = income_month_actual
            imp['values'][month_name] = income_month_projected

            cash_month_projected += (income_month_projected - expenses_month_projected - payroll_month_projected)
            cmpr['values'][month_name] = cash_month_projected
            cma['values'][month_name] = cash_month_actual

            income_booked_projected = Decimal('0.00')
            for value in imp['values'].values():
                income_booked_projected += value
            total_assets_month_projected = cash_month_projected + income_booked_projected
            tamp['values'][month_name] = total_assets_month_projected

            income_booked_actual = Decimal('0.00')
            for value in ima['values'].values():
                income_booked_actual += value
            total_assets_month_actual = cash_month_actual
            tama['values'][month_name] = total_assets_month_actual

        dashboard_data = [cma, cmpr, ima, imp, pma, pmp, ema, emp, tama, tamp]
        context['month_names'] = month_names
        context['predicted_totals'] = json.dumps([float(cmpr['values'][month_name]) for month_name in month_names])
        context['actual_totals'] = json.dumps([float(cma['values'][month_name]) for month_name in month_names])
        context['dashboard_data'] = dashboard_data
        return context


class ContractsView(ViewerMixin, SetUpMixin, TemplateView):
    template_name = 'accounting/contracts.html'

    def get_context_data(self, **kwargs):
        context = super(ContractsView, self).get_context_data()
        contracts = models.Contract.objects.filter(business_unit=self.current_business_unit)
        completed_contracts = []
        active_contracts = []
        for contract in contracts:
            if contract.contract_state == 'ACTIVE':
                invoices = models.Invoice.objects.filter(contract=contract).order_by('date_payable')
                active_contracts.extend([
                    {
                        'contract': contract,
                        'invoices': invoices,
                    }
                ])
            elif contract.contract_state == 'COMPLETE':
                invoices = models.Invoice.objects.filter(contract=contract)
                completed_contracts.extend([
                    {
                        'contract': contract,
                        'invoices': invoices,
                    }
                ])
        context['active_contracts'] = active_contracts
        context['completed_contracts'] = completed_contracts
        return context


class RevenueView(ViewerMixin, SetUpMixin, TemplateView):
    template_name = 'accounting/revenue.html'

    def get_context_data(self, **kwargs):
        context = super(RevenueView, self).get_context_data()
        invoices = models.Invoice.objects.filter(contract__business_unit=self.current_business_unit)
        context['invoices'] = invoices
        return context


class MonthlyReconcileView(ViewerMixin, SetUpMixin, TemplateView):
    template_name = 'accounting/monthly_reconcile.html'

    def get_context_data(self, **kwargs):
        context = super(MonthlyReconcileView, self).get_context_data()
        months = []
        [months.append(month) for month in rrule(MONTHLY, dtstart=self.start_year, until=self.end_year)]
        context['months'] = months

        active_month_int = None
        if 'month' in self.kwargs:
            active_month_int = int(self.kwargs['month'])
        else:
            active_month_int = int(self.now.month)

        start_date = None
        end_date = None
        active_month = None
        for month in months:
            if month.month == active_month_int:
                days_in_month = monthrange(month.year, month.month)[1]
                start_date = '{}-{}-{}'.format(month.year, month.month, '01')
                end_date = '{}-{}-{}'.format(month.year, month.month, days_in_month)
                active_month = date(month.year, month.month, days_in_month)
        try:
            context['payroll'] = models.Expense.objects.get(business_unit=self.current_business_unit, expense_type='PAYROLL', date_payable__range=[start_date, end_date])
        except models.Expense.DoesNotExist:
            context['payroll'] = None
        context['expenses'] = models.Expense.objects.filter(business_unit=self.current_business_unit, expense_type='GENERAL', date_payable__range=[start_date, end_date])
        context['incomes'] = models.Income.objects.filter(business_unit=self.current_business_unit, date_payable__range=[start_date, end_date])
        try:
            context['cash'] = models.Cash.objects.get(business_unit=self.current_business_unit, date_associated=end_date)
        except ObjectDoesNotExist:
            context['cash'] = None
        context['active_month'] = active_month
        return context


class BusinessUnitSettingsPageView(ManagerMixin, TemplateView):
    template_name = 'accounting/settings/business_unit.html'

    def get_context_data(self, **kwargs):
        context = super(BusinessUnitSettingsPageView, self).get_context_data()
        users = models.UserTeamRole.objects.filter(business_unit=self.current_business_unit)
        viewers = [user for user in users if user.role == 'VIEWER']
        managers = [user for user in users if user.role == 'MANAGER']
        context['viewers'] = viewers
        context['managers'] = managers
        return context


class UserTeamRolesSettingsPageView(ManagerMixin, TemplateView):
    template_name = 'accounting/settings/user_team_roles.html'

    def get_context_data(self, **kwargs):
        context = super(UserTeamRolesSettingsPageView, self).get_context_data()
        users = models.UserTeamRole.objects.filter(business_unit=self.current_business_unit)
        viewers = [user for user in users if user.role == 'VIEWER']
        managers = [user for user in users if user.role == 'MANAGER']
        context['viewers'] = viewers
        context['managers'] = managers
        return context


class BusinessUnitCreateView(LoginRequiredMixin, CreateView):
    model = models.BusinessUnit
    form_class = forms.BusinessUnitCreateForm
    template_name = 'accounting/base_form.html'
    success_url = reverse_lazy('accounting:home')

    def form_valid(self, form):
        response = super(BusinessUnitCreateView, self).form_valid(form)
        models.UserTeamRole.objects.create(user=self.request.user, business_unit=form.instance, role='MANAGER')
        return response


class BusinessUnitDeleteView(ManagerMixin, DeleteView):
    model = models.BusinessUnit
    template_name = 'accounting/base_delete_form.html'
    success_url = reverse_lazy('accounting:home')
    pk_url_kwarg = 'business_unit'


class BusinessUnitUpdateView(ManagerMixin, UpdateView):
    model = models.BusinessUnit
    form_class = forms
    template_name = 'accounting/base_form.html'
    pk_url_kwarg = 'business_unit'

    def get_success_url(self):
        return reverse_lazy('accounting:business_unit_settings', kwargs={'business_unit': self.kwargs['business_unit']})


class ContractCreateView(ManagerMixin, CreateView):
    model = models.Contract
    form_class = forms.ContractCreateForm
    template_name = 'accounting/base_form.html'

    def get_success_url(self):
        return reverse_lazy('accounting:contracts', kwargs=self.kwargs)

    def form_valid(self, form):
        business_unit = models.BusinessUnit.objects.get(pk=self.kwargs['business_unit'])
        form.instance.business_unit = business_unit
        max_contract_number = models.Contract.objects.filter(business_unit=business_unit).aggregate(Max('contract_number'))
        if not max_contract_number['contract_number__max']:
            form.instance.contract_number = 1
        else:
            form.instance.contract_number = max_contract_number['contract_number__max'] + 1

        return super(ContractCreateView, self).form_valid(form)


class ContractDeleteView(ManagerMixin, DeleteView):
    model = models.Contract
    template_name = 'accounting/base_delete_form.html'
    pk_url_kwarg = 'contract'

    def get_success_url(self):
        return reverse_lazy('accounting:contracts', kwargs={'business_unit': self.kwargs['business_unit']})


class ContractUpdateView(ManagerMixin, UpdateView):
    model = models.Contract
    form_class = forms.ContractUpdateForm
    template_name = 'accounting/base_form.html'
    pk_url_kwarg = 'contract'

    def get_success_url(self):
        return reverse_lazy('accounting:contracts', kwargs={'business_unit': self.kwargs['business_unit']})


class InvoiceCreateView(ManagerMixin, CreateView):
    model = models.Invoice
    form_class = forms.InvoiceCreateForm
    template_name = 'accounting/base_form.html'

    def get_success_url(self):
        return reverse_lazy('accounting:contracts', kwargs={'business_unit': self.kwargs['business_unit']})

    def form_valid(self, form):
        contract = models.Contract.objects.get(pk=self.kwargs['contract'])
        form.instance.contract = contract
        max_invoice_number = models.Invoice.objects.filter(contract=contract).aggregate(Max('number'))
        if not max_invoice_number['number__max']:
            form.instance.number = 1
        else:
            form.instance.number = max_invoice_number['number__max'] + 1
        form.instance.transition_state = 'NOT_INVOICED'
        business_unit = models.BusinessUnit.objects.get(pk=self.kwargs['business_unit'])
        form.instance.business_unit = business_unit
        contract_number = str(form.instance.contract.contract_number)
        contract_number = contract_number.zfill(4)
        form.instance.name = form.instance.contract.department + contract_number + '-' + str(form.instance.number)

        invoices_sum = models.Invoice.objects.filter(contract=contract).aggregate(Sum('predicted_amount'))['predicted_amount__sum']
        if invoices_sum is None:
            invoices_sum = Decimal('0.00')
        available_amount = contract.amount - invoices_sum
        if form.instance.predicted_amount <= available_amount:
            response = super(InvoiceCreateView, self).form_valid(form)
            return response
        else:
            error_message = 'Predicted amount must be less than or equal to {}'.format(available_amount)
            if available_amount == Decimal('0.00'):
                error_message = 'Invoices have reached contract total. Please update or delete exisiting invoices.'
            form.add_error('predicted_amount', error_message)
            return self.form_invalid(form)

        return response


class InvoiceDeleteView(ManagerMixin, DeleteView):
    model = models.Invoice
    template_name = 'accounting/base_delete_form.html'
    pk_url_kwarg = 'invoice'

    def get_success_url(self):
        return reverse_lazy('accounting:contracts', kwargs={'business_unit': self.kwargs['business_unit']})


class InvoiceUpdateView(ManagerMixin, UpdateView):
    model = models.Invoice
    form_class = forms.InvoiceUpdateForm
    template_name = 'accounting/base_form.html'
    pk_url_kwarg = 'invoice'

    def get_success_url(self):
        return reverse_lazy('accounting:contracts', kwargs={'business_unit': self.kwargs['business_unit']})

    def form_valid(self, form):
        if form.instance.actual_amount is not None and form.instance.date_paid is not None and form.instance.transition_state == 'RECEIVED':
            form.instance.reconciled = True
        else:
            form.instance.reconciled = False
        response = super(InvoiceUpdateView, self).form_valid(form)

        contract = models.Contract.objects.get(pk=self.kwargs['contract'])

        predicted_invoices_sum = models.Invoice.objects.filter(contract=contract).aggregate(Sum('predicted_amount'))['predicted_amount__sum']
        actual_invoices_sum = models.Invoice.objects.filter(contract=contract).aggregate(Sum('actual_amount'))['actual_amount__sum']

        if predicted_invoices_sum is None or actual_invoices_sum is None:
            predicted_invoices_sum = Decimal('0.00')
            actual_invoices_sum = Decimal('0.00')

        predicted_available_amount = contract.amount - predicted_invoices_sum + self.object.predicted_amount
        actual_available_amount = contract.amount - actual_invoices_sum + self.object.actual_amount

        if form.instance.predicted_amount > predicted_available_amount:
            error_message = 'Predicted amount must be less than or equal to {}'.format(predicted_available_amount)
            if predicted_available_amount == Decimal('0.00'):
                error_message = 'Invoices have reached contract total. Please update or delete exisiting invoices.'
            form.add_error('predicted_amount', error_message)

        if form.instance.actual_amount > actual_available_amount:
            error_message = 'Actual amount must be less than or equal to {}'.format(actual_available_amount)
            if actual_available_amount == Decimal('0.00'):
                error_message = 'Invoices have reached contract total. Please update or delete exisiting invoices.'
            form.add_error('actual_amount', error_message)

        elif form.instance.predicted_amount <= predicted_available_amount and form.instance.actual_amount <= actual_available_amount:
            response = super(InvoiceUpdateView, self).form_valid(form)
            return response

        return self.form_invalid(form)


class ExpenseMixin(ManagerMixin):
    model = models.Expense
    pk_url_kwarg = 'expense'
    success_url_name = 'accounting:reconcile'

    def get_object_fiscal_year(self):
        date = self.get_object().date_payable
        return self.get_fiscal_year(date)

    def get_success_url_kwargs(self):
        kwargs = super().get_success_url_kwargs()

        fy_object = self.get_object_fiscal_year()
        fy_now = self.get_fiscal_year(self.now)

        if fy_object is not None and fy_now != fy_object:
            kwargs.update({
                'start_year': fy_object,
                'end_year': fy_object + 1,
            })

        return kwargs


class ExpenseCreateView(ExpenseMixin, CreateView):
    form_class = forms.ExpenseCreateForm
    template_name = 'accounting/base_form.html'

    def form_valid(self, form):
        business_unit = models.BusinessUnit.objects.get(pk=self.kwargs['business_unit'])
        form.instance.business_unit = business_unit

        try:
            if 'recurring' in self.request.POST:
                date_payable = form.instance.date_payable
                until_date = None
                if int(date_payable.month) <= 6:
                    until_date = date(date_payable.year, 6, 30)
                else:
                    until_date = date(date_payable.year+1, 6, 30)

                monthly_expense_dates = [monthly_date for monthly_date in rrule(MONTHLY, dtstart=date_payable, until=until_date)]
                for expense_date in monthly_expense_dates:
                    expense = models.Expense(
                        business_unit=form.instance.business_unit,
                        predicted_amount=form.instance.predicted_amount,
                        name=form.instance.name,
                        date_payable=expense_date,
                    )
                    if expense_date.date() < self.now:
                        expense.date_paid = expense_date
                        expense.actual_amount = form.instance.predicted_amount
                    expense.save()
                return redirect('accounting:reconcile', pk=self.kwargs['pk'])
        except KeyError:
            if form.instance.date_payable < self.now:
                form.instance.date_paid = form.instance.date_payable
                form.instance.actual_amount = form.instance.predicted_amount

        # cache so we can us this in get_object_fiscal_year()
        self.object_date = form.instance.date_payable

        response = super(ExpenseCreateView, self).form_valid(form)
        return response

    def get_object_fiscal_year(self):
        return self.get_fiscal_year(self.object_date)


class ExpenseDeleteView(ExpenseMixin, DeleteView):
    model = models.Expense
    template_name = 'accounting/base_delete_form.html'


class ExpenseUpdateView(ExpenseMixin, UpdateView):
    form_class = forms.ExpenseUpdateForm
    template_name = 'accounting/base_form.html'


class IncomeCreateView(ManagerMixin, CreateView):
    model = models.Income
    form_class = forms.IncomeCreateForm
    template_name = 'accounting/base_form.html'

    def get_success_url(self):
        return reverse_lazy('accounting:reconcile', kwargs={'business_unit': self.kwargs['business_unit']})

    def form_valid(self, form):
        form.instance.business_unit = models.BusinessUnit.objects.get(pk=self.kwargs['business_unit'])
        try:
            if self.request.POST['recurring']:
                monthly_income_dates = [monthly_date for monthly_date in rrule(MONTHLY, dtstart=form.instance.date_payable, until=date(2017, 6, 30))]
                for income_date in monthly_income_dates:
                    income = models.Income(
                        business_unit=form.instance.business_unit,
                        predicted_amount=form.instance.predicted_amount,
                        name=form.instance.name,
                        date_payable=income_date,
                    )
                    if form.instance.date_payable < self.now:
                        form.instance.date_paid = form.instance.date_payable
                        form.instance.actual_amount = form.instance.predicted_amount
                    income.save()
        except KeyError:
            if form.instance.date_payable < self.now:
                form.instance.date_paid = form.instance.date_payable
                form.instance.actual_amount = form.instance.predicted_amount

        response = super(IncomeCreateView, self).form_valid(form)
        return response


class IncomeDeleteView(ManagerMixin, DeleteView):
    model = models.Income
    template_name = 'accounting/base_delete_form.html'
    pk_url_kwarg = 'income'

    def get_success_url(self):
        return reverse_lazy('accounting:reconcile', kwargs={'business_unit': self.kwargs['business_unit']})


class IncomeUpdateView(ManagerMixin, UpdateView):
    model = models.Income
    form_class = forms.IncomeUpdateForm
    template_name = 'accounting/base_form.html'
    pk_url_kwarg = 'income'

    def get_success_url(self):
        return reverse_lazy('accounting:reconcile', kwargs={'business_unit': self.kwargs['business_unit']})


class PersonnelView(ViewerMixin, TemplateView):
    template_name = 'accounting/personnel.html'

    def get_context_data(self, **kwargs):
        context = super(PersonnelView, self).get_context_data()

        full_time = models.FullTime.objects.filter(business_unit=self.current_business_unit)
        context['full_time'] = full_time

        part_time = models.PartTime.objects.filter(business_unit=self.current_business_unit)
        context['part_time'] = part_time

        return context


class FullTimeCreateView(ManagerMixin, CreateView):
    model = models.FullTime
    form_class = forms.FullTimeCreateForm
    template_name = 'accounting/base_form.html'

    def get_success_url(self):
        return reverse_lazy('accounting:personnel', kwargs={'business_unit': self.kwargs['business_unit']})

    def form_valid(self, form):
        business_unit = models.BusinessUnit.objects.get(pk=self.kwargs['business_unit'])
        form.instance.business_unit = business_unit
        response = super(FullTimeCreateView, self).form_valid(form)
        return response


class FullTimeDeleteView(ManagerMixin, DeleteView):
    model = models.FullTime
    template_name = 'accounting/base_delete_form.html'
    pk_url_kwarg = 'full_time'

    def get_success_url(self):
        return reverse_lazy('accounting:personnel', kwargs={'business_unit': self.kwargs['business_unit']})


class FullTimeUpdateView(ManagerMixin, UpdateView):
    model = models.FullTime
    form_class = forms.FullTimeUpdateForm
    template_name = 'accounting/base_form.html'
    pk_url_kwarg = 'full_time'

    def get_success_url(self):
        return reverse_lazy('accounting:personnel', kwargs={'business_unit': self.kwargs['business_unit']})


class PartTimeCreateView(ManagerMixin, CreateView):
    model = models.PartTime
    form_class = forms.PartTimeCreateForm
    template_name = 'accounting/base_form.html'

    def get_success_url(self):
        return reverse_lazy('accounting:personnel', kwargs={'business_unit': self.kwargs['business_unit']})

    def form_valid(self, form):
        business_unit = models.BusinessUnit.objects.get(pk=self.kwargs['business_unit'])
        form.instance.business_unit = business_unit
        form.instance.hours_work = 20
        response = super(PartTimeCreateView, self).form_valid(form)
        return response


class PartTimeDeleteView(ManagerMixin, DeleteView):
    model = models.PartTime
    template_name = 'accounting/base_delete_form.html'
    pk_url_kwarg = 'part_time'

    def get_success_url(self):
        return reverse_lazy('accounting:personnel', kwargs={'business_unit': self.kwargs['business_unit']})


class PartTimeUpdateView(ManagerMixin, UpdateView):
    model = models.PartTime
    form_class = forms.PartTimeUpdateForm
    template_name = 'accounting/base_form.html'
    pk_url_kwarg = 'part_time'

    def get_success_url(self):
        return reverse_lazy('accounting:personnel', kwargs={'business_unit': self.kwargs['business_unit']})


class UserTeamRoleCreateView(ManagerMixin, CreateView):
    model = models.UserTeamRole
    form_class = forms.UserTeamRoleCreateForm
    template_name = 'accounting/base_form.html'

    def get_success_url(self):
        return reverse_lazy('accounting:user_team_roles_settings', kwargs={'business_unit': self.kwargs['business_unit']})

    def form_valid(self, form):
        business_unit = models.BusinessUnit.objects.get(pk=self.kwargs['business_unit'])
        form.instance.business_unit = business_unit
        form.instance.hours_work = 20
        try:
            response = super(UserTeamRoleCreateView, self).form_valid(form)
            return response
        except:
            form.add_error(None, 'This user already has a role in this team.')
            return self.form_invalid(form)


class UserTeamRoleDeleteView(ManagerMixin, DeleteView):
    model = models.UserTeamRole
    template_name = 'accounting/user_team_role_delete_form.html'
    pk_url_kwarg = 'user_team_role'

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.role == 'MANAGER' and models.UserTeamRole.objects.filter(role='MANAGER', business_unit=self.object.business_unit).count() == 1:
            raise Http404()
        else:
            return super(UserTeamRoleDeleteView, self).delete(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('accounting:user_team_roles_settings', kwargs={'business_unit': self.kwargs['business_unit']})


class UserTeamRoleUpdateView(ManagerMixin, UpdateView):
    model = models.UserTeamRole
    form_class = forms.UserTeamRoleUpdateForm
    template_name = 'accounting/base_form.html'
    pk_url_kwarg = 'user_team_role'

    def get_success_url(self):
        return reverse_lazy('accounting:user_team_roles_settings', kwargs={'business_unit': self.kwargs['business_unit']})


class PayrollExpenseCreateView(ManagerMixin, CreateView):
    model = models.Expense
    form_class = forms.PayrollExpenseCreateForm
    template_name = 'accounting/base_form.html'
    pk_url_kwarg = 'expense'

    def get_initial(self):
        if 'month' in self.kwargs and 'year' in self.kwargs:
            date_payable = '{}/{}/{}'.format(self.kwargs['month'], monthrange(int(self.kwargs['year']), int(self.kwargs['month']))[1], self.kwargs['year'])
            return {
                'date_payable': date_payable
            }

    def get_context_data(self, *kwargs):
        context = super(PayrollExpenseCreateView, self).get_context_data()
        context['base_form_title'] = 'Payroll Expense'
        return context

    def get_success_url(self):
        return reverse_lazy('accounting:reconcile', kwargs={'business_unit': self.kwargs['business_unit']})

    def form_valid(self, form):
        business_unit = models.BusinessUnit.objects.get(pk=self.kwargs['business_unit'])
        form.instance.business_unit = business_unit
        form.instance.predicted_amount = form.instance.actual_amount
        form.instance.reconciled = True
        form.instance.expense_type = 'PAYROLL'
        form.instance.name = 'Payroll'
        form.instance.date_paid = form.instance.date_payable
        response = super(PayrollExpenseCreateView, self).form_valid(form)
        return response


class CashCreateView(ManagerMixin, CreateView):
    model = models.Cash
    form_class = forms.CashCreateForm
    template_name = 'accounting/base_form.html'

    def get_success_url(self):
        return reverse_lazy('accounting:reconcile', kwargs={'business_unit': self.kwargs['business_unit']})

    def get_context_data(self, *kwargs):
        context = super(CashCreateView, self).get_context_data()
        context['base_form_title'] = 'Cash Actual'
        return context

    def form_valid(self, form):
        business_unit = models.BusinessUnit.objects.get(pk=self.kwargs['business_unit'])
        year = int(self.kwargs['year'])
        month = int(self.kwargs['month'])
        days_in_month = monthrange(year, month)[1]

        date_associated = date(year, month, days_in_month)

        form.instance.business_unit = business_unit
        form.instance.predicted_amount = form.instance.actual_amount
        form.instance.reconciled = True
        form.instance.name = 'Cash'
        form.instance.date_associated = date_associated

        response = super(CashCreateView, self).form_valid(form)
        return response


class CashUpdateView(ManagerMixin, UpdateView):
    model = models.Cash
    form_class = forms.CashUpdateForm
    template_name = 'accounting/base_form.html'
    pk_url_kwarg = 'cash'

    def get_success_url(self):
        return reverse_lazy('accounting:reconcile', kwargs={'business_unit': self.kwargs['business_unit']})

    def get_context_data(self, *kwargs):
        context = super(CashUpdateView, self).get_context_data()
        context['base_form_title'] = 'Cash Actual'
        return context


def calculatePayrollProjectedAmount(current_business_unit):
    payroll_month_projected = Decimal('0.00')
    for partTime in models.PartTime.objects.filter(business_unit=current_business_unit):
        payroll_month_projected += partTime.hourly_amount * partTime.hours_work
    for fullTime in models.FullTime.objects.filter(business_unit=current_business_unit):
        payroll_month_projected += fullTime.salary_amount + fullTime.social_security_amount + fullTime.fed_health_insurance_amount + fullTime.retirement_amount + fullTime.medical_insurance_amount + fullTime.staff_benefits_amount + fullTime.fringe_amount
    return payroll_month_projected
