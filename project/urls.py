from django.conf.urls import include, url
from django.contrib import admin

from project import views


___password_reset_confirm = r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$'

urlpatterns = [
    url(r'^$', views.HomepageView.as_view()),

    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),

    # Auth urls
    url(r'^login/$',                    views.LoginView.as_view(),                  name='login'),
    url(r'^logout/$',                   views.LogoutView.as_view(),                 name='logout'),

    url(r'^password_change/$',          views.PasswordChangeView.as_view(),         name='password_change'),
    url(r'^password_change/done/$',     views.PasswordChangeDoneView.as_view(),     name='password_change_done'),

    url(r'^password_reset/$',           views.PasswordResetView.as_view(),          name='password_reset'),
    url(r'^password_reset/done/$',      views.PasswordResetDoneView.as_view(),      name='password_reset_done'),
    url(___password_reset_confirm,      views.PasswordResetConfirmView.as_view(),   name='password_reset_confirm'),
    url(r'^reset/done/$',               views.PasswordResetCompleteView.as_view(),  name='password_reset_complete'),

    url(r'^accounts/', include('registration_invite.urls.activation')),

    # App urls
    url(r'^lunch/', include('foodapp.urls')),
    url(r'^worklog/', include('worklog.urls')),
    url(r'^accounting/', include('accounting.urls')),
]
