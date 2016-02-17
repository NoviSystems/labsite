from django.conf.urls import url, include, patterns
from accounting.views import *

urlpatterns = [
	url(r'^$', HomePageView.as_view(), name='home'),

	url(r'^dashboard/(?P<pk>\d+)/$', DashboardView.as_view(), name='dashboard'),

	url(r'^create_business_unit/$', BusinessUnitCreateView.as_view(), name='create_business_unit'),
	url(r'^update_business_unit/(?P<business_unit>\d+)/$', BusinessUnitUpdateView.as_view(), name='update_business_unit'),
	url(r'^delete_business_unit/(?P<business_unit>\d+)/$', BusinessUnitDeleteView.as_view(), name='delete_business_unit'),

	url(r'^dashboard/(?P<pk>\d+)/create_fiscal_year/$', FiscalYearCreateView.as_view(), name='create_fiscal_year'),
	url(r'^dashboard/(?P<pk>\d+)/update_fiscal_year/(?P<fiscal_year>\d+)/$', FiscalYearUpdateView.as_view(), name='update_fiscal_year'),
	url(r'^dashboard/(?P<pk>\d+)/delete_fiscal_year/(?P<fiscal_year>\d+)/$', FiscalYearDeleteView.as_view(), name='delete_fiscal_year'),

	url(r'^dashboard/(?P<pk>\d+)/create_expense/$', ExpenseCreateView.as_view(), name='create_expense'),
	url(r'^dashboard/(?P<pk>\d+)/update_expense/(?P<expense>\d+)/$', ExpenseUpdateView.as_view(), name='update_expense'),
	url(r'^dashboard/(?P<pk>\d+)/delete_expense/(?P<expense>\d+)/$', ExpenseDeleteView.as_view(), name='delete_expense'),

	url(r'^contracts/(?P<pk>\d+)/$', ContractsView.as_view(), name='contracts'),

	url(r'^contracts/(?P<pk>\d+)/create_contract/$', ContractCreateView.as_view(), name='create_contract'),
	url(r'^contracts/(?P<pk>\d+)/update_contract/(?P<contract>\d+)/$', ContractUpdateView.as_view(), name='update_contract'),
	url(r'^contracts/(?P<pk>\d+)/delete_contract/(?P<contract>\d+)/$', ContractDeleteView.as_view(), name='delete_contract'),

	url(r'^expenses/(?P<pk>\d+)/$', ExpensesView.as_view(), name='expenses'),
]