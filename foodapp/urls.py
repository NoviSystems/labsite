from django.conf.urls.defaults import url
from views import HomepageView, OrderListView, UserOrderView, TodaysOrdersView, MonthOrdersView, last_month_view, SuperMonthOrdersView

urlpatterns = (
    url(r'^$', HomepageView.as_view(), name='url_homepage'),
    url(r'^orders/$', OrderListView.as_view(), name='url_orders'),
    url(r'^orders/user/(?P<username>\w+)/$', UserOrderView.as_view(), name='url_user_orders'),
    url(r'^orders/today/$', TodaysOrdersView.as_view(), name='url_todays_orders'),
    url(r'^orders/last_month/$', last_month_view, name='url_last_month_view'),
    url(r'^orders/(?P<year>\d{4})/(?P<month>\d{2})/$', MonthOrdersView.as_view(), name='url_month_orders'),
    url(r'^orders/super/(?P<year>\d{4})/(?P<month>\d{2})/$', SuperMonthOrdersView.as_view(), name='url_super_month_orders'),
    #url(r'^orders/items/(?P<pk>\d+)/$', view, name='url_item_orders'),
)
