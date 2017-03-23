from django.contrib.auth.views import login as auth_login, logout as auth_logout
from django.conf.urls import include, url
from django.contrib import admin

from project.views import HomepageView


urlpatterns = [
    url(r'^$', HomepageView.as_view()),

    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),

    url(r'^accounts/login/$', auth_login, name='login'),
    url(r'^accounts/logout/$', auth_logout, {'next_page': '/accounts/login'}, name='logout'),
    url(r'^accounts/', include('itng.registration.auth_urls')),
    url(r'^accounts/', include('itng.registration.backends.invite.urls.activation')),

    # App urls
    url(r'^lunch/', include('foodapp.urls')),
    url(r'^worklog/', include('worklog.urls')),
    url(r'^accounting/', include('accounting.urls')),
]
