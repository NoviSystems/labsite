
from django.db import models
from django.contrib.auth.models import User


class BusinessUnit(models.Model):
    name = models.CharField(max_length=64, verbose_name='Name')
    account_number = models.CharField(max_length=12, verbose_name='Account Number')

    def __str__(self):
        return self.name


class UserTeamRole(models.Model):
    ROLE_STATE = (
        ('MANAGER', 'Manager'),
        ('VIEWER', 'Viewer'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='User')
    business_unit = models.ForeignKey(BusinessUnit, on_delete=models.CASCADE, verbose_name='Business Unit')
    role = models.CharField(max_length=12, choices=ROLE_STATE, verbose_name='Role')

    class Meta:
        unique_together = ['user', 'business_unit']

    def __str__(self):
        return '%s is a %s of %s' % (self.user.username, self.role, self.business_unit.name)


class LineItem(models.Model):
    business_unit = models.ForeignKey(BusinessUnit, verbose_name='Business Unit')
    predicted_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name='Predicted Amount')
    actual_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name='Actual Amount')
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
    CONTRACT_STATE = (
        ('ACTIVE', 'Active'),
        ('COMPLETE', 'Complete'),
    )
    CONTRACT_TYPE = (
        ('FIXED', 'Fixed'),
        ('HOURLY', 'Hourly'),
    )
    business_unit = models.ForeignKey(BusinessUnit, on_delete=models.CASCADE, verbose_name='Business Unit')
    department = models.CharField(max_length=4, default='CSC', verbose_name='Department')
    contract_number = models.IntegerField(verbose_name='Contract Number')
    organization_name = models.CharField(max_length=255, verbose_name='Contract Name')
    start_date = models.DateField(verbose_name='Start Date')
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name='Amount')
    contract_state = models.CharField(max_length=8, choices=CONTRACT_STATE, verbose_name='Contract State')
    contract_type = models.CharField(max_length=8, choices=CONTRACT_TYPE, verbose_name='Contract Type')


class Income(LineItem):
    name = models.CharField(max_length=50, verbose_name='Name')
    date_payable = models.DateField(verbose_name='Date Payable')
    date_paid = models.DateField(default=None, null=True, blank=True, verbose_name='Date Paid')


class Invoice(Income):
    TRANSITION_STATE = (
        ('INVOICED', 'Invoiced'),
        ('NOT_INVOICED', 'Not Invoiced'),
        ('RECEIVED', 'Received'),
    )
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, verbose_name='Contract')
    number = models.IntegerField(verbose_name='Number')
    transition_state = models.CharField(max_length=15, choices=TRANSITION_STATE, verbose_name='Transition State')


class Expense(LineItem):
    EXPENSE_TYPE = (
        ('GENERAL', 'General'),
        ('PAYROLL', 'Payroll'),
    )
    expense_type = models.CharField(max_length=7, choices=EXPENSE_TYPE, verbose_name='Expense Type')
    name = models.CharField(max_length=50, verbose_name='Name')
    date_payable = models.DateField(verbose_name='Date Payable')
    date_paid = models.DateField(default=None, null=True, blank=True, verbose_name='Date Paid')


class Cash(LineItem):
    name = models.CharField(max_length=50, verbose_name='Name')
    date_associated = models.DateField(verbose_name='Date Associated')
