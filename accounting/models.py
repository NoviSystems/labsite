from datetime import date
from decimal import Decimal

from django.apps import apps
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q, Value as V, Sum
from django.db.models.functions import Coalesce
from django.utils.translation import ugettext_lazy as _
from django_fsm import FSMField, transition
from itng.common.utils import choices

from accounting.utils import Month, get_or_none

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


def validate_percentile(value):
    if value is not None and value > 1:
        raise ValidationError(_('Value must be less than or equal to 1'))


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
    customer = models.CharField(max_length=255, verbose_name=_("Customer"), blank=True)
    description = models.CharField(max_length=255, verbose_name=_("Description"), blank=True)
    start_date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[validate_positive])
    state = FSMField(max_length=8, choices=STATES, default=STATES.NEW)
    type = models.CharField(max_length=8, choices=TYPES)
    notes = models.TextField(verbose_name="Notes", blank=True)

    def __str__(self):
        return '%s: %s' % (self.contract_id, self.name)

    def outstanding_amount(self):
        total_received = self.invoice_set \
            .filter(state=Invoice.STATES.RECEIVED) \
            .aggregate(v=Coalesce(Sum('actual_amount'), V(Decimal(0))))['v']
        return self.amount - total_received

    def get_invoices_expected_total(self):
        aggregate = models.Sum(
            'expected_amount',
            output_field=models.DecimalField(max_digits=10, decimal_places=2, default=0)
        )
        return self.invoice_set.all().aggregate(amount=aggregate)['amount']

    def get_unreceived_invoices(self):
        return self.invoice_set.filter(actual_amount=None) | \
            self.invoice_set.exclude(state=Invoice.STATES.RECEIVED)

    def has_invoice(self):
        return self.invoice_set.exists()

    def amount_matches_invoices(self):
        # The expected amount of all invoices should match the contract's dollar amount.
        return self.amount == self.get_invoices_expected_total()

    def all_invoices_received(self):
        return not self.get_unreceived_invoices().exists()

    @transition(field=state, source=STATES.NEW, target=STATES.ACTIVE, conditions=[has_invoice, amount_matches_invoices])
    def activate(self):
        """
        Mark the Contract as active.
        """

        for idx, invoice in enumerate(self.invoice_set.order_by('expected_invoice_date'), start=1):
            invoice.invoice_id = "%s-%02d" % (self.contract_id, idx)
            invoice.save()

    @transition(field=state, source=STATES.ACTIVE, target=STATES.COMPLETE, conditions=[all_invoices_received])
    def complete(self):
        """
        Mark the contract as complete.
        """


class Prospect(models.Model):
    TYPES = choices((
        ('FIXED', _('Fixed')),
        ('HOURLY', _('Hourly')),
    ))
    name = models.CharField(max_length=255, verbose_name=_("Name"))
    business_unit = models.ForeignKey(BusinessUnit, on_delete=models.CASCADE)
    description = models.CharField(max_length=255, verbose_name=_("Description"))
    est_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[validate_positive])
    probability = models.FloatField(default=0, validators=[validate_positive, validate_percentile])

    def __str__(self):
        return '%s: %s' % (self.id, self.name)


class LineItem(models.Model):
    business_unit = models.ForeignKey(BusinessUnit, on_delete=models.CASCADE)
    expected_amount = models.DecimalField(max_digits=10, decimal_places=2)
    actual_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=None)

    class Meta():
        abstract = True


class Invoice(LineItem):
    STATES = choices((
        ('NOT_INVOICED', _('Not Invoiced')),
        ('INVOICED', _('Invoiced')),
        ('RECEIVED', _('Received')),
    ))
    # Invoice IDs are generated by the contract when transitioning from the 'new' to 'active' state. Although it
    # goes against general advice, the charfield is made nullable in order to bypass the uniqueness constraint.
    invoice_id = models.CharField(max_length=64, unique=True, null=True, editable=False, verbose_name=_("invoice ID"))
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE)
    state = models.CharField(max_length=15, choices=STATES, default=STATES.NOT_INVOICED)

    expected_invoice_date = models.DateField()
    expected_payment_date = models.DateField()
    actual_invoice_date = models.DateField(null=True, blank=True)
    actual_payment_date = models.DateField(null=True, blank=True)

    class Meta:
        # The unique_together constraint soft requirement:
        # - expected invoice date is used for ordering before the ID is created.
        # - It doesn't really make sense to expect two separate invoices on the
        #   same date for the same contract.
        # - This can easily be removed if necessary
        unique_together = ('contract', 'expected_invoice_date')

    def __str__(self):
        return self.invoice_id or "Invoice: %d" % self.pk


