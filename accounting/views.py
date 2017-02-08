from datetime import date
from dateutil.rrule import rrule, MONTHLY
from calendar import monthrange
from decimal import Decimal

from django.db.models import Max, Sum
from django.db.transaction import atomic
from django.contrib import messages
from django.contrib.humanize.templatetags.humanize import intcomma
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse, reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import Http404
from django.shortcuts import redirect
from django.utils.functional import cached_property
from django.views.generic import TemplateView, CreateView, UpdateView, DeleteView

from accounting import models
from accounting import forms


class AccountingMixin(LoginRequiredMixin):
    """
    Common setup required for most accounting views.
    """
    success_url_name = None

    @atomic
    def dispatch(self, request, *args, **kwargs):
        return super(AccountingMixin, self).dispatch(request, *args, **kwargs)

    def get_fiscal_year(self, calendar_date):
        calendar_year = calendar_date.year

        # if we're in the first half of the calendar year, then we're in the previous fiscal year
        if calendar_date < date(calendar_year, 7, 1):
            return calendar_year - 1
        return calendar_year

    def get_object_fiscal_year(self):
        pass

    @cached_property
    def user(self):
        return self.request.user

    @cached_property
    def team_role(self):
        try:
            return models.UserTeamRole.objects.get(user=self.user, business_unit=self.current_business_unit)
        except models.UserTeamRole.DoesNotExist:
            return None

    @cached_property
    def is_manager(self):
        if self.user.is_superuser:
            return True

        if self.team_role is None:
            return False

        ROLES = models.UserTeamRole.ROLES
        return self.team_role.role == ROLES.MANAGER

    @cached_property
    def business_units(self):
        return self.user.business_units.all()

    @cached_property
    def current_business_unit(self):
        pk = self.kwargs.get('business_unit', None)

        if pk is None:
            return None
        return models.BusinessUnit.objects.get(pk=pk)

    @cached_property
    def fiscal_year(self):
        return self.kwargs.get('fiscal_year', self.get_fiscal_year(date.today()))

    @cached_property
    def fiscal_start(self):
        return date(self.fiscal_year, 7, 1)

    @cached_property
    def fiscal_end(self):
        return date(self.fiscal_year+1, 6, 30)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'business_units': self.business_units,
            'current_business_unit': self.current_business_unit,
            'fiscal_year': self.fiscal_year,
            'fiscal_start': self.fiscal_start,
            'fiscal_end': self.fiscal_end,
            'is_manager': self.is_manager,
        })

        return context

    def get_success_url_kwargs(self):
        return {
            'business_unit': self.current_business_unit.pk
        }

    def get_success_url(self):
        if self.success_url_name is None:
            return super().get_success_url()
        return reverse(self.success_url_name, kwargs=self.get_success_url_kwargs())


class ViewerMixin(AccountingMixin, UserPassesTestMixin):
    """
    View requires 'view' permissions
    """
    raise_exception = True

    def test_func(self):
        if self.is_manager:
            return True

        if self.team_role is not None:
            ROLES = models.UserTeamRole.ROLES
            if self.team_role.role == ROLES.VIEWER:
                return True
        return False


class ManagerMixin(AccountingMixin, UserPassesTestMixin):
    """
    View requires 'edit' permissions
    """
    raise_exception = True

    def test_func(self):
        return self.is_manager


################################################################
# Dashboard Views                                              #
################################################################
class HomePageView(ViewerMixin, TemplateView):
    template_name = 'accounting/home.html'


class DashboardView(ViewerMixin, TemplateView):
    template_name = 'accounting/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update({
            'next_url': reverse('accounting:dashboard', kwargs={'business_unit': self.current_business_unit.pk, 'fiscal_year': self.fiscal_year + 1}),
            'prev_url': reverse('accounting:dashboard', kwargs={'business_unit': self.current_business_unit.pk, 'fiscal_year': self.fiscal_year - 1}),
            'current_url': reverse('accounting:dashboard', kwargs={'business_unit': self.current_business_unit.pk}),
        })

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


