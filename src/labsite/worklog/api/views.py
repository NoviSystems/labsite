from django.contrib.auth.models import User
from rest_framework import viewsets

from . import filters, serializers
from .. import models


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all().order_by('pk')
    serializer_class = serializers.UserSerializer
    # filter_class = there is no user filter class yet


class WorkDayViewSet(viewsets.ModelViewSet):
    queryset = models.WorkDay.objects.all().order_by('pk')
    serializer_class = serializers.WorkDaySerializer
    filter_class = filters.WorkDayFilter


class WorkItemViewSet(viewsets.ModelViewSet):
    queryset = models.WorkItem.objects.all().order_by('pk')
    serializer_class = serializers.WorkItemSerializer
    filter_class = filters.WorkItemFilter


class JobViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Job.objects.all().order_by('pk')
    serializer_class = serializers.JobSerializer
    filter_class = filters.JobFilter
