import datetime
from django.test import TestCase
from django.contrib.auth import get_user_model


class UserLoginContext(object):
    def __init__(self, client, username, password):
        self.client = client
        self.username = username
        self.password = password

    def __enter__(self):
        self.client.login(username=self.username, password=self.password)

    def __exit__(self, type, value, traceback):
        self.client.logout()


class WorklogTestCaseBase(TestCase):
    @classmethod
    def setUpTestData(cls):
        from labsite.worklog.models import Job

        today = datetime.date.today()
        cls.today = today
        last_week = today - datetime.timedelta(days=7)
        last_2week = today - datetime.timedelta(days=14)
        next_week = today + datetime.timedelta(days=7)
        cls.last_week = last_week
        cls.next_week = next_week
        cls.yesterday = cls.today - datetime.timedelta(days=1)
        cls.tomorrow = cls.today + datetime.timedelta(days=1)
        cls.today_minus_2 = cls.today - datetime.timedelta(days=2)
        cls.today_minus_3 = cls.today - datetime.timedelta(days=3)

        job = Job.objects.create(name="Job_Today", open_date=today)
        job.save()
        job = Job.objects.create(name="Job_OneDay", open_date=today, close_date=today)
        job.save()
        job = Job.objects.create(name="Job_LastWeek", open_date=last_week)
        job.save()
        job = Job.objects.create(name="Job_LastWeek2", open_date=last_week, close_date=today)
        job.save()

        job = Job.objects.create(name="Job_Future", open_date=next_week)
        job.save()
        job = Job.objects.create(name="Job_Old", open_date=last_2week, close_date=last_week)
        job.save()

        User = get_user_model()
        cls.user = User.objects.create_user(username="master", email="master@example.com", password="password")
        cls.user2 = User.objects.create_user(username="user2", email="user2@example.com", password="password")

    # for use in 'with' statements
    def scoped_login(self, username, password):
        return UserLoginContext(self.client, username, password)
