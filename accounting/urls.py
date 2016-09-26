from django.conf.urls import url, include, patterns
from accounting.views import *

urlpatterns = [
    
    # Accounting HomePage
    url(r'^$', HomePageView.as_view(), name='home'),

    # Dashboard Views
    url(r'^business_unit/(?P<business_unit>\d+)/dashboard/$', DashboardView.as_view(), name='dashboard'),
    url(r'^business_unit/(?P<business_unit>\d+)/dashboard/(?P<fiscal_year>\d+)/$', DashboardView.as_view(), name='dashboard'),
    url(r'^business_unit/(?P<business_unit>\d+)/dashboard/(?P<fiscal_year>\d+)/(?P<month>\d+)/$', DashboardMonthView.as_view(), name='dashboard_month'),

    # Expense Views
    url(r'^business_unit/(?P<business_unit>\d+)/expenses/$', ExpensesView.as_view(), name='expenses'),
    url(r'^business_unit/(?P<business_unit>\d+)/expenses/(?P<fiscal_year>\d+)/(?P<month>\d+)/$', ExpensesView.as_view(), name='expenses'),
    url(r'^business_unit/(?P<business_unit>\d+)/expenses/(?P<month>\d+)/$', ExpensesView.as_view(), name='expenses'),

    # Revenue Views
    url(r'^business_unit/(?P<business_unit>\d+)/revenue/$', RevenueView.as_view(), name='revenue'),

    # Contracts View
    url(r'^(?P<business_unit>\d+)/contracts/$', ContractsView.as_view(), name='contracts'),

    # Personnel Views
    url(r'^(?P<business_unit>\d+)/personnel/$', PersonnelView.as_view(), name='personnel'),

    # Settings Views
    url(r'^(?P<business_unit>\d+)/settings/$', SettingsPageView.as_view(), name='settings'),

    # BusinessUnit Forms
    url(r'^business_unit/create/$', BusinessUnitCreateView.as_view(), name='create_business_unit'),
    url(r'^business_unit/(?P<business_unit>\d+)/update/$', BusinessUnitUpdateView.as_view(), name='update_business_unit'),
    url(r'^business_unit/(?P<business_unit>\d+)/delete/$', BusinessUnitDeleteView.as_view(), name='delete_business_unit'),

    # FiscalYear Forms
    url(r'^business_unit/(?P<business_unit>\d+)/fiscal_year/create/$', FiscalYearCreateView.as_view(), name='create_fiscal_year'),
    url(r'^business_unit/(?P<business_unit>\d+)/fiscal_year/(?P<fiscal_year>\d+)/update/$', FiscalYearUpdateView.as_view(), name='update_fiscal_year'),
    url(r'^business_unit/(?P<business_unit>\d+)/fiscal_year/(?P<fiscal_year>\d+)/delete/$', FiscalYearDeleteView.as_view(), name='delete_fiscal_year'),

    # Expense Forms
    url(r'^business_unit/(?P<business_unit>\d+)/(?P<month>\d+)/expenses/create/$', ExpenseCreateView.as_view(), name='create_expense'),
    url(r'^business_unit/(?P<business_unit>\d+)/(?P<month>\d+)/expenses/(?P<expense>\d+)/update/$', ExpenseUpdateView.as_view(), name='update_expense'),
    url(r'^business_unit/(?P<business_unit>\d+)/(?P<month>\d+)/expenses/(?P<expense>\d+)/delete/$', ExpenseDeleteView.as_view(), name='delete_expense'),

    # Income Forms
    url(r'^business_unit/(?P<business_unit>\d+)/(?P<month>\d+)/income/create/$', IncomeCreateView.as_view(), name='create_income'),
    url(r'^business_unit/(?P<business_unit>\d+)/(?P<month>\d+)/income/(?P<income>\d+)/update/$', IncomeUpdateView.as_view(), name='update_income'),
    url(r'^business_unit/(?P<business_unit>\d+)/(?P<month>\d+)/income/(?P<income>\d+)/delete/$', IncomeDeleteView.as_view(), name='delete_income'),

    # Cash Forms
    url(r'^(?P<business_unit>\d+)/(?P<month>\d+)/cash/(?P<cash>\d+)/update/$', CashUpdateView.as_view(), name='update_cash'),

    # Contracts Forms
    url(r'^business_unit/(?P<business_unit>\d+)/contracts/create/$', ContractCreateView.as_view(), name='create_contract'),
    url(r'^business_unit/(?P<business_unit>\d+)/contracts/(?P<contract>\d+)/update/$', ContractUpdateView.as_view(), name='update_contract'),
    url(r'^business_unit/(?P<business_unit>\d+)/contracts/(?P<contract>\d+)/delete/$', ContractDeleteView.as_view(), name='delete_contract'),

    # Invoice Forms
    url(r'^business_unit/(?P<business_unit>\d+)/contracts/(?P<contract>\d+)/invoice/create/$', InvoiceCreateView.as_view(), name='create_invoice'),
    url(r'^business_unit/(?P<business_unit>\d+)/contracts/(?P<contract>\d+)/invoice/(?P<invoice>\d+)/update/$', InvoiceUpdateView.as_view(), name='update_invoice'),
    url(r'^business_unit/(?P<business_unit>\d+)/contracts/(?P<contract>\d+)/invoice/(?P<invoice>\d+)/delete/$', InvoiceDeleteView.as_view(), name='delete_invoice'),

    # Salary Forms
    url(r'^business_unit/(?P<business_unit>\d+)/salary/create/$', SalaryCreateView.as_view(), name='create_salary'),
    url(r'^business_unit/(?P<business_unit>\d+)/salary/(?P<salary>\d+)/update/$', SalaryUpdateView.as_view(), name='update_salary'),
    url(r'^business_unit/(?P<business_unit>\d+)/salary/(?P<salary>\d+)/delete/$', SalaryDeleteView.as_view(), name='delete_salary'),

    # PartTime Forms
    url(r'^business_unit/(?P<business_unit>\d+)/part_time/create/$', PartTimeCreateView.as_view(), name='create_part_time'),
    url(r'^business_unit/(?P<business_unit>\d+)/part_time/(?P<part_time>\d+)/update/$', PartTimeUpdateView.as_view(), name='update_part_time'),
    url(r'^business_unit/(?P<business_unit>\d+)/part_time/(?P<part_time>\d+)/delete/$', PartTimeDeleteView.as_view(), name='delete_part_time'),

    # User Team Role Forms
    url(r'^business_unit/(?P<business_unit>\d+)/user_team_role/create/$', UserTeamRoleCreateView.as_view(), name='create_user_team_role'),
    url(r'^business_unit/(?P<business_unit>\d+)/user_team_role/(?P<user_team_role>\d+)/update/$', UserTeamRoleUpdateView.as_view(), name='update_user_team_role'),
    url(r'^business_unit/(?P<business_unit>\d+)/user_team_role/(?P<user_team_role>\d+)/delete/$', UserTeamRoleDeleteView.as_view(), name='delete_user_team_role'),
]