class ContractsView(ViewerMixin, TemplateView):
    template_name = 'accounting/contracts.html'

    def contract_url_kwargs(self, contract):
        return {
            'business_unit': self.current_business_unit.pk,
            'contract': contract.pk
        }

    def invoice_url_kwargs(self, invoice):
        kwargs = self.contract_url_kwargs(invoice.contract)
        kwargs['invoice'] = invoice.pk

        return kwargs

    def make_contract_context(self, contract):
        return {
            'contract': contract,
            'invoices': [
                self.make_invoice_context(invoice) for invoice
                in models.Invoice.objects.filter(contract=contract).order_by('-year', '-month')
            ],
            'delete_url': reverse('accounting:delete_contract', kwargs=self.contract_url_kwargs(contract)),
            'update_url': reverse('accounting:update_contract', kwargs=self.contract_url_kwargs(contract)),
            'invoice_url': reverse('accounting:create_invoice', kwargs=self.contract_url_kwargs(contract)),
        }

    def make_invoice_context(self, invoice):
        return {
            'invoice': invoice,
            'delete_url': reverse('accounting:delete_invoice', kwargs=self.invoice_url_kwargs(invoice)),
            'update_url': reverse('accounting:update_invoice', kwargs=self.invoice_url_kwargs(invoice)),
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        contracts = models.Contract.objects \
            .filter(business_unit=self.current_business_unit) \
            .order_by('-start_date')

        STATES = models.Contract.STATES
        context.update({
            'has_contracts': contracts.exists(),
            'new_contracts': [
                self.make_contract_context(contract) for contract
                in contracts.filter(state=STATES.NEW)
            ],
            'active_contracts': [
                self.make_contract_context(contract) for contract
                in contracts.filter(state=STATES.ACTIVE)
            ],
            'completed_contracts': [
                self.make_contract_context(contract) for contract
                in contracts.filter(state=STATES.COMPLETE)
            ],
        })

        return context


class RevenueView(ViewerMixin, TemplateView):
    template_name = 'accounting/revenue.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        invoices = models.Invoice.objects.filter(contract__business_unit=self.current_business_unit)
        context['invoices'] = invoices
        return context


class MonthlyReconcileView(ViewerMixin, TemplateView):
    template_name = 'accounting/monthly_reconcile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update({
            'next_url': reverse('accounting:reconcile', kwargs={'business_unit': self.current_business_unit.pk, 'fiscal_year': self.fiscal_year + 1}),
            'prev_url': reverse('accounting:reconcile', kwargs={'business_unit': self.current_business_unit.pk, 'fiscal_year': self.fiscal_year - 1}),
            'current_url': reverse('accounting:reconcile', kwargs={'business_unit': self.current_business_unit.pk}),
        })

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
        context = super().get_context_data(**kwargs)
        users = models.UserTeamRole.objects.filter(business_unit=self.current_business_unit)
        viewers = [user for user in users if user.role == 'VIEWER']
        managers = [user for user in users if user.role == 'MANAGER']
        context['viewers'] = viewers
        context['managers'] = managers
        return context


class UserTeamRolesSettingsPageView(ManagerMixin, TemplateView):
    template_name = 'accounting/settings/user_team_roles.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        users = models.UserTeamRole.objects.filter(business_unit=self.current_business_unit)
        viewers = [user for user in users if user.role == 'VIEWER']
        managers = [user for user in users if user.role == 'MANAGER']
        context['viewers'] = viewers
        context['managers'] = managers
        return context


################################################################
# Business Units                                               #
################################################################
class BusinessUnitCreateView(AccountingMixin, CreateView):
    model = models.BusinessUnit
    form_class = forms.BusinessUnitForm
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
    form_class = forms.BusinessUnitForm
    template_name = 'accounting/base_form.html'
    pk_url_kwarg = 'business_unit'

    def get_success_url(self):
        return reverse_lazy('accounting:business_unit_settings', kwargs={'business_unit': self.kwargs['business_unit']})


################################################################
# Contracts                                                    #
################################################################
class ContractMixin(ManagerMixin):
    model = models.Contract
    pk_url_kwarg = 'contract'
    success_url_name = 'accounting:contracts'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cancel_url'] = self.get_success_url()

        return context


class ContractCreateView(ContractMixin, CreateView):
    template_name = 'accounting/base_form.html'
    form_class = forms.ContractForm

    def form_valid(self, form):
        form.instance.business_unit = self.current_business_unit

        return super(ContractCreateView, self).form_valid(form)


class ContractUpdateView(ContractMixin, UpdateView):
    template_name = 'accounting/base_form.html'
    form_class = forms.ContractForm


class ContractDeleteView(ContractMixin, DeleteView):
    template_name = 'accounting/base_delete_form.html'


################################################################
# Invoices                                                     #
################################################################
class InvoiceMixin(ManagerMixin):
    model = models.Invoice
    pk_url_kwarg = 'invoice'
    success_url_name = 'accounting:contracts'

    @cached_property
    def current_contract(self):
        pk = self.kwargs.get('contract', None)

        if pk is None:
            return None
        return models.Contract.objects.get(pk=pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cancel_url'] = self.get_success_url()

        return context


class InvoiceCreateView(InvoiceMixin, CreateView):
    template_name = 'accounting/base_form.html'
    form_class = forms.InvoiceForm

    def form_valid(self, form):
        form.instance.business_unit = self.current_business_unit
        form.instance.contract = self.current_contract

        return super().form_valid(form)


class InvoiceUpdateView(InvoiceMixin, UpdateView):
    template_name = 'accounting/base_form.html'
    form_class = forms.InvoiceForm

    def form_valid(self, form):
        form.instance.business_unit = self.current_business_unit
        form.instance.contract = self.current_contract

        return super().form_valid(form)


class InvoiceDeleteView(InvoiceMixin, DeleteView):
    template_name = 'accounting/base_delete_form.html'


################################################################
# User Team Roles                                              #
################################################################
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


def calculatePayrollProjectedAmount(current_business_unit):
    payroll_month_projected = Decimal('0.00')
    for partTime in models.PartTime.objects.filter(business_unit=current_business_unit):
        payroll_month_projected += partTime.hourly_amount * partTime.hours_work
    for fullTime in models.FullTime.objects.filter(business_unit=current_business_unit):
        payroll_month_projected += fullTime.salary_amount + fullTime.social_security_amount + fullTime.fed_health_insurance_amount + fullTime.retirement_amount + fullTime.medical_insurance_amount + fullTime.staff_benefits_amount + fullTime.fringe_amount
    return payroll_month_projected
