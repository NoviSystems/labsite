from django.conf.urls import url, include, patterns
from accounting import views

urlpatterns = patterns(
	'accounting',
	url(r'^$', views.TestView.as_view(), name='accounting-home'),
)