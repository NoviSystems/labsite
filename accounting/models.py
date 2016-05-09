from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.dispatch import receiver
from django.db.models.signals import post_save
from datetime import date, datetime, timedelta
from calendar import monthrange
from django.core.exceptions import ObjectDoesNotExist


class BusinessUnit(models.Model):
    name = models.CharField(max_length=64)
    account_number = models.CharField(max_length=12)
    user = models.ManyToManyField(User)

    def __str__(self):
        return self.name


class FiscalYear(models.Model):
    business_unit = models.ForeignKey(BusinessUnit)
    start_date = models.DateField()
    end_date = models.DateField(default=datetime.now, blank=True)
    cash_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)

    def __str__(self):
        return self.start_date.strftime("%b %Y") + " - " + self.end_date.strftime("%b %Y")


class Month(models.Model):
    fiscal_year = models.ForeignKey(FiscalYear, default=None)
    month = models.DateField()
    projected_values = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    actual_values = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)

    def __str__(self):
        return self.fiscal_year.business_unit.name + " " + self.month.strftime("%b %Y")


class LineItem(models.Model):
    business_unit = models.ForeignKey(BusinessUnit)
    month = models.ForeignKey(Month)
    predicted_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    actual_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    reconciled = models.BooleanField(default=False)


class Contract(models.Model):
    CONTRACT_STATE = {
        ('ACTIVE', "active" ),
        ('COMPLETE', "complete" ),
    }
    CONTRACT_TYPE = {
        ('FIXED', "fixed" ),
        ('HOURLY', "hourly" ),
    }

    business_unit = models.ForeignKey(BusinessUnit)
    department = models.CharField(max_length=4, default='CSC')
    contract_number = models.IntegerField()
    organization_name = models.CharField(max_length=255)
    start_date = models.DateField()
    amount = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    contract_state = models.CharField(max_length=8, choices=CONTRACT_STATE)
    contract_type = models.CharField(max_length=8, choices=CONTRACT_TYPE)
    

class Cash(LineItem):
    name = models.CharField(max_length=50)


class Income(LineItem):
    name = models.CharField(max_length=50)
    date_payable = models.DateField()
    date_payed = models.DateField(default=None, null=True)


class Invoice(Income):
    TRANSITION_STATE = {
        ('INVOICED', "invoiced"),
        ('NOT_INVOICED', "not invoiced"),
        ('RECIEVED', "recieved"),
    }

    contract = models.ForeignKey(Contract)
    number = models.IntegerField()
    transition_state = models.CharField(max_length=15, choices=TRANSITION_STATE)


class Personnel(models.Model):
    business_unit = models.ForeignKey(BusinessUnit)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    employee_id = models.IntegerField()
    position = models.CharField(max_length=50)


class Salary(Personnel):
    SALARY_TYPE = {
        ('EPA', 'EPA'),
        ('SPA', 'SPA'),
    }

    salary_type = models.CharField(max_length=3, choices=SALARY_TYPE)
    salary_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    social_security_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    fed_health_insurance_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    retirement_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    medical_insurance_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    staff_benefits_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    fringe_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)


class PartTime(Personnel):
    HOURLY_TYPE = {
        ('STUDENT', 'student'),
        ('NON_STUDENT', 'non student')
    }
    hourly_type = models.CharField(max_length=12, choices=HOURLY_TYPE)
    hourly_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    hours_work = models.IntegerField()


class Expense(LineItem):
    name = models.CharField(max_length=50)
    date_payable = models.DateField()
    date_payed = models.DateField(default=None, null=True)


class Payroll(models.Model):
    month = models.OneToOneField(Month)
    expense = models.OneToOneField(Expense)
    
    def delete(self, *args, **kwargs):
        self.expense.delete()
        return super(self.__class__, self).delete(*args, **kwargs)


@receiver(post_save, sender=FiscalYear, dispatch_uid="createItemsForFiscalYear")
def createItemsForFiscalYear(sender, instance, **kwargs):
    start_month = instance.start_date
    end_month= instance.end_date
    number_of_months = monthdelta(start_month, end_month)

    month = start_month.month
    year = start_month.year
    day = start_month.day
    for i in range(number_of_months+1):
        if month == 12:
            year = year + 1
            month = 1
        elif i == 0:
            month = month
        else:
            month = month + 1
        Month.objects.create(fiscal_year=instance, month=date(year, month, day), projected_values=0.00, actual_values=0.00)
    months = Month.objects.filter(fiscal_year=instance.pk)
    for month in months:
        Cash.objects.create(month=month, business_unit=instance.business_unit, name="Cash")


# calculate month duration
def monthdelta(d1, d2):
    delta = 0
    while True:
        mdays = monthrange(d1.year, d1.month)[1]
        d1 += timedelta(days=mdays)
        if d1 <= d2:
            delta += 1
        else:
            break
    return delta