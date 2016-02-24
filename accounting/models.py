from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.dispatch import receiver
from django.db.models.signals import post_save
from datetime import date
from django.core.exceptions import ObjectDoesNotExist


class BusinessUnit(models.Model):
    name = models.CharField(max_length=64)
    user = models.ManyToManyField(User)

    def __str__(self):
        return self.name

class FiscalYear(models.Model):
    business_unit = models.ForeignKey(BusinessUnit)
    start_month = models.DateField()
    number_of_months = models.IntegerField()


class Month(models.Model):
    fiscal_year = models.ForeignKey(FiscalYear, default=None)
    month = models.DateField()
    projected_values = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    actual_values = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)


class LineItem(models.Model):
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
    contract_number = models.IntegerField()
    organization_name = models.CharField(max_length=255)
    start_date = models.DateField()
    amount = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    contract_state = models.CharField(max_length=8, choices=CONTRACT_STATE)
    contract_type = models.CharField(max_length=8, choices=CONTRACT_TYPE)
    

class Invoice(LineItem):
    TRANSATION_STATE = {
        ('INVOICED', "invoiced"),
        ('NOT_INVOICED', "not invoiced"),
        ('RECIEVED', "recieved"),
    }

    month = models.ForeignKey(Month)
    number = models.IntegerField()
    date = models.DateField()
    amount = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    transation_state = models.CharField(max_length=15, choices=TRANSATION_STATE)


class Personnel(models.Model):
    business_unit = models.ForeignKey(BusinessUnit)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    employee_id = models.IntegerField()
    position = models.CharField(max_length=50)


class Salary(models.Model):
    SALARY_TYPE = {
        ('EPA', 'EPA'),
        ('SPA', 'SPA'),
    }
    salary_type = models.CharField(max_length=3, choices=SALARY_TYPE)
    social_security_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    fed_health_insurance_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    retirement_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    medical_insurance_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    staff_benefits_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    fringe_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)


class PartTime(models.Model):
    HOURLY_TYPE = {
        ('STUDENT', 'student'),
        ('NON_STUDENT', 'non student')
    }
    hourly_type = models.CharField(max_length=12, choices=HOURLY_TYPE)
    hourly_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    hours_work = models.IntegerField()


class Expense(LineItem):
    month = models.ForeignKey(Month)
    name = models.CharField(max_length=50)
    data_payable = models.DateField()
    date_payed = models.DateField()
    reoccuring = models.IntegerField()


@receiver(post_save, sender=FiscalYear, dispatch_uid="createMonthsForFiscalYear")
def createMonthsForFiscalYear(sender, instance, **kwargs):
    start_month = instance.start_month
    number_of_months = instance.number_of_months
    for i in range(number_of_months):
        Month.objects.create(fiscal_year=instance, month=date(start_month.year, start_month.month + i, start_month.day), projected_values=0.00, actual_values=0.00)