class MonthlyQuerySet(models.QuerySet):
    # TODO: define before/after if useful

    def range(self, start, stop, inclusive=True):
        # While counterintuitive, we're mostly dealing with inclusive month ranges.
        # eg, FY 2016 starts on July 2016 and ends in June of 2017.

        # coerce date-likes to Month types.
        start, stop = Month(start), Month(stop)

        # ensure start is before stop
        if start > stop:
            start, stop = stop, start

        if inclusive:
            stop = Month.next(stop)

        return self.filter(
            Q(year=start.year, month__gte=start.month) |
            Q(year__gt=start.year, year__lt=stop.year) |
            Q(year=stop.year, month__lt=stop.month)
        )


class MonthlyReconcile(models.Model):
    business_unit = models.ForeignKey(BusinessUnit, on_delete=models.CASCADE)

    # Date field isn't entirely appropriate, since items are associated by month.
    month = models.SmallIntegerField(choices=MONTHS, default=MONTHS._1)
    year = models.SmallIntegerField(default=current_year)

    objects = MonthlyQuerySet.as_manager()

    class Meta:
        unique_together = ('month', 'year')
        ordering = ('-year', '-month')

    def __repr__(self):
        return '<%s: %s>' % (self.__class__.__name__, str(self), )

    def __str__(self):
        return "%4d-%02d (%s)" % (self.year, self.month, self.business_unit, )


class MonthlyBalance(LineItem):
    # Date field isn't entirely appropriate, since items are associated by month.
    month = models.SmallIntegerField(choices=MONTHS, default=MONTHS._1)
    year = models.SmallIntegerField(default=current_year)

    objects = MonthlyQuerySet.as_manager()

    class Meta:
        unique_together = ('month', 'year')
        ordering = ('-year', '-month')
        abstract = True

    def __repr__(self):
        return '<%s: %s>' % (self.__class__.__name__, str(self), )

    def __str__(self):
        return "%4d-%02d (%s)" % (self.year, self.month, self.business_unit, )


class CashBalance(MonthlyBalance):
    """
    The actual "cash on hand" balance per month.
    """
    @property
    def expected_amount(self):
        """
        Formula:
            - use *last* month's cash balance
            - add this month's billable invoices
            - subtract this month's expenses
        """
        # carry over last month's cash balance
        cash_balance = Decimal(0)
        if self.previous_cashbalance is not None:
            # preference actual cash balance over expected
            cash_balance = self.previous_cashbalance.actual_amount \
                or self.previous_cashbalance.expected_amount

        # sum all billable invoices
        income = Invoice.objects \
            .filter(
                business_unit=self.business_unit,
                expected_payment_date__year=self.year,
                expected_payment_date__month=self.month) \
            .exclude(contract__state=Contract.STATES.NEW) \
            .aggregate(v=Coalesce(Sum('expected_amount'), V(Decimal(0))))['v']

        # sum all expenses
        expenses = Decimal(0)
        for inst in [self.expenses, self.permanent_payroll, self.temporary_payroll]:
            if inst is not None:
                expenses += inst.expected_amount or 0

        return cash_balance + income - expenses

    @property
    def previous_balance_kwargs(self):
        previous = Month.prev(self)
        return {
            'business_unit': self.business_unit,
            'year': previous.year,
            'month': previous.month,
        }

    @property
    def balance_kwargs(self):
        return {
            'business_unit': self.business_unit,
            'year': self.year,
            'month': self.month,
        }

    def balance_property(model_name, kwargs_name):
        def fget(self):
            model = apps.get_model('accounting', model_name)
            name = '_previous_%s' % model.__name__.lower()

            if not hasattr(self, name):
                kwargs = getattr(self, kwargs_name)
                setattr(self, name, get_or_none(model.objects.filter(**kwargs)))

            return getattr(self, name)

        def fset(self, value):
            model = apps.get_model('accounting', model_name)
            name = '_previous_%s' % model.__name__.lower()

            setattr(self, name, value)

        return property(**{'fget': fget, 'fset': fset})

    previous_cashbalance = balance_property('CashBalance', 'previous_balance_kwargs')
    expenses = balance_property('Expenses', 'balance_kwargs')
    permanent_payroll = balance_property('PermanentPayroll', 'balance_kwargs')
    temporary_payroll = balance_property('TemporaryPayroll', 'balance_kwargs')


class Expenses(MonthlyBalance):
    """
    The total miscelaneous expenses for a month. (eg, phone bill + electric + ...)
    """


class PermanentPayroll(MonthlyBalance):
    """
    The full time payroll costs for a month.
    """


class TemporaryPayroll(MonthlyBalance):
    """
    The part time payroll costs for a month.
    """
