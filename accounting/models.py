from datetime import date, datetime, timedelta
from calendar import monthrange

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User

__all__ = ['BusinessUnit', 'UserTeamRole', 'LineItem', 'Contract', 'Cash', 'Income', 'Invoice', 'Personnel', 'FullTime', 'PartTime', 'Expense', 'Payroll']

class BusinessUnit(models.Model):
    name = models.CharField(max_length=64, verbose_name='Name')
    account_number = models.CharField(max_length=12, verbose_name='Account Number')

    def __unicode__(self):
        return self.name


class UserTeamRole(models.Model):
    ROLE_STATE = {
        ('MANAGER', 'Manager'),
        ('VIEWER', 'Viewer'),
    }
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='User')
    business_unit = models.ForeignKey(BusinessUnit, on_delete=models.CASCADE, verbose_name='Business Unit')
    role = models.CharField(max_length=12, choices=ROLE_STATE, verbose_name='Role')

    class Meta:
        unique_together = ['user', 'business_unit']

    def __unicode__(self):
        return self.user.username + ' is a ' + self.role + ' of ' + self.business_unit.name


class LineItem(models.Model):
    business_unit = models.ForeignKey(BusinessUnit, verbose_name='Business Unit')
    predicted_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0.00, verbose_name='Predicted Amount')
    actual_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0.00, verbose_name='Actual Amount')
    reconciled = models.BooleanField(default=False, verbose_name='Reconciled')

    @classmethod
    def from_db(cls, db, field_names, values):
        if cls._deferred:
            instance = cls(**zip(field_names, values))
        else:
            instance = cls(*values)
        instance._state.adding = False
        instance._state.db = db
        instance._loaded_values = dict(zip(field_names, values))
        return instance

    def save(self, *args, **kwargs):
        if not self._state.adding and (self.actual_amount != self._loaded_values['actual_amount']):
            self.reconciled = True
        super(LineItem, self).save(*args, **kwargs)

    class Meta():
        abstract = True


class Contract(models.Model):
    CONTRACT_STATE = {
        ('ACTIVE', 'Active'),
        ('COMPLETE', 'Complete'),
    }
    CONTRACT_TYPE = {
        ('FIXED', 'Fixed'),
        ('HOURLY', 'Hourly'),
    }

    business_unit = models.ForeignKey(BusinessUnit, on_delete=models.CASCADE, verbose_name='Business Unit')
    department = models.CharField(max_length=4, default='CSC', verbose_name='Department')
    contract_number = models.IntegerField(verbose_name='Contract Number')
    organization_name = models.CharField(max_length=255, verbose_name='Contract Name')
    start_date = models.DateField(verbose_name='Start Date')
    amount = models.DecimalField(max_digits=8, decimal_places=2, default=0.00, verbose_name='Amount')
    contract_state = models.CharField(max_length=8, choices=CONTRACT_STATE, verbose_name='Contract State')
    contract_type = models.CharField(max_length=8, choices=CONTRACT_TYPE, verbose_name='Contract Type')


class Cash(LineItem):
    name = models.CharField(max_length=50, verbose_name='Name')


class Income(LineItem):
    name = models.CharField(max_length=50, verbose_name='Name')
    date_payable = models.DateField(verbose_name='Date Payable')
    date_paid = models.DateField(default=None, null=True, blank=True, verbose_name='Date Paid')


class Invoice(Income):
    TRANSITION_STATE = {
        ('INVOICED', 'Invoiced'),
        ('NOT_INVOICED', 'Not Invoiced'),
        ('RECEIVED', 'Received'),
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

    class Meta:
        abstract = True


class FullTime(Personnel):
    SALARY_TYPE = {
        ('EPA', 'EPA'),
        ('SPA', 'SPA'),
    }
    salary_type = models.CharField(max_length=3, choices=SALARY_TYPE, verbose_name='Salary Type')
    salary_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0.00, verbose_name='Salary')
    social_security_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0.00, verbose_name='Social Security Amount')
    fed_health_insurance_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0.00, verbose_name='Federal Health Insurance Amount')
    retirement_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0.00, verbose_name='Retirement Amount')
    medical_insurance_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0.00, verbose_name='Medical Insurance Amount')
    staff_benefits_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0.00, verbose_name='Staff Benefits Amount')
    fringe_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0.00, verbose_name='Fringe Amount')


class PartTime(Personnel):
    HOURLY_TYPE = {
        ('STUDENT', 'Student'),
        ('NON_STUDENT', 'Non-Student')
    }
    hourly_type = models.CharField(max_length=12, choices=HOURLY_TYPE, verbose_name='Hourly Type')
    hourly_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0.00, verbose_name='Hourly Amount')
    hours_work = models.IntegerField(verbose_name='Hours Worked')


class Expense(LineItem):
    name = models.CharField(max_length=50, verbose_name='Name')
    date_payable = models.DateField(verbose_name='Date Payable')
    date_paid = models.DateField(default=None, null=True, blank=True, verbose_name='Date Paid')


class Payroll(models.Model):
    expense = models.OneToOneField(Expense, verbose_name='Expense')

    def delete(self, *args, **kwargs):
        self.expense.delete()
        return super(self.__class__, self).delete(*args, **kwargs)


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
