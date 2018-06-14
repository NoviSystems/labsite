import datetime

from django.contrib.auth.models import User
from django.core import mail

import worklog.tasks as tasks
from tests.worklog import WorklogTestCaseBase
from worklog.models import Employee, Job, WorkDay, WorkItem


class SendReminderEmailsTestCase(WorklogTestCaseBase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.user3 = User.objects.create_user(username="user3", email="user3@example.com", password="password")
        cls.user4 = User.objects.create_user(username="user4", email="user4@example.com", password="password")
        cls.user5 = User.objects.create_user(username="user5", email="user5@example.com", password="password")
        Employee.objects.create(user=cls.user)
        Employee.objects.create(user=cls.user2)
        Employee.objects.create(user=cls.user3)
        Employee.objects.create(user=cls.user4)
        Employee.objects.create(user=cls.user5)

    def test_basic(self):
        # create some work items
        job = Job.objects.get(name="Job_Today")
        items = [
            WorkItem.objects.create(user=self.user, date=self.today, hours=1, text="item1", job=job),
            WorkItem.objects.create(user=self.user, date=self.yesterday, hours=2, text="item2", job=job),
            WorkItem.objects.create(user=self.user, date=self.today_minus_2, hours=3, text="item3", job=job),
            WorkItem.objects.create(user=self.user, date=self.today_minus_3, hours=4, text="item4", job=job),
            WorkItem.objects.create(user=self.user2, date=self.today, hours=5, text="item5", job=job),
            WorkItem.objects.create(user=self.user2, date=self.yesterday, hours=6, text="item6", job=job),
            WorkItem.objects.create(user=self.user2, date=self.today_minus_2, hours=7, text="item7", job=job),
            WorkItem.objects.create(user=self.user2, date=self.today_minus_3, hours=8, text="item8", job=job),
            WorkItem.objects.create(user=self.user3, date=self.yesterday, hours=9, text="item9", job=job),
            WorkItem.objects.create(user=self.user4, date=self.last_week, hours=10, text="item10", job=job),
            WorkItem.objects.create(user=self.user5, date=self.tomorrow, hours=11, text="item11", job=job),
        ]
        for item in items:
            workday, _ = WorkDay.objects.get_or_create(user=item.user, date=item.date)
            workday.reconciled = True
            workday.save()

        # try to send emails
        tasks.send_reminder_emails()

        email_count = {
            1: 6,
            2: 5,
            3: 8,
            4: 11,
            5: 11,
            6: 0,
            7: 0
        }

        emails_sent = email_count[datetime.date.today().isoweekday()]

        self.assertEquals(len(mail.outbox), emails_sent)  # user3, user4, user5
        all_recipients = list(m.to[0] for m in mail.outbox)
        self.assertEquals(len(all_recipients), emails_sent)
        if emails_sent:
            self.assertTrue("user3@example.com" in all_recipients)
            self.assertTrue("user4@example.com" in all_recipients)
            self.assertTrue("user5@example.com" in all_recipients)

    def test_empty(self):
        # create some work items
        job = Job.objects.get(name="Job_Today")
        items = [
            WorkItem.objects.create(user=self.user, date=self.today, hours=1, text="item1", job=job),
            WorkItem.objects.create(user=self.user2, date=self.today, hours=2, text="item2", job=job),
            WorkItem.objects.create(user=self.user3, date=self.today, hours=3, text="item3", job=job),
            WorkItem.objects.create(user=self.user4, date=self.today, hours=4, text="item4", job=job),
            WorkItem.objects.create(user=self.user5, date=self.today, hours=5, text="item5", job=job),
            WorkItem.objects.create(user=self.user, date=self.yesterday, hours=6, text="item6", job=job),
            WorkItem.objects.create(user=self.user2, date=self.yesterday, hours=7, text="item7", job=job),
            WorkItem.objects.create(user=self.user3, date=self.yesterday, hours=8, text="item8", job=job),
            WorkItem.objects.create(user=self.user4, date=self.yesterday, hours=9, text="item9", job=job),
            WorkItem.objects.create(user=self.user5, date=self.yesterday, hours=10, text="item10", job=job),
            WorkItem.objects.create(user=self.user, date=self.today_minus_2, hours=11, text="item11", job=job),
            WorkItem.objects.create(user=self.user2, date=self.today_minus_2, hours=12, text="item12", job=job),
            WorkItem.objects.create(user=self.user3, date=self.today_minus_2, hours=13, text="item13", job=job),
            WorkItem.objects.create(user=self.user4, date=self.today_minus_2, hours=14, text="item14", job=job),
            WorkItem.objects.create(user=self.user5, date=self.today_minus_2, hours=15, text="item15", job=job),
            WorkItem.objects.create(user=self.user, date=self.today_minus_3, hours=16, text="item16", job=job),
            WorkItem.objects.create(user=self.user2, date=self.today_minus_3, hours=17, text="item17", job=job),
            WorkItem.objects.create(user=self.user3, date=self.today_minus_3, hours=18, text="item18", job=job),
            WorkItem.objects.create(user=self.user4, date=self.today_minus_3, hours=19, text="item19", job=job),
            WorkItem.objects.create(user=self.user5, date=self.today_minus_3, hours=20, text="item20", job=job),
        ]
        for item in items:
            workday, created = WorkDay.objects.get_or_create(user=item.user, date=item.date)
            workday.reconciled = True
            workday.save()

        # try to send emails
        tasks.send_reminder_emails()

        self.assertEquals(len(mail.outbox), 0)
        all_recipients = list(m.to[0] for m in mail.outbox)
        self.assertEquals(len(all_recipients), 0)
