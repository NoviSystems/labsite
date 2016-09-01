from django.conf.urls import url, include, patterns
from accounting.views import *

urlpatterns = [
	url(r'^$', HomePageView.as_view(), name='home'),

	url(r'^create_business_unit/$', BusinessUnitCreateView.as_view(), name='create_business_unit'),
	url(r'^(?P<business_unit>\d+)/update_business_unit/$', BusinessUnitUpdateView.as_view(), name='update_business_unit'),
	url(r'^(?P<business_unit>\d+)/delete_business_unit/$', BusinessUnitDeleteView.as_view(), name='delete_business_unit'),

	url(r'^(?P<business_unit>\d+)/revenue/$', RevenueView.as_view(), name='revenue'),
	url(r'^(?P<business_unit>\d+)/revenue/(?P<invoice>\d+)/update_invoice/$', InvoiceUpdateView.as_view(), name='udpate_invoice'),

	url(r'^(?P<business_unit>\d+)/dashboard/$', DashboardView.as_view(), name='dashboard'),
	url(r'^(?P<business_unit>\d+)/dashboard/(?P<fiscal_year>\d+)/$', DashboardView.as_view(), name='dashboard'),
	url(r'^(?P<business_unit>\d+)/dashboard/(?P<fiscal_year>\d+)/(?P<month>\d+)/$', DashboardMonthView.as_view(), name='dashboard_month'),

	url(r'^(?P<business_unit>\d+)/dashboard/create_fiscal_year/$', FiscalYearCreateView.as_view(), name='create_fiscal_year'),
	url(r'^(?P<business_unit>\d+)/dashboard/(?P<fiscal_year>\d+)/update_fiscal_year/$', FiscalYearUpdateView.as_view(), name='update_fiscal_year'),
	url(r'^(?P<business_unit>\d+)/dashboard/(?P<fiscal_year>\d+)/delete_fiscal_year/$', FiscalYearDeleteView.as_view(), name='delete_fiscal_year'),

	url(r'^(?P<business_unit>\d+)/expenses/$', ExpensesView.as_view(), name='expenses'),
	url(r'^(?P<business_unit>\d+)/expenses/(?P<fiscal_year>\d+)/(?P<month>\d+)/$', ExpensesView.as_view(), name='expenses'),
	url(r'^(?P<business_unit>\d+)/expenses/(?P<month>\d+)/$', ExpensesView.as_view(), name='expenses'),

	url(r'^(?P<business_unit>\d+)/expenses/(?P<month>\d+)/create_expense/$', ExpenseCreateView.as_view(), name='create_expense'),
	url(r'^(?P<business_unit>\d+)/expenses/(?P<month>\d+)/(?P<expense>\d+)/update_expense/$', ExpenseUpdateView.as_view(), name='update_expense'),
	url(r'^(?P<business_unit>\d+)/expenses/(?P<month>\d+)/(?P<expense>\d+)/delete_expense/$', ExpenseDeleteView.as_view(), name='delete_expense'),

	url(r'^(?P<business_unit>\d+)/expenses/(?P<month>\d+)/create_income/$', IncomeCreateView.as_view(), name='create_income'),
	url(r'^(?P<business_unit>\d+)/expenses/(?P<month>\d+)/(?P<income>\d+)/update_income/$', IncomeUpdateView.as_view(), name='update_income'),
	url(r'^(?P<business_unit>\d+)/expenses/(?P<month>\d+)/(?P<income>\d+)/delete_income/$', IncomeDeleteView.as_view(), name='delete_income'),

	url(r'^(?P<business_unit>\d+)/expenses/(?P<month>\d+)/(?P<cash>\d+)/update_cash/$', CashUpdateView.as_view(), name='update_cash'),

	url(r'^(?P<business_unit>\d+)/contracts/$', ContractsView.as_view(), name='contracts'),

	url(r'^(?P<business_unit>\d+)/contracts/create_contract/$', ContractCreateView.as_view(), name='create_contract'),
	url(r'^(?P<business_unit>\d+)/contracts/(?P<contract>\d+)/update_contract/$', ContractUpdateView.as_view(), name='update_contract'),
	url(r'^(?P<business_unit>\d+)/contracts/(?P<contract>\d+)/delete_contract/$', ContractDeleteView.as_view(), name='delete_contract'),

	url(r'^(?P<business_unit>\d+)/contracts/(?P<contract>\d+)/create_invoice/$', InvoiceCreateView.as_view(), name='create_invoice'),
	url(r'^(?P<business_unit>\d+)/contracts/(?P<contract>\d+)/(?P<invoice>\d+)/udpate_invoice/$', InvoiceUpdateView.as_view(), name='udpate_invoice'),
	url(r'^(?P<business_unit>\d+)/contracts/(?P<contract>\d+)/(?P<invoice>\d+)/delete_invoice/$', InvoiceDeleteView.as_view(), name='delete_invoice'),

	url(r'^(?P<business_unit>\d+)/personnel/$', PersonnelView.as_view(), name='personnel'),

	url(r'^(?P<business_unit>\d+)/personnel/create_salary/$', SalaryCreateView.as_view(), name='create_salary'),
	url(r'^(?P<business_unit>\d+)/personnel/(?P<salary>\d+)/update_salary/$', SalaryUpdateView.as_view(), name='update_salary'),
	url(r'^(?P<business_unit>\d+)/personnel/(?P<salary>\d+)/delete_salary/$', SalaryDeleteView.as_view(), name='delete_salary'),

	url(r'^(?P<business_unit>\d+)/personnel/create_part_time/$', PartTimeCreateView.as_view(), name='create_part_time'),
	url(r'^(?P<business_unit>\d+)/personnel/(?P<part_time>\d+)/update_part_time/$', PartTimeUpdateView.as_view(), name='update_part_time'),
	url(r'^(?P<business_unit>\d+)/personnel/(?P<part_time>\d+)/delete_part_time/$', PartTimeDeleteView.as_view(), name='delete_part_time'),

	url(r'^(?P<business_unit>\d+)/settings/$', SettingsPageView.as_view(), name='settings'),
	url(r'^(?P<business_unit>\d+)/settings/permissions/create_accounting_user/$', AccountingUserCreateView.as_view(), name='create_accounting_user'),
	url(r'^(?P<business_unit>\d+)/settings/permissions/(?P<accounting_user>\d+)/update_accounting_user/$', AccountingUserUpdateView.as_view(), name='update_accounting_user'),
	url(r'^(?P<business_unit>\d+)/settings/permissions/(?P<accounting_user>\d+)/delete_accounting_user/$', AccountingUserDeleteView.as_view(), name='delete_accounting_user'),
]