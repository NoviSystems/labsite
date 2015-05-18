from django.conf.urls import include, url
from django.contrib import admin

from views import LabsiteView


urlpatterns = [
    url(r'^$', LabsiteView.as_view()),

    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),

    url(r'^accounts/login/$', 'django.contrib.auth.views.login', name='login'),
    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout', {'next_page': "/accounts/login"}, name="logout"),

    # App urls
    url(r'^lunch/', include('foodapp.urls')),
    url(r'^worklog/', include('worklog.urls')),
]
