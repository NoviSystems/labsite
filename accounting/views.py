import json
from collections import OrderedDict
from datetime import date
from decimal import Decimal

from django.db.models import Sum, Value as V
from django.db.models.functions import Coalesce
from django.db.transaction import atomic
from django.contrib import messages
from django.core.urlresolvers import reverse, reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import Http404
from django.shortcuts import redirect
from django.utils.functional import cached_property
from django.utils.safestring import mark_safe
from django.views.generic import TemplateView, CreateView, UpdateView, DeleteView, FormView

from accounting import models
from accounting import forms
from accounting.utils import format_currency, Month, FiscalCalendar


class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return int(obj)
        return super(DecimalEncoder, self).default(obj)


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
    def fiscal_calendar(self):
        fiscal_year = self.kwargs.get('fiscal_year')

        # coerce to int
        if fiscal_year is not None:
            fiscal_year = int(fiscal_year)

        # try to determine from the last reconcile date
        else:
            latest = models.MonthlyReconcile.objects \
                .filter(business_unit=self.current_business_unit) \
                .order_by('-year', '-month').first()

            if latest is not None:
                latest_date = Month(latest).as_date()
                fiscal_year = FiscalCalendar.get_fiscal_year(latest_date)

        # if fiscal_year is none, will default to fiscal year for current date
        return FiscalCalendar(fiscal_year)

    @cached_property
    def fiscal_year(self):
        return self.fiscal_calendar.fiscal_year

    @cached_property
    def fiscal_months(self):
        return self.fiscal_calendar.months

    @cached_property
    def current_billing_month(self):
        """
        The current month to focus on for billing purposes. This will either be
        the next month to reconcile, or (if no months have been reconciled yet)
        the first month of this fiscal year.
        """
        latest = models.MonthlyReconcile.objects \
            .filter(business_unit=self.current_business_unit) \
            .order_by('-year', '-month').first()

        # get the next month
        if latest is not None:
            latest = Month(latest.year, latest.month)
            return Month.next(latest)

        # default to start of this fiscal year
        return Month(self.fiscal_calendar.start_date)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'business_units': self.business_units,
            'current_business_unit': self.current_business_unit,
            'fiscal_year': self.fiscal_year,
            'fiscal_start': self.fiscal_calendar.start_date,
            'fiscal_end': self.fiscal_calendar.end_date,
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

    def test_func(self):
        return self.is_manager


################################################################
# Dashboard Views                                              #
################################################################
class HomePageView(ViewerMixin, TemplateView):
    template_name = 'accounting/home.html'


class DashboardView(ViewerMixin, TemplateView):
    template_name = 'accounting/dashboard.html'

    def get_expected_monthly_invoices(self, date):
        # Although this call looks similar to the other queries, there may be multiple
        # invoices per month while the other models are an aggregate monthly balance.
        return models.Invoice.objects \
            .exclude(contract__state=models.Contract.STATES.NEW) \
            .filter(business_unit=self.current_business_unit) \
            .filter(expected_payment_date__year=date.year, expected_payment_date__month=date.month) \
            .aggregate(v=Coalesce(Sum('expected_amount'), V(0)))['v']

    def get_actual_monthly_invoices(self, date):
        # Although this call looks similar to the other queries, there may be multiple
        # invoices per month while the other models are an aggregate monthly balance.
        return models.Invoice.objects \
            .exclude(contract__state=models.Contract.STATES.NEW) \
            .filter(business_unit=self.current_business_unit) \
            .filter(actual_payment_date__year=date.year, actual_payment_date__month=date.month) \
            .aggregate(v=Coalesce(Sum('actual_amount'), V(0)))['v']

    def get_monthly_invoices(self, date):
        return {
            'expected_amount': self.get_expected_monthly_invoices(date),
            'actual_amount': self.get_actual_monthly_invoices(date),
        }

    def get_monthly_instance(self, model, date):
        try:
            return model.objects \
                .filter(business_unit=self.current_business_unit) \
                .filter(year=date.year, month=date.month).get()
        except model.DoesNotExist:
            return model(
                business_unit=self.current_business_unit,
                year=date.year, month=date.month)

    def get_balances(self):
        # get instances
        invoices = [self.get_monthly_invoices(month) for month in self.fiscal_months]  # alreaady in dict form
        expenses = [self.get_monthly_instance(models.Expenses, month) for month in self.fiscal_months]
        ft_payroll = [self.get_monthly_instance(models.FullTimePayroll, month) for month in self.fiscal_months]
        pt_payroll = [self.get_monthly_instance(models.PartTimePayroll, month) for month in self.fiscal_months]
        cash_balance = [self.get_monthly_instance(models.CashBalance, month) for month in self.fiscal_months]

        # avoid executing duplicate query for expected cash balance calculation.
        for i, _ in enumerate(self.fiscal_months):
            cash_balance[i].expenses = expenses[i]
            cash_balance[i].fulltime_payroll = ft_payroll[i]
            cash_balance[i].parttime_payroll = pt_payroll[i]

            if i > 0:
                cash_balance[i].previous_cashbalance = cash_balance[i - 1]

        # create dictionaries
        return OrderedDict([
            ('Invoices', invoices),
            ('Expenses', expenses),
            ('Full-time Payroll', ft_payroll),
            ('Part-time Payroll', pt_payroll),
            ('Cash Balance', cash_balance),
        ])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        balances = self.get_balances()
        cash_balances = balances['Cash Balance']

        context.update({
            'next_url': reverse('accounting:dashboard', kwargs={'business_unit': self.current_business_unit.pk, 'fiscal_year': self.fiscal_year + 1}),
            'prev_url': reverse('accounting:dashboard', kwargs={'business_unit': self.current_business_unit.pk, 'fiscal_year': self.fiscal_year - 1}),
            'current_url': reverse('accounting:dashboard', kwargs={'business_unit': self.current_business_unit.pk}),

            'billing_month': self.current_billing_month,
            'fiscal_months': self.fiscal_months,
            'balances': balances,
            'expected_totals': json.dumps([balance.expected_amount for balance in cash_balances], cls=DecimalEncoder),
            'actual_totals': json.dumps([balance.actual_amount for balance in cash_balances], cls=DecimalEncoder),
        })

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
                in models.Invoice.objects.filter(contract=contract).order_by('-expected_invoice_date')
            ],
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

    def post(self, *args, **kwargs):
        activate = self.request.POST.get('activate')
        complete = self.request.POST.get('complete')
        delete = self.request.POST.get('delete')

        if activate is not None:
            instance = models.Contract.objects.get(pk=activate)
            self.activate(instance)

        elif complete is not None:
            instance = models.Contract.objects.get(pk=complete)
            self.complete(instance)

        elif delete is not None:
            instance = models.Contract.objects.get(pk=delete)
            self.delete(instance)

        return redirect('accounting:contracts', business_unit=self.current_business_unit.pk)

    def activate(self, contract):
        if not contract.has_invoice():
            msg = "Contract %s not activated. Activation requires at least one invoice."
            messages.error(self.request, msg % contract.contract_id)

        elif not contract.amount_matches_invoices():
            msg = "Contract %s not activated. Sum of invoice amounts (%s) do not equal contract amount (%s)."
            messages.error(self.request, mark_safe(msg % (
                contract.contract_id,
                format_currency(contract.get_invoices_expected_total()),
                format_currency(contract.amount),
            )))

        else:
            contract.activate()
            contract.save()

    def complete(self, contract):
        if not contract.all_invoices_received():
            msg = "Contract %s not completed. Contract has unreceived invoices."
            messages.error(self.request, msg % contract.contract_id)

        else:
            contract.complete()
            contract.save()

    def delete(self, contract):
        if contract.state != contract.STATES.NEW:
            msg = "Contract %s not deleted. Cannot delete active/completed contracts."
            messages.error(self.request, msg % contract.contract_id)

        else:
            contract.delete()


