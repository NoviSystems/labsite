from django.contrib.auth import get_user_model
import rest_framework_filters as filters
from worklog import models


User = get_user_model()


class WorkDayFilter(filters.FilterSet):
    class Meta:
        model = models.WorkDay
        fields = ['date', 'user', ]


class WorkItemFilter(filters.FilterSet):
    username = filters.CharFilter(name='user__username', lookup_type='exact')

    class Meta:
        model = models.WorkItem
        fields = {
            'user': ['exact', 'in', ],
            'date': [
                'exact', 'in', 'lt', 'lte', 'gt', 'gte', 'range', 'isnull',
                'year', 'month', 'day', 'week_day',
            ],
            'hours': [
                'exact', 'in', 'lt', 'lte', 'gt', 'gte', 'range',
            ],
            'job': ['exact', 'in', ],
        }


class JobFilter(filters.FilterSet):
    user = filters.ModelChoiceFilter(method='filter_user', queryset=User.objects.all())
    date = filters.DateFilter(method='filter_date')

    def filter_date(self, qs, name, value):
        return qs.open_on(value)

    def filter_user(self, qs, name, value):
        return qs.available_to(value)

    class Meta:
        model = models.Job
        fields = {
            'name': ['exact', 'in', ],
        }
