
from django.conf import settings
from django.db import models
from itng.common.utils import choices

User = settings.AUTH_USER_MODEL


class BusinessUnit(models.Model):
    name = models.CharField(max_length=64)
    account_number = models.CharField(max_length=12)

    users = models.ManyToManyField(User, through='UserTeamRole', related_name='business_units')

    def __str__(self):
        return self.name


class UserTeamRole(models.Model):
    ROLES = choices((
        ('MANAGER', 'Manager'),
        ('VIEWER', 'Viewer'),
    ))
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    business_unit = models.ForeignKey(BusinessUnit, on_delete=models.CASCADE)
    role = models.CharField(max_length=12, choices=ROLES, default=ROLES.VIEWER)

    class Meta:
        unique_together = ['user', 'business_unit']

    def __str__(self):
        return '%s is a %s of %s' % (self.user.username, self.role, self.business_unit.name)


class LineItem(models.Model):
    business_unit = models.ForeignKey(BusinessUnit)
    predicted_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    actual_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    reconciled = models.BooleanField(default=False)

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
    STATES = choices((
        ('ACTIVE', 'Active'),
        ('COMPLETE', 'Complete'),
    ))
    TYPES = choices((
        ('FIXED', 'Fixed'),
        ('HOURLY', 'Hourly'),
    ))
    business_unit = models.ForeignKey(BusinessUnit, on_delete=models.CASCADE)
    department = models.CharField(max_length=4, default='CSC')
    contract_number = models.IntegerField()
    organization_name = models.CharField(max_length=255, verbose_name='Contract Name')
    start_date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    state = models.CharField(max_length=8, choices=STATES, default=STATES.ACTIVE)
    type = models.CharField(max_length=8, choices=TYPES)


class Income(LineItem):
    name = models.CharField(max_length=50)
    date_payable = models.DateField()
    date_paid = models.DateField(default=None, null=True, blank=True)


class Invoice(Income):
    STATES = choices((
        ('NOT_INVOICED', 'Not Invoiced'),
        ('INVOICED', 'Invoiced'),
        ('RECEIVED', 'Received'),
    ))
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE)
    number = models.IntegerField()
    transition_state = models.CharField(max_length=15, choices=STATES, default=STATES.NOT_INVOICED)


class Expense(LineItem):
    EXPENSE_TYPES = choices((
        ('GENERAL', 'General'),
        ('PAYROLL', 'Payroll'),
    ))
    expense_type = models.CharField(max_length=7, choices=EXPENSE_TYPES)
    name = models.CharField(max_length=50)
    date_payable = models.DateField()
    date_paid = models.DateField(default=None, null=True, blank=True)


class Cash(LineItem):
    name = models.CharField(max_length=50)
    date_associated = models.DateField()
