from django.conf.urls import include, url
from django.contrib import admin

from views import HomepageView


urlpatterns = [
    url(r'^$', HomepageView.as_view()),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/login/$', 'django.contrib.auth.views.login', name='login'),
    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout', {'next_page': "/accounts/login"}, name="logout"),
    url(r'^lunch/', include('foodapp.urls', app_name='foodapp')),
    url(r'^worklog/', include('worklog.urls', app_name='worklog')),
]
