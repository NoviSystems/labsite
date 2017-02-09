
from collections import namedtuple
from datetime import date


class Month(namedtuple('Month', ['year', 'month'])):

    @classmethod
    def range(cls, start, to):
        assert start < to

        months = []
        current = start
        while current != to:
            months.append(current)
            current = cls.next_month(current)

        return months

    @classmethod
    def next_month(cls, date):
        month = date.month + 1

        year = date.year + ((month-1) // 12)
        month = ((month-1) % 12) + 1

        return Month(year, month)

    def as_date(self):
        return date(self.year, self.month, 1)

    def get_month_display(self):
        return self.as_date().strftime('%B')
