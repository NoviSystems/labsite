from django.conf.urls import url, include, patterns
from accounting.views import *

urlpatterns = [
	url(r'^$', HomePageView.as_view(), name='home'),

	url(r'^create_business_unit/$', BusinessUnitCreateView.as_view(), name='create_business_unit'),
	url(r'^(?P<business_unit>\d+)/update_business_unit/$', BusinessUnitUpdateView.as_view(), name='update_business_unit'),
	url(r'^(?P<business_unit>\d+)/delete_business_unit/$', BusinessUnitDeleteView.as_view(), name='delete_business_unit'),

	url(r'^(?P<pk>\d+)/dashboard/$', DashboardView.as_view(), name='dashboard'),

	url(r'^(?P<pk>\d+)/dashboard/create_fiscal_year/$', FiscalYearCreateView.as_view(), name='create_fiscal_year'),
	url(r'^(?P<pk>\d+)/dashboard/(?P<fiscal_year>\d+)/update_fiscal_year/$', FiscalYearUpdateView.as_view(), name='update_fiscal_year'),
	url(r'^(?P<pk>\d+)/dashboard/(?P<fiscal_year>\d+)/delete_fiscal_year/$', FiscalYearDeleteView.as_view(), name='delete_fiscal_year'),

	url(r'^(?P<pk>\d+)/dashboard/(?P<month>\d+)/create_expense/$', ExpenseCreateView.as_view(), name='create_expense'),
	url(r'^(?P<pk>\d+)/dashboard/(?P<expense>\d+)/update_expense/$', ExpenseUpdateView.as_view(), name='update_expense'),
	url(r'^(?P<pk>\d+)/dashboard/(?P<expense>\d+)/delete_expense/$', ExpenseDeleteView.as_view(), name='delete_expense'),

	url(r'^(?P<pk>\d+)/contracts/$', ContractsView.as_view(), name='contracts'),

	url(r'^(?P<pk>\d+)/contracts/create_contract/$', ContractCreateView.as_view(), name='create_contract'),
	url(r'^(?P<pk>\d+)/contracts/(?P<contract>\d+)/update_contract/$', ContractUpdateView.as_view(), name='update_contract'),
	url(r'^(?P<pk>\d+)/contracts/(?P<contract>\d+)/delete_contract/$', ContractDeleteView.as_view(), name='delete_contract'),

	url(r'^(?P<pk>\d+)/expenses/$', ExpensesView.as_view(), name='expenses'),
]