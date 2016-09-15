from datetime import date, datetime, timedelta
from calendar import monthrange

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User

__all__ = ['BusinessUnit', 'UserTeamRole', 'FiscalYear', 'Month', 'LineItem', 'Contract', 'Cash', 'Income', 'Invoice', 'Personnel', 'Salary', 'PartTime', 'Expense', 'Payroll']

class BusinessUnit(models.Model):
    name = models.CharField(max_length=64, verbose_name='Name')
    account_number = models.CharField(max_length=12, verbose_name='Account Number')

    def __str__(self):
        return self.name


class UserTeamRole(models.Model):
    ROLE_STATE = {
        ('MANAGER', "manager"),
        ('VIEWER', "viewer"),
    }
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='User')
    business_unit = models.ForeignKey(BusinessUnit, on_delete=models.CASCADE, verbose_name='Business Unit')
    role = models.CharField(max_length=12, choices=ROLE_STATE, verbose_name='Role')

    class Meta:
        unique_together = ['user', 'business_unit']

    def __str__(self):
        return self.user.username + ' is a ' + self.role + ' of ' + self.business_unit.name


class FiscalYear(models.Model):
    business_unit = models.ForeignKey(BusinessUnit, verbose_name='Business Unit')
    start_date = models.DateField(verbose_name='Start Date')
    end_date = models.DateField(default=datetime.now, blank=True, verbose_name='End Date')
    cash_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0.00, verbose_name='Cash Amount')

    def __str__(self):
        return self.start_date.strftime("%b %Y") + " - " + self.end_date.strftime("%b %Y")


class Month(models.Model):
    fiscal_year = models.ForeignKey(FiscalYear, default=None, verbose_name='Fiscal Year')
    month = models.DateField(verbose_name='Month')
    projected_values = models.DecimalField(max_digits=8, decimal_places=2, default=0.00, verbose_name='Projected Values')
    actual_values = models.DecimalField(max_digits=8, decimal_places=2, default=0.00, verbose_name='Actual Values')

    def __str__(self):
        return self.fiscal_year.business_unit.name + " " + self.month.strftime("%b %Y")


class LineItem(models.Model):
    business_unit = models.ForeignKey(BusinessUnit, verbose_name='Business Unit')
    month = models.ForeignKey(Month, verbose_name='Month')
    predicted_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0.00, verbose_name='Predicted Amount')
    actual_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0.00, verbose_name='Actual Amount')
    reconciled = models.BooleanField(default=False, verbose_name='Reconciled')


class Contract(models.Model):
    CONTRACT_STATE = {
        ('ACTIVE', "active"),
        ('COMPLETE', "complete"),
    }
    CONTRACT_TYPE = {
        ('FIXED', "fixed"),
        ('HOURLY', "hourly"),
    }

    business_unit = models.ForeignKey(BusinessUnit, on_delete=models.CASCADE, verbose_name='Business Unit')
    department = models.CharField(max_length=4, default='CSC', verbose_name='Department')
    contract_number = models.IntegerField(verbose_name='Contract Number')
    organization_name = models.CharField(max_length=255, verbose_name='Organization Name')
    start_date = models.DateField(verbose_name='Start Date')
    amount = models.DecimalField(max_digits=8, decimal_places=2, default=0.00, verbose_name='Amount')
    contract_state = models.CharField(max_length=8, choices=CONTRACT_STATE, verbose_name='Contract State')
    contract_type = models.CharField(max_length=8, choices=CONTRACT_TYPE, verbose_name='Contract Type')


class Cash(LineItem):
    name = models.CharField(max_length=50, verbose_name='Name')


class Income(LineItem):
    name = models.CharField(max_length=50, verbose_name='Name')
    date_payable = models.DateField(verbose_name='Date Payable')
    date_payed = models.DateField(default=None, null=True, verbose_name='Date Payed')


class Invoice(Income):
    TRANSITION_STATE = {
        ('INVOICED', "invoiced"),
        ('NOT_INVOICED', "not invoiced"),
        ('RECIEVED', "recieved"),
    }

    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, verbose_name='Contract')
    number = models.IntegerField(verbose_name='Number')
    transition_state = models.CharField(max_length=15, choices=TRANSITION_STATE, verbose_name='Transition State')


class Personnel(models.Model):
    business_unit = models.ForeignKey(BusinessUnit, verbose_name='Business Unit')
    first_name = models.CharField(max_length=50, verbose_name='First Name')
    last_name = models.CharField(max_length=50, verbose_name='Last Name')
    employee_id = models.IntegerField(verbose_name='Employee ID')
    position = models.CharField(max_length=50, verbose_name='Position')


class Salary(Personnel):
    SALARY_TYPE = {
        ('EPA', 'EPA'),
        ('SPA', 'SPA'),
    }

    salary_type = models.CharField(max_length=3, choices=SALARY_TYPE, verbose_name='Salary Type')
    salary_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0.00, verbose_name='Salary')
    social_security_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0.00, verbose_name='Social Security Amount')
    fed_health_insurance_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0.00, verbose_name='Federal health Insurance Amount')
    retirement_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0.00, verbose_name='retirement_amount')
    medical_insurance_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0.00, verbose_name='Medical Insurance Amount')
    staff_benefits_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0.00, verbose_name='Staff Benefits Amount')
    fringe_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0.00, verbose_name='Fringe Amount')


class PartTime(Personnel):
    HOURLY_TYPE = {
        ('STUDENT', 'student'),
        ('NON_STUDENT', 'non student')
    }
    hourly_type = models.CharField(max_length=12, choices=HOURLY_TYPE, verbose_name='Hourly Type')
    hourly_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0.00, verbose_name='Hourly Amount')
    hours_work = models.IntegerField(verbose_name='Hours Worked')


class Expense(LineItem):
    name = models.CharField(max_length=50, verbose_name='Name')
    date_payable = models.DateField(verbose_name='Date Payable')
    date_paid = models.DateField(default=None, null=True, verbose_name='Date Paid')


class Payroll(models.Model):
    month = models.OneToOneField(Month, verbose_name='Payroll')
    expense = models.OneToOneField(Expense, verbose_name='Expense')

    def delete(self, *args, **kwargs):
        self.expense.delete()
        return super(self.__class__, self).delete(*args, **kwargs)


@receiver(post_save, sender=FiscalYear, dispatch_uid="createItemsForFiscalYear")
def createItemsForFiscalYear(sender, instance, **kwargs):
    start_month = instance.start_date
    end_month = instance.end_date
    number_of_months = monthdelta(start_month, end_month)

    month = start_month.month
    year = start_month.year
    day = start_month.day
    for i in range(number_of_months + 1):
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
