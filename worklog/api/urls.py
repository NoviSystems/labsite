
from django.conf.urls import include, url
from rest_framework.routers import DefaultRouter
from worklog.api import views


router = DefaultRouter()
router.register(r'workdays', views.WorkDayViewSet)
router.register(r'workitems', views.WorkItemViewSet)
router.register(r'users', views.UserViewSet)
router.register(r'jobs', views.JobViewSet)


urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]
