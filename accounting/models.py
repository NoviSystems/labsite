from datetime import date
from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from itng.common.utils import choices

User = settings.AUTH_USER_MODEL


MONTHS = choices((
    (1, _('January')),
    (2, _('February')),
    (3, _('March')),
    (4, _('April')),
    (5, _('May')),
    (6, _('June')),
    (7, _('July')),
    (8, _('August')),
    (9, _('September')),
    (10, _('October')),
    (11, _('November')),
    (12, _('December')),
))


def current_year():
    return date.today().year


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
    number = models.IntegerField(verbose_name='Contract Number')
    name = models.CharField(max_length=255, verbose_name='Contract Name')
    start_date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    state = models.CharField(max_length=8, choices=STATES, default=STATES.ACTIVE)
    type = models.CharField(max_length=8, choices=TYPES)

    def __str__(self):
        return '%d: %s' % (self.contract_number, self.name)


class LineItem(models.Model):
    business_unit = models.ForeignKey(BusinessUnit, on_delete=models.CASCADE)
    predicted_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    actual_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, default=None)

    # Date field isn't entirely appropriate, since items are associated by month.
    month = models.SmallIntegerField(choices=MONTHS, default=MONTHS._1)
    year = models.SmallIntegerField(default=current_year)

    class Meta():
        abstract = True


class Invoice(LineItem):
    STATES = choices((
        ('NOT_INVOICED', 'Not Invoiced'),
        ('INVOICED', 'Invoiced'),
        ('RECEIVED', 'Received'),
    ))
    name = models.CharField(max_length=50)
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE)
    number = models.PositiveIntegerField()
    state = models.CharField(max_length=15, choices=STATES, default=STATES.NOT_INVOICED)

    class Meta:
        unique_together = ('contract', 'number')


class MonthlyBalance(LineItem):
    class Meta:
        unique_together = ('month', 'year')
        abstract = True


class CashBalance(MonthlyBalance):
    """
    The actual "cash on hand" balance per month.

    Predictions are always computed from last month's results.
    """
    predicted_amount = None


class Expenses(MonthlyBalance):
    """
    The total miscelaneous expenses for a month. (eg, phone bill + electric + ...)
    """


class FullTimePayroll(MonthlyBalance):
    """
    The full time payroll costs for a month.
    """


class PartTimePayroll(MonthlyBalance):
    """
    The part time payroll costs for a month.
    """