class RevenueView(ViewerMixin, TemplateView):
    template_name = 'accounting/revenue.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        invoices = models.Invoice.objects.filter(contract__business_unit=self.current_business_unit)
        context['invoices'] = invoices
        return context


class MonthlyReconcileView(ViewerMixin, FormView):
    template_name = 'accounting/monthly_reconcile.html'
    form_class = forms.MonthlyBalanceForm
    success_url_name = 'accounting:reconcile'

    def get_success_url_kwargs(self):
        kwargs = super().get_success_url_kwargs()
        if 'fiscal_year' in self.kwargs:
            kwargs['fiscal_year'] = self.kwargs['fiscal_year']

        return kwargs

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'business_unit': self.current_business_unit,
            'billing_month': self.current_billing_month,
            'fiscal_months': self.fiscal_months,
        })
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'next_url': reverse('accounting:reconcile', kwargs={'business_unit': self.current_business_unit.pk, 'fiscal_year': self.fiscal_year + 1}),
            'prev_url': reverse('accounting:reconcile', kwargs={'business_unit': self.current_business_unit.pk, 'fiscal_year': self.fiscal_year - 1}),
            'current_url': reverse('accounting:reconcile', kwargs={'business_unit': self.current_business_unit.pk}),
            'billing_prefix': '%d_%02d' % (self.current_billing_month.year, self.current_billing_month.month, )
        })
        return context

    def post(self, request, *args, **kwargs):
        self.reconciling = 'reconcile' in self.request.POST
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        response = self.check_reconcile(form)
        if response is not None:
            return response

        form.save()
        return super().form_valid(form)

    def form_invalid(self, form):
        response = self.check_reconcile(form)
        if response is not None:
            return response

        return super().form_invalid(form)

    def check_reconcile(self, form):
        if not self.reconciling:
            return

        month = self.current_billing_month
        data = {'month': month.month, 'year': month.year, 'business_unit': self.current_business_unit.pk}
        reconcile_form = forms.MonthlyReconcileForm(dirty=form.has_changed(), data=data)

        if reconcile_form.is_valid():
            reconcile_form.save()
            messages.success(self.request, '%s %d has been reconciled.' % (month.get_month_display(), month.year))
            return super().form_valid(form)

        for _, errors in reconcile_form.errors.items():
            for error in errors:
                messages.error(self.request, error)

        return super().form_invalid(form)


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

    def form_valid(self, form):
        response = super(BusinessUnitCreateView, self).form_valid(form)
        models.UserTeamRole.objects.create(user=self.request.user, business_unit=form.instance, role='MANAGER')
        return response

    def get_success_url(self):
        return reverse('accounting:dashboard', kwargs={'business_unit': self.object.pk})


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

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['contract'] = self.current_contract

        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cancel_url'] = self.get_success_url()

        return context


class InvoiceCreateView(InvoiceMixin, CreateView):
    template_name = 'accounting/base_form.html'
    form_class = forms.InvoiceCreateForm


class InvoiceUpdateView(InvoiceMixin, UpdateView):
    template_name = 'accounting/base_form.html'

    def get_form_class(self):
        STATES = models.Contract.STATES

        return {
            STATES.NEW: forms.NewInvoiceUpdateForm,
            STATES.ACTIVE: forms.ActiveInvoiceUpdateForm,
        }[self.current_contract.state]


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
