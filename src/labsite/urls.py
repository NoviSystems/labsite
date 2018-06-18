from django.conf.urls import include, url
from django.contrib import admin

from project import views


urlpatterns = [
    url(r'^$', views.HomepageView.as_view()),

    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),

    # Auth urls
    url(r'^', include('labsite.accounts.auth.urls')),

    url(r'^accounts/', include('registration_invite.urls.activation')),

    # App urls
    url(r'^lunch/', include('foodapp.urls')),
    url(r'^worklog/', include('worklog.urls')),
    url(r'^accounting/', include('accounting.urls')),
]
