import json
from datetime import date, datetime
from dateutil.rrule import rrule, MONTHLY

from django.shortcuts import redirect
from django.db.models import Max
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import Http404
from django.views.generic import TemplateView, CreateView, UpdateView, DeleteView

from models import *
from forms import *
from decimal import Decimal
from calendar import monthrange


class PermissionsMixin(LoginRequiredMixin, object):

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated():
            try:
                self.team_roles = UserTeamRole.objects.filter(user=self.request.user)
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
    
    def dispatch(self, request, *args, **kwargs):
        self.current_business_unit = BusinessUnit.objects.get(pk=kwargs['business_unit'])
        self.now = date.today()
        return super(SetUpMixin, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super(SetUpMixin, self).get_context_data(*args, **kwargs)
        try:
            context['is_viewer'] = self.is_viewer
        except AttributeError:
            context['is_viewer'] = False
        context['current_business_unit'] = self.current_business_unit
        return context


class ViewerMixin(SetUpMixin, PermissionsMixin, UserPassesTestMixin):

    def test_func(self):
        try:
            bu_role = UserTeamRole.objects.get(user=self.request.user, business_unit=self.current_business_unit).role
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
            bu_role = UserTeamRole.objects.get(user=self.request.user, business_unit=self.current_business_unit).role
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
        cma = { 'title': 'Cash Month Actual', 'values': {} }
        cmpr = { 'title': 'Cash Month Projected', 'values': {} }
        ema = { 'title': 'Expenses Month Actual', 'values': {} }
        emp = { 'title': 'Expenses Month Projected', 'values': {} }
        ima = { 'title': 'Receivables Month Actual', 'values': {} }
        imp = { 'title': 'Receivables Month Projected', 'values': {} }
        pma = { 'title': 'Payroll Month Actual', 'values': {} }
        pmp = { 'title': 'Payroll Month Projected', 'values': {} }
        tama = { 'title': 'Total Assets Projected', 'values': {} }
        tamp = { 'title': 'Total Assets Actual', 'values': {} }

        start_year = None
        end_year = None
        if 'start_year' in self.kwargs and 'end_year' in self.kwargs:
            start_year = date(int(self.kwargs['start_year']), 07, 01)
            end_year = date(int(self.kwargs['end_year']), 06, 30)
        else:
            start_year = date(datetime.now().year, 07, 1)
            end_year = date(datetime.now().year+1, 06, 30)

        months = [month for month in rrule(MONTHLY, dtstart=start_year, until=end_year)]
        month_names = []

        cash_month_actual = self.current_business_unit.cash
        cash_month_projected = self.current_business_unit.cash

        for month in months:

            start_date = '{}-{}-{}'.format(month.year, month.month, '01')
            end_date = '{}-{}-{}'.format(month.year, month.month, monthrange(month.year, month.month)[1])

            month_name = month.strftime("%B") 
            month_names.append(month_name)

            payroll_month_actual = Decimal('0.00')
            payroll_month_projected = Decimal('0.00') 
            for payroll in Payroll.objects.filter(expense__business_unit=self.current_business_unit, expense__date_payable__range=[start_date, end_date]):
                if payroll.expense.reconciled:
                    payroll_month_actual += payroll.expense.actual_amount
                payroll_month_projected += payroll.expense.predicted_amount
            pma['values'][month_name] = payroll_month_actual
            pmp['values'][month_name] = payroll_month_projected

            expenses_month_actual = Decimal('0.00')
            expenses_month_projected = Decimal('0.00')
            for expense in Expense.objects.filter(business_unit=self.current_business_unit, date_payable__range=[start_date, end_date]):
                if expense.reconciled:
                    expenses_month_actual += expense.actual_amount
                expense_month_projected += expense.predicted_amount
            expenses_month_actual -= payroll_month_actual
            expenses_month_projected -= payroll_month_projected
            ema['values'][month_name] = expenses_month_actual
            emp['values'][month_name] = expenses_month_projected

            income_month_actual = Decimal('0.00')
            income_month_projected = Decimal('0.00')
            for income in Income.objects.filter(business_unit=self.current_business_unit, date_payable__range=[start_date, end_date]):
                if income.reconciled:
                    income_month_actual += income.actual_amount
                income_month_projected += income.predicted_amount
            ima['values'][month_name] = income_month_actual
            imp['values'][month_name] = income_month_projected
            
            cash_month_actual +=  (income_month_actual - payroll_month_actual - expenses_month_actual)
            cash_month_projected += (income_month_projected - payroll_month_projected - expenses_month_projected)

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
            total_assets_month_actual = cash_month_actual + income_booked_actual
            tama['values'][month_name] = total_assets_month_actual

        dashboard_data = [cma, cmpr, ema, emp, ima, imp, pma, pmp, tama, tamp]
        context['month_names'] = month_names
        context['predicted_totals'] = json.dumps([float(cmpr['values'][month_name]) for month_name in month_names])
        context['actual_totals'] = json.dumps([float(cma['values'][month_name]) for month_name in month_names])
        context['dashboard_data'] = dashboard_data
        
        context['start_year'] = start_year.year
        context['end_year'] = end_year.year
        return context


'''class DashboardMonthView(DashboardView):
    template_name = 'accounting/dashboard_month.html'

    def get_context_data(self, **kwargs):
        context = super(DashboardMonthView, self).get_context_data(**kwargs)
        month_data = {
            'month': Month.objects.get(pk=kwargs['month']),
        }
        context['month_data'] = month_data

        index = list(context['months']).index(month_data['month'])

        # calculate month_values per index
        context['month_cma'] = context['cma']['values'][index]
        context['month_cmpr_pre'] = context['cmpr']['values'][index - 1]

        context['expenses'] = Expense.objects.filter(month=kwargs['month'])
        context['payrolls'] = Payroll.objects.filter(month=kwargs['month'])

        context['month_cmpr'] = context['cmpr']['values'][index]
        context['month_ima'] = context['ima']['values'][index]
        context['month_imp'] = context['imp']['values'][index]
        context['month_ema'] = context['ema']['values'][index]
        context['month_emp'] = context['emp']['values'][index]
        context['month_pmp'] = context['pmp']['values'][index]
        context['month_pma'] = context['pma']['values'][index]
        context['month_tama'] = context['tama']['values'][index]
        context['month_tamp'] = context['tamp']['values'][index]

        full_time = FullTime.objects.filter(business_unit=self.current_business_unit)
        context['full_time'] = full_time

        part_time = PartTime.objects.filter(business_unit=self.current_business_unit)
        context['part_time'] = part_time

        # part time amounts
        part_time_hours_total = 0
        part_time_total = Decimal('0.00')

        # full time amounts
        monthly_amount = Decimal('0.00')
        social_security_total = Decimal('0.00')
        fed_health_insurance_total = Decimal('0.00')
        retirement_total = Decimal('0.00')
        medical_insurance_total = Decimal('0.00')
        staff_benefits_total = Decimal('0.00')
        fringe_total = Decimal('0.00')

        for part_time in PartTime.objects.filter(business_unit=self.current_business_unit):
            part_time_hours_total += part_time.hours_work
            part_time_total += (part_time.hours_work * part_time.hourly_amount)

        # find full time totals for each type
        for full_time in FullTime.objects.filter(business_unit=self.current_business_unit):
            monthly_amount = (full_time.salary_amount / 12)
            social_security_total += full_time.social_security_amount
            fed_health_insurance_total += full_time.fed_health_insurance_amount
            retirement_total += full_time.retirement_amount
            medical_insurance_total += full_time.medical_insurance_amount
            staff_benefits_total += full_time.staff_benefits_amount
            fringe_total += full_time.fringe_amount

        context['ssa'] = social_security_total
        context['fhit'] = fed_health_insurance_total
        context['rt'] = retirement_total
        context['mit'] = medical_insurance_total
        context['sbt'] = staff_benefits_total
        context['ft'] = fringe_total

        context['ptht'] = part_time_hours_total
        context['ptt'] = part_time_total

        return context'''

class ContractsView(ViewerMixin, SetUpMixin, TemplateView):
    template_name = 'accounting/contracts.html'

    def get_context_data(self, **kwargs):
        context = super(ContractsView, self).get_context_data()
        contracts = Contract.objects.filter(business_unit=self.current_business_unit)
        completed_contracts = []
        active_contracts = []
        for contract in contracts:
            if contract.contract_state == 'ACTIVE':
                invoices = Invoice.objects.filter(contract=contract).order_by('date_payable')
                active_contracts.extend([
                    {
                        'contract': contract,
                        'invoices': invoices,
                    }
                ])
            elif contract.contract_state == 'COMPLETE':
                invoices = Invoice.objects.filter(contract=contract)
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
        invoices = Invoice.objects.filter(contract__business_unit=self.current_business_unit)
        context['invoices'] = invoices
        return context


class ExpensesView(ViewerMixin, SetUpMixin, TemplateView):
    template_name = 'accounting/expenses.html'

    def get_context_data(self, **kwargs):
        context = super(ExpensesView, self).get_context_data()

        ''' month_data = []

        if 'month' in self.kwargs:
            display_month = Month.objects.get(pk=self.kwargs['month'])
        else:
            display_month = self.current_month

        try:
            cash = Cash.objects.get(month=display_month)
        except ObjectDoesNotExist:
            cash = None
        month_data = {
            'month': display_month,
            'expenses': Expense.objects.filter(month=display_month),
            'incomes': Income.objects.filter(month=display_month),
            'cash': cash
        }

        context['month_data'] = month_data'''
        return context


class BusinessUnitSettingsPageView(ManagerMixin, TemplateView):
    template_name = 'accounting/settings/business_unit.html'

    def get_context_data(self, **kwargs):
        context = super(BusinessUnitSettingsPageView, self).get_context_data()
        users = UserTeamRole.objects.filter(business_unit=self.current_business_unit)
        viewers = [user for user in users if user.role == 'VIEWER']
        managers = [user for user in users if user.role == 'MANAGER']
        context['viewers'] = viewers
        context['managers'] = managers
        return context


class UserTeamRolesSettingsPageView(ManagerMixin, TemplateView):
    template_name = 'accounting/settings/user_team_roles.html'

    def get_context_data(self, **kwargs):
        context = super(UserTeamRolesSettingsPageView, self).get_context_data()
        users = UserTeamRole.objects.filter(business_unit=self.current_business_unit)
        viewers = [user for user in users if user.role == 'VIEWER']
        managers = [user for user in users if user.role == 'MANAGER']
        context['viewers'] = viewers
        context['managers'] = managers
        return context


class BusinessUnitCreateView(LoginRequiredMixin, CreateView):
    model = BusinessUnit
    form_class = BusinessUnitCreateForm
    template_name = 'accounting/base_form.html'
    success_url = reverse_lazy('accounting:home')

    def form_valid(self, form):
        response = super(BusinessUnitCreateView, self).form_valid(form)
        UserTeamRole.objects.create(user=self.request.user, business_unit=form.instance, role='MANAGER')
        return response


class BusinessUnitDeleteView(ManagerMixin, DeleteView):
    model = BusinessUnit
    template_name = 'accounting/base_delete_form.html'
    success_url = reverse_lazy('accounting:home')

    def get_object(self):
        return BusinessUnit.objects.get(pk=self.kwargs['business_unit'])


class BusinessUnitUpdateView(ManagerMixin, UpdateView):
    model = BusinessUnit
    form_class = BusinessUnitUpdateForm
    template_name = 'accounting/base_form.html'

    def get_object(self):
        return BusinessUnit.objects.get(pk=self.kwargs['business_unit'])

    def get_success_url(self):
        return reverse_lazy('accounting:business_unit_settings', kwargs={'business_unit': self.kwargs['business_unit']})


class ContractCreateView(ManagerMixin, CreateView):
    model = Contract
    form_class = ContractCreateForm
    template_name = 'accounting/base_form.html'

    def get_success_url(self):
        return reverse_lazy('accounting:contracts', kwargs=self.kwargs)

    def form_valid(self, form):
        business_unit = BusinessUnit.objects.get(pk=self.kwargs['business_unit'])
        form.instance.business_unit = business_unit
        max_contract_number = Contract.objects.filter(business_unit=business_unit).aggregate(Max('contract_number'))
        if not max_contract_number['contract_number__max']:
            form.instance.contract_number = 1
        else:
            form.instance.contract_number = max_contract_number['contract_number__max'] + 1

        return super(ContractCreateView, self).form_valid(form)


class ContractDeleteView(ManagerMixin, DeleteView):
    model = Contract
    template_name = 'accounting/base_delete_form.html'

    def get_object(self):
        return Contract.objects.get(pk=self.kwargs['contract'])

    def get_success_url(self):
        return reverse_lazy('accounting:contracts', kwargs={'business_unit': self.kwargs['business_unit']})


class ContractUpdateView(ManagerMixin, UpdateView):
    model = Contract
    form_class = ContractUpdateForm
    template_name = 'accounting/base_form.html'

    def get_object(self):
        return Contract.objects.get(pk=self.kwargs['contract'])

    def get_success_url(self):
        return reverse_lazy('accounting:contracts', kwargs={'business_unit': self.kwargs['business_unit']})


class InvoiceCreateView(ManagerMixin, CreateView):
    model = Invoice
    form_class = InvoiceCreateForm
    template_name = 'accounting/base_form.html'

    def get_success_url(self):
        return reverse_lazy('accounting:contracts', kwargs={'business_unit': self.kwargs['business_unit']})

    def form_valid(self, form):
        contract = Contract.objects.get(pk=self.kwargs['contract'])
        form.instance.contract = contract
        max_invoice_number = Invoice.objects.filter(contract=contract).aggregate(Max('number'))
        if not max_invoice_number['number__max']:
            form.instance.number = 1
        else:
            form.instance.number = max_invoice_number['number__max'] + 1
        form.instance.transition_state = 'NOT_INVOICED'
        business_unit = BusinessUnit.objects.get(pk=self.kwargs['business_unit'])
        form.instance.business_unit = business_unit
        contract_number = str(form.instance.contract.contract_number)
        contract_number = contract_number.zfill(4)
        form.instance.name = form.instance.contract.department + contract_number + '-' + str(form.instance.number)

        response = super(InvoiceCreateView, self).form_valid(form)
        return response


class InvoiceDeleteView(ManagerMixin, DeleteView):
    model = Invoice
    template_name = 'accounting/base_delete_form.html'

    def get_object(self):
        return Invoice.objects.get(pk=self.kwargs['invoice'])

    def get_success_url(self):
        return reverse_lazy('accounting:contracts', kwargs={'business_unit': self.kwargs['business_unit']})


class InvoiceUpdateView(ManagerMixin, UpdateView):
    model = Invoice
    form_class = InvoiceUpdateForm
    template_name = 'accounting/base_form.html'

    def get_object(self):
        return Invoice.objects.get(pk=self.kwargs['invoice'])

    def get_success_url(self):
        return reverse_lazy('accounting:contracts', kwargs={'business_unit': self.kwargs['business_unit']})


class ExpenseCreateView(ManagerMixin, CreateView):
    model = Expense
    form_class = ExpenseCreateForm
    template_name = 'accounting/base_form.html'

    def get_success_url(self):
        return reverse_lazy('accounting:expenses', kwargs={'business_unit': self.kwargs['business_unit']})

    def form_valid(self, form):
        business_unit = BusinessUnit.objects.get(pk=self.kwargs['business_unit'])
        form.instance.business_unit = business_unit
        try:
            if self.request.POST['recurring']:
                monthly_expense_dates = [monthly_date for monthly_date in rrule(MONTHLY, dtstart=form.instance.date_payable, until=date(2017, 06, 30))]
                for expense_date in monthly_expense_dates:
                    expense = Expense(
                        business_unit=form.instance.business_unit,
                        predicted_amount=form.instance.predicted_amount,
                        name=form.instance.name,
                        date_payable=expense_date,
                    )
                    if expense_date < self.now:
                        expense.date_paid = expense_date
                        expense.actual_amount = form.instance.predicted_amount
                    expense.save()
                return redirect('accounting:expenses', pk=self.kwargs['pk'])
        except KeyError:
            if form.instance.date_payable < self.now:
                form.instance.date_paid = form.instance.date_payable
                form.instance.actual_amount = form.instance.predicted_amount

            response = super(ExpenseCreateView, self).form_valid(form)
            return response


class ExpenseDeleteView(ManagerMixin, DeleteView):
    model = Expense
    template_name = 'accounting/base_delete_form.html'

    def get_object(self):
        return Expense.objects.get(pk=self.kwargs['expense'])

    def get_success_url(self):
        return reverse_lazy('accounting:expenses', kwargs={'business_unit': self.kwargs['business_unit']})


class ExpenseUpdateView(ManagerMixin, UpdateView):
    model = Expense
    form_class = ExpenseUpdateForm
    template_name = 'accounting/base_form.html'

    def get_object(self):
        return Expense.objects.get(pk=self.kwargs['expense'])

    def get_success_url(self):
        return reverse_lazy('accounting:expenses', kwargs={'business_unit': self.kwargs['business_unit']})


class IncomeCreateView(ManagerMixin, CreateView):
    model = Income
    form_class = IncomeCreateForm
    template_name = 'accounting/base_form.html'

    def get_success_url(self):
        return reverse_lazy('accounting:expenses', kwargs={'business_unit': self.kwargs['business_unit']})

    def form_valid(self, form):
        form.instance.business_unit = BusinessUnit.objects.get(pk=self.kwargs['business_unit'])
        try:
            if self.request.POST['recurring']:
                monthly_income_dates = [monthly_date for monthly_date in rrule(MONTHLY, dtstart=form.instance.date_payable, until=date(2017, 06, 30))]
                for income_date in monthly_income_dates:
                    income = Income(
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
    model = Income
    template_name = 'accounting/base_delete_form.html'

    def get_object(self):
        return Income.objects.get(pk=self.kwargs['income'])

    def get_success_url(self):
        return reverse_lazy('accounting:expenses', kwargs={'business_unit': self.kwargs['business_unit']})


class IncomeUpdateView(ManagerMixin, UpdateView):
    model = Income
    form_class = IncomeUpdateForm
    template_name = 'accounting/base_form.html'

    def get_object(self):
        return Income.objects.get(pk=self.kwargs['income'])

    def get_success_url(self):
        return reverse_lazy('accounting:expenses', kwargs={'business_unit': self.kwargs['business_unit']})


class PersonnelView(ViewerMixin, TemplateView):
    template_name = 'accounting/personnel.html'

    def get_context_data(self, **kwargs):
        context = super(PersonnelView, self).get_context_data()

        full_time = FullTime.objects.filter(business_unit=self.current_business_unit)
        context['full_time'] = full_time

        part_time = PartTime.objects.filter(business_unit=self.current_business_unit)
        context['part_time'] = part_time

        return context


class FullTimeCreateView(ManagerMixin, CreateView):
    model = FullTime
    form_class = FullTimeCreateForm
    template_name = 'accounting/base_form.html'

    def get_success_url(self):
        return reverse_lazy('accounting:personnel', kwargs={'business_unit': self.kwargs['business_unit']})

    def form_valid(self, form):
        business_unit = BusinessUnit.objects.get(pk=self.kwargs['business_unit'])
        form.instance.business_unit = business_unit
        response = super(FullTimeCreateView, self).form_valid(form)
        return response


class FullTimeDeleteView(ManagerMixin, DeleteView):
    model = FullTime
    template_name = 'accounting/base_delete_form.html'

    def get_object(self):
        return FullTime.objects.get(pk=self.kwargs['full_time'])

    def get_success_url(self):
        return reverse_lazy('accounting:personnel', kwargs={'business_unit': self.kwargs['business_unit']})


class FullTimeUpdateView(ManagerMixin, UpdateView):
    model = FullTime
    form_class = FullTimeUpdateForm
    template_name = 'accounting/base_form.html'

    def get_object(self):
        return FUllTime.objects.get(pk=self.kwargs['full_time'])

    def get_success_url(self):
        return reverse_lazy('accounting:personnel', kwargs={'business_unit': self.kwargs['business_unit']})


class PartTimeCreateView(ManagerMixin, CreateView):
    model = PartTime
    form_class = PartTimeCreateForm
    template_name = 'accounting/base_form.html'

    def get_success_url(self):
        return reverse_lazy('accounting:personnel', kwargs={'business_unit': self.kwargs['business_unit']})

    def form_valid(self, form):
        business_unit = BusinessUnit.objects.get(pk=self.kwargs['business_unit'])
        form.instance.business_unit = business_unit
        form.instance.hours_work = 20
        response = super(PartTimeCreateView, self).form_valid(form)
        return response


class PartTimeDeleteView(ManagerMixin, DeleteView):
    model = PartTime
    template_name = 'accounting/base_delete_form.html'

    def get_object(self):
        return PartTime.objects.get(pk=self.kwargs['part_time'])

    def get_success_url(self):
        return reverse_lazy('accounting:personnel', kwargs={'business_unit': self.kwargs['business_unit']})


class PartTimeUpdateView(ManagerMixin, UpdateView):
    model = PartTime
    form_class = PartTimeUpdateForm
    template_name = 'accounting/base_form.html'

    def get_object(self):
        return PartTime.objects.get(pk=self.kwargs['part_time'])

    def get_success_url(self):
        return reverse_lazy('accounting:personnel', kwargs={'business_unit': self.kwargs['business_unit']})


class UserTeamRoleCreateView(ManagerMixin, CreateView):
    model = UserTeamRole
    form_class = UserTeamRoleCreateForm
    template_name = 'accounting/base_form.html'

    def get_success_url(self):
        return reverse_lazy('accounting:user_team_roles_settings', kwargs={'business_unit': self.kwargs['business_unit']})

    def form_valid(self, form):
        business_unit = BusinessUnit.objects.get(pk=self.kwargs['business_unit'])
        form.instance.business_unit = business_unit
        form.instance.hours_work = 20
        try:
            response = super(UserTeamRoleCreateView, self).form_valid(form)
            return response
        except:
            form.add_error(None, 'This user already has a role in this team.')
            return self.form_invalid(form)


class UserTeamRoleDeleteView(ManagerMixin, DeleteView):
    model = UserTeamRole
    template_name = 'accounting/user_team_role_delete_form.html'

    def get_object(self):
        return UserTeamRole.objects.get(pk=self.kwargs['user_team_role'])

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.role == 'MANAGER' and UserTeamRole.objects.filter(role='MANAGER', business_unit=self.object.business_unit).count() == 1:
            raise Http404()
        else:
            return super(UserTeamRoleDeleteView, self).delete(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('accounting:user_team_roles_settings', kwargs={'business_unit': self.kwargs['business_unit']})


class UserTeamRoleUpdateView(ManagerMixin, UpdateView):
    template_name = 'accounting/base_form.html'
    form_class = UserTeamRoleUpdateForm
    model = UserTeamRole

    def get_object(self):
        return UserTeamRole.objects.get(pk=self.kwargs['user_team_role'])

    def get_success_url(self):
        return reverse_lazy('accounting:user_team_roles_settings', kwargs={'business_unit': self.kwargs['business_unit']})
