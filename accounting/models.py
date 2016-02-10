from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType

# Create your models here.
class FiscalYear(models.Model):
    start_month = models.DateField()
    number_of_months = models.IntegerField()


class Month(models.Model):
    month = models.DateField()
    projected_values = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    actual_values = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)


class Contract(models.Model):
    CONTRACT_STATE = {
        ('ACTIVE', "active" ),
        ('COMPLETE', "complete" ),
    }
    CONTRACT_TYPE = {
        ('FIXED', "fixed" ),
        ('HOURLY', "hourly" ),
    }

    contract_number = models.IntegerField()
    organization_name = models.CharField(max_length=255)
    start_date = models.DateField()
    contract_state = models.CharField(max_length=8, choices=CONTRACT_STATE)
    contract_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    contract_type = models.CharField(max_length=8, choices=CONTRACT_TYPE)
    

class Invoice(models.Model):
    TRANSATION_STATE = {
        ('INVOICED', "invoiced"),
        ('NOT_INVOICED', "not invoiced"),
        ('RECIEVED', "recieved"),
    }

    invoice_number = models.IntegerField()
    invoice_date = models.DateField()
    invoice_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    transation_state = models.CharField(max_length=15, choices=TRANSATION_STATE)
    lineItem = GenericRelation(LineItem)


class Personnel(models.Model):
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


class Expense(models.Model):
    name = models.CharField(max_length=50)
    Expense_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    data_payable = models.DateField()
    date_payed = models.DateField()
    reoccuring = models.IntegerField()
    lineItem = GenericRelation(LineItem)


class LineItem(models.Model):
    month = models.ForeignKey(Month)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    predicted_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    actual_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)

