import json
from collections import OrderedDict
from datetime import date
from decimal import Decimal

from django.db.models import Sum, Value as V
from django.db.models.functions import Coalesce
from django.db.transaction import atomic
from django.contrib import messages
from django.contrib.humanize.templatetags.humanize import intcomma
from django.core.urlresolvers import reverse, reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import Http404
from django.shortcuts import redirect
from django.utils.functional import cached_property
from django.views.generic import TemplateView, CreateView, UpdateView, DeleteView

from accounting import models
from accounting import forms
from accounting.utils import Month


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

    @cached_property
    def fiscal_months(self):
        start = Month(self.fiscal_year, 7)
        end = Month(self.fiscal_year+1, 7)

        return Month.range(start, end)

    def get_monthly_invoices(self, date):
        # Although this call looks similar to the other queries, there may be multiple
        # invoices per month while the other models are an aggregate monthly balance.
        return models.Invoice.objects \
            .filter(business_unit=self.current_business_unit) \
            .exclude(contract__state=models.Contract.STATES.NEW) \
            .filter(date__year=date.year, date__month=date.month) \
            .aggregate(
                predicted=Coalesce(Sum('predicted_amount'), V(0)),
                actual=Coalesce(Sum('actual_amount'), V(0)))

    def get_monthly_expenses(self, date):
        return models.Expenses.objects \
            .filter(business_unit=self.current_business_unit) \
            .filter(year=date.year, month=date.month) \
            .aggregate(
                predicted=Coalesce(Sum('predicted_amount'), V(0)),
                actual=Coalesce(Sum('actual_amount'), V(0)))

    def get_monthly_ft_payroll(self, date):
        return models.FullTimePayroll.objects \
            .filter(business_unit=self.current_business_unit) \
            .filter(year=date.year, month=date.month) \
            .aggregate(
                predicted=Coalesce(Sum('predicted_amount'), V(0)),
                actual=Coalesce(Sum('actual_amount'), V(0)))

    def get_monthly_pt_payroll(self, date):
        return models.PartTimePayroll.objects \
            .filter(business_unit=self.current_business_unit) \
            .filter(year=date.year, month=date.month) \
            .aggregate(
                predicted=Coalesce(Sum('predicted_amount'), V(0)),
                actual=Coalesce(Sum('actual_amount'), V(0)))

    def get_monthly_cash_balance(self, date):
        # predicted values are calculated
        return models.CashBalance.objects \
            .filter(business_unit=self.current_business_unit) \
            .filter(year=date.year, month=date.month) \
            .aggregate(actual=Coalesce(Sum('actual_amount'), V(0)))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update({
            'next_url': reverse('accounting:dashboard', kwargs={'business_unit': self.current_business_unit.pk, 'fiscal_year': self.fiscal_year + 1}),
            'prev_url': reverse('accounting:dashboard', kwargs={'business_unit': self.current_business_unit.pk, 'fiscal_year': self.fiscal_year - 1}),
            'current_url': reverse('accounting:dashboard', kwargs={'business_unit': self.current_business_unit.pk}),
        })

        invoices = {m: self.get_monthly_invoices(m) for m in self.fiscal_months}
        expenses = {m: self.get_monthly_expenses(m) for m in self.fiscal_months}
        ft_payroll = {m: self.get_monthly_ft_payroll(m) for m in self.fiscal_months}
        pt_payroll = {m: self.get_monthly_pt_payroll(m) for m in self.fiscal_months}
        cash_balance = {m: self.get_monthly_cash_balance(m) for m in self.fiscal_months}

        # calculate the monthly predicted cash balance
        for month in self.fiscal_months:
            cash_balance[month]['predicted'] = invoices[month]['predicted'] - (
                expenses[month]['predicted'] +
                ft_payroll[month]['predicted'] +
                pt_payroll[month]['predicted']
            )

        dashboard_data = OrderedDict([
            ('Invoices', invoices),
            ('Expenses', expenses),
            ('Full-time Payroll', ft_payroll),
            ('Part-time Payroll', pt_payroll),
            ('Cash Balance', cash_balance),
        ])

        context['fiscal_months'] = self.fiscal_months
        context['month_names'] = [month.get_month_display() for month in self.fiscal_months]
        context['predicted_totals'] = json.dumps([cash_balance[m]['predicted'] for m in self.fiscal_months], cls=DecimalEncoder)
        context['actual_totals'] = json.dumps([cash_balance[m]['actual'] for m in self.fiscal_months], cls=DecimalEncoder)
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
                in models.Invoice.objects.filter(contract=contract).order_by('-date')
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
            messages.error(self.request, msg % (
                contract.contract_id,
                "$%s" % intcomma(contract.get_invoices_predicted_total()),
                "$%s" % intcomma(contract.amount),
            ))

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
