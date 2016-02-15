from django.conf.urls import url, include, patterns
from accounting.views import *

urlpatterns = [
	url(r'^$', HomePageView.as_view(), name='home'),
	url(r'^dashboard/(?P<pk>\d+)/$', DashboardView.as_view(), name='dashboard'),

	url(r'^create_business_unit/$', BusinessUnitCreateView.as_view(), name='create_business_unit'),
	url(r'^update_business_unit/(?P<business_unit>\d+)/$', BusinessUnitUpdateView.as_view(), name='update_business_unit'),
	url(r'^delete_business_unit/(?P<business_unit>\d+)/$', BusinessUnitDeleteView.as_view(), name='delete_business_unit'),

	url(r'^create_fiscal_year/$', FiscalYearCreateView.as_view(), name='create_fiscal_year'),
	
]