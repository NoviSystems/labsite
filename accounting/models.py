from datetime import date
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django_fsm import FSMField, transition
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


def validate_positive(value):
    if value is not None and value < 0:
        raise ValidationError(_('Value must be a positive number.'))


class BusinessUnit(models.Model):
    name = models.CharField(max_length=64)
    account_number = models.CharField(max_length=12)

    users = models.ManyToManyField(User, through='UserTeamRole', related_name='business_units')

    def __str__(self):
        return self.name


class UserTeamRole(models.Model):
    ROLES = choices((
        ('MANAGER', _('Manager')),
        ('VIEWER', _('Viewer')),
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
        ('NEW', _('New')),
        ('ACTIVE', _('Active')),
        ('COMPLETE', _('Complete')),
    ))
    TYPES = choices((
        ('FIXED', _('Fixed')),
        ('HOURLY', _('Hourly')),
    ))
    business_unit = models.ForeignKey(BusinessUnit, on_delete=models.CASCADE)
    contract_id = models.CharField(max_length=64, unique=True, verbose_name=_("contract ID"))
    name = models.CharField(max_length=255, verbose_name=_("contract name"))
    start_date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[validate_positive])
    state = FSMField(max_length=8, choices=STATES, default=STATES.NEW)
    type = models.CharField(max_length=8, choices=TYPES)

    def __str__(self):
        return '%s: %s' % (self.contract_id, self.name)

    def get_invoices_predicted_total(self):
        aggregate = models.Sum(
            'predicted_amount',
            output_field=models.DecimalField(max_digits=10, decimal_places=2, default=0)
        )
        return self.invoice_set.all().aggregate(amount=aggregate)['amount']

    def get_unreceived_invoices(self):
        return self.invoice_set.filter(actual_amount=None) | \
            self.invoice_set.exclude(state=Invoice.STATES.RECEIVED)

    def has_invoice(self):
        return self.invoice_set.exists()

    def amount_matches_invoices(self):
        # The predicted amount of all invoices should match the contract's dollar amount.
        return self.amount == self.get_invoices_predicted_total()

    def all_invoices_received(self):
        return not self.get_unreceived_invoices().exists()

    @transition(field=state, source=STATES.NEW, target=STATES.ACTIVE, conditions=[has_invoice, amount_matches_invoices])
    def activate(self):
        """
        Mark the Contract as active.
        """

        for idx, invoice in enumerate(self.invoice_set.order_by('date'), start=1):
            invoice.invoice_id = "%s-%02d" % (self.contract_id, idx)
            invoice.save()

    @transition(field=state, source=STATES.ACTIVE, target=STATES.COMPLETE, conditions=[all_invoices_received])
    def complete(self):
        """
        Mark the contract as complete.
        """


class LineItem(models.Model):
    business_unit = models.ForeignKey(BusinessUnit, on_delete=models.CASCADE)
    predicted_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    actual_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=None)

    class Meta():
        abstract = True


class Invoice(LineItem):
    STATES = choices((
        ('NOT_INVOICED', _('Not Invoiced')),
        ('INVOICED', _('Invoiced')),
        ('RECEIVED', _('Received')),
    ))
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE)
    # Invoice IDs are generated by the contract when transitioning from the 'new' to 'active' state. Although it
    # goes against general advice, the charfield is made nullable in order to bypass the uniqueness constraint.
    invoice_id = models.CharField(max_length=64, unique=True, null=True, editable=False, verbose_name=_("invoice ID"))
    date = models.DateField()
    state = models.CharField(max_length=15, choices=STATES, default=STATES.NOT_INVOICED)

    class Meta:
        unique_together = ('contract', 'date')

    def __str__(self):
        return self.invoice_id or "Invoice: %d" % self.pk


class MonthlyBalance(LineItem):
    # Date field isn't entirely appropriate, since items are associated by month.
    month = models.SmallIntegerField(choices=MONTHS, default=MONTHS._1)
    year = models.SmallIntegerField(default=current_year)

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
