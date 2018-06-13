import datetime

from django.conf import settings
from django.db import models
from django.db.models import Q, Case, When

User = settings.AUTH_USER_MODEL


class Employee(models.Model):
    user = models.OneToOneField(User)

    def __str__(self):
        return '%s' % self.user.get_full_name()


class Holiday(models.Model):
    description = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return '%s' % (self.description,)


class WorkDay(models.Model):
    user = models.ForeignKey(User, related_name='workdays')
    date = models.DateField()
    reconciled = models.BooleanField(default=False)

    @property
    def workitem_set(self):
        return WorkItem.objects.filter(date=self.date, user=self.user)


class WorkPeriod(models.Model):
    payroll_id = models.CharField(max_length=8)
    start_date = models.DateField()
    end_date = models.DateField()
    due_date = models.DateField()
    pay_day = models.DateField()

    def __str__(self):
        return '%s' % (self.payroll_id,)


class JobQuerySet(models.QuerySet):
    def annotate_is_open(self, date=None):
        if date is None:
            date = datetime.date.today()
        return self.annotate(is_open=Case(
            When(
                condition=Q(open_date__lte=date) & (Q(close_date__gte=date) | Q(close_date=None)),
                then=True,
            ),
            default=False,
            output_field=models.BooleanField(),
        ))

    def open_on(self, date=None):
        return self.annotate_is_open(date).filter(is_open=True)

    def available_to(self, user):
        if (user.is_superuser):
            return self
        return self.filter(Q(users__id=user.pk) | Q(available_all_users=True)).distinct()


class JobManager(models.Manager.from_queryset(JobQuerySet)):
    def get_queryset(self):
        return super().get_queryset().annotate_is_open()


class Job(models.Model):
    name = models.CharField(max_length=256)
    # end_date is inclusive, so the duration of a Job is end_date-start_date + 1 day
    # if end_date==None, the Job is still open
    open_date = models.DateField()
    close_date = models.DateField(null=True, blank=True)
    invoiceable = models.BooleanField(default=True)
    users = models.ManyToManyField(User, blank=True)
    available_all_users = models.BooleanField(default=True)

    objects = JobManager()

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def hasFunding(self):
        return len(self.funding.all()) != 0

    def hasWork(self):
        return len(WorkItem.objects.filter(job=self)) != 0


class BillingSchedule(models.Model):
    job = models.ForeignKey(Job, related_name='billing_schedule')
    date = models.DateField()

    def __str__(self):
        return 'Billing for %s' % self.job


class Funding(models.Model):
    job = models.ForeignKey(Job, related_name='funding')
    hours = models.IntegerField()
    date_available = models.DateField()

    def __str__(self):
        return 'Funding for %s' % self.job


class WorkItem(models.Model):
    user = models.ForeignKey(User)
    date = models.DateField()
    hours = models.FloatField()
    text = models.TextField(verbose_name="Tasks")
    job = models.ForeignKey(Job)
    invoiced = models.BooleanField(default=False)

    def __str__(self):
        return '{user} on {date} worked {hours} hours on job {job} doing {item}'.format(
            user=self.user, date=self.date, hours=self.hours, job=self.job, item=self.text)

    def save(self, *args, **kwargs):
        if (not Job.objects.available_to(self.user).filter(name=self.job.name).exists()):
            raise ValueError("Specified job is not available to {user}".format(user=str(self.user)))

        if (not Job.objects.open_on(self.date).filter(name=self.job.name).exists()):
            raise ValueError("Specified job is not open on {date}".format(date=self.date.isoformat()))

        super(WorkItem, self).save(*args, **kwargs)
