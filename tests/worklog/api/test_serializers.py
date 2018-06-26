import datetime

from django.contrib.auth.models import User
from rest_framework.serializers import ValidationError
from rest_framework.test import APITestCase

from labsite.worklog.api.serializers import WorkItemSerializer
from labsite.worklog.models import Job
from tests.worklog import factories


class WorkItemSerializerTestCase(APITestCase):

    def setUp(self):
        self.serializer = WorkItemSerializer()

        factories.UserFactory.create_batch(10)
        factories.WorkItemFactory.create_batch(10)
        factories.JobFactory.create_batch(10)

        self.jobs = Job.objects.all()
        self.open_jobs = Job.objects.open_on(datetime.date.today())
        self.closed_jobs = Job.objects.exclude(pk__in=self.open_jobs.values_list('pk', flat=True))

    def test_fixtures(self):
        users = list(User.objects.all())
        jobs = list(Job.objects.all())

        self.assertNotEqual(users, [])
        self.assertNotEqual(jobs, [])

    def test_validate_job(self):
        self.assertRaises(ValidationError, lambda: self.serializer.validate_job(None))
        self.assertRaises(ValidationError, lambda: self.serializer.validate_job({}))

        attrs = self.serializer.validate_job(self.open_jobs[0])
        self.assertIsNotNone(attrs)

        self.assertRaises(ValidationError, lambda: self.serializer.validate_job(None))
        self.assertRaises(ValidationError, lambda: self.serializer.validate_job(self.closed_jobs[0]))

    def test_validate_hours(self):
        self.assertRaises(ValidationError, lambda: self.serializer.validate_hours(None))
        self.assertRaises(ValidationError, lambda: self.serializer.validate_hours({}))

        attrs = self.serializer.validate_hours(13)
        self.assertIsNotNone(attrs)
        attrs = self.serializer.validate_hours(13.5)
        self.assertIsNotNone(attrs)

        self.assertRaises(ValidationError, lambda: self.serializer.validate_hours(None))
        self.assertRaises(ValidationError, lambda: self.serializer.validate_hours(-1))
        self.assertRaises(ValidationError, lambda: self.serializer.validate_hours(1.3))

    def test_validate_text(self):
        self.assertRaises(ValidationError, lambda: self.serializer.validate_text(None,))
        self.assertRaises(ValidationError, lambda: self.serializer.validate_text({}))

        attrs = self.serializer.validate_text('foo bar baz qux')
        self.assertIsNotNone(attrs)
