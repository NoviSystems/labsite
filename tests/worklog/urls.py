from django.conf.urls import include, url


urlpatterns = [
    url(r'^worklog/', include('worklog.urls', namespace='worklog')),
]
