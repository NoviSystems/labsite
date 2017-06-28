
from collections import namedtuple
from datetime import date

from django.utils.formats import number_format
from django.utils.safestring import mark_safe


def get_or_none(queryset):
    try:
        return queryset.get()
    except queryset.model.DoesNotExist:
        return None


def format_currency(value, decimal=True, html=True):
    if value is None:
        return ''

    # For display purposes, we can drop the cents. It only matters that the
    # true value is stored in the database and is used in calculations.
    value = number_format(value, decimal_pos=2 if decimal else 0, force_grouping=True)
    if not html:
        return '$ %s' % value
    return mark_safe('<span class="currency"><i class="fa fa-usd"></i> %s</span>' % value)


class Month(namedtuple('Month', ['year', 'month'])):

    def __new__(cls, *args, **kwargs):
        # allow date-like object as sole positional argument
        if len(args) == 1 and not kwargs and not isinstance(args[0], int):
            return super(Month, cls).__new__(cls, args[0].year, args[0].month)
        return super(Month, cls).__new__(cls, *args, **kwargs)

    @classmethod
    def range(cls, start, to):
        assert start < to

        months = []
        current = start
        while current != to:
            months.append(current)
            current = cls.next(current)

        return months

    @classmethod
    def offset(cls, date, months):
        month = date.month + months

        year = date.year + ((month - 1) // 12)
        month = ((month - 1) % 12) + 1

        return Month(year, month)

    @classmethod
    def next(cls, date):
        return cls.offset(date, 1)

    @classmethod
    def prev(cls, date):
        return cls.offset(date, -1)

    def as_date(self):
        return date(self.year, self.month, 1)

    def get_month_display(self):
        return self.as_date().strftime('%B')


class FiscalCalendar:

    def __init__(self, fiscal_year=None):
        self.fiscal_year = fiscal_year

        if fiscal_year is None:
            self.fiscal_year = self.get_fiscal_year(date.today())

    def __str__(self):
        return "FY %d" % self.fiscal_year

    def __repr__(self):
        return '<%(cls)s fiscal_year=%(fiscal_year)s>' % {
            'cls': self.__class__.__name__,
            'fiscal_year': self.fiscal_year,
        }

    @staticmethod
    def get_start_date(fiscal_year):
        return date(fiscal_year - 1, 7, 1)

    @staticmethod
    def get_end_date(fiscal_year):
        return date(fiscal_year, 6, 30)

    @classmethod
    def get_fiscal_year(cls, calendar_date):
        calendar_year = calendar_date.year

        # if the date is before the start of the fiscal year, then we're in the previous fiscal year
        if calendar_date < cls.get_start_date(calendar_year):
            return calendar_year - 1
        return calendar_year

    @property
    def start_date(self):
        return self.get_start_date(self.fiscal_year)

    @property
    def end_date(self):
        return self.get_end_date(self.fiscal_year)

    @property
    def months(self):
        start = Month(self.start_date)
        end = Month.next(self.end_date)

        return Month.range(start, end)
