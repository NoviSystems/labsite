from django.conf.urls import url, include, patterns
from accounting.views import *

urlpatterns = [
	url(r'^$', HomePageView.as_view(), name='home'),
	url(r'^dashboard/(?P<pk>\d+)/', DashboardView.as_view(), name='dashboard'),
	url(r'^create_business_unit/$', BusinessUnitCreateView.as_view(), name='create_business_unit'),
]
