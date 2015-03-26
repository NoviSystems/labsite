
from django.conf.urls import url
from foodapp import views


urlpatterns = (
    url(r'^$', views.HomeView.as_view(), name='url_home'),
    url(r'^orders/$', views.OrderListView.as_view(), name='url_orders'),
    url(r'^orders/user/(?P<username>\w+)/$', views.UserOrderView.as_view(), name='url_user_orders'),
    url(r'^orders/last_month/$', views.last_month_view, name='url_last_month_view'),
    url(r'^orders/leaderboard/$', views.LeaderboardView.as_view(), name='url_leaderboard'),
    url(r'^orders/(?P<year>\d{4})/(?P<month>\d{2})/$', views.MonthOrdersView.as_view(), name='url_month_orders'),
    url(r'^orders/super/(?P<year>\d{4})/(?P<month>\d{2})/$', views.SuperMonthOrdersView.as_view(), name='url_super_month_orders'),
)
