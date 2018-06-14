from datetime import date
from unittest import TestCase

from accounting.utils import FiscalCalendar, Month


class MonthTestCase(TestCase):
    def setUp(self):
        self.base = Month(2016, 1)

    def test_positive_offset(self):
        self.assertEqual(Month.offset(self.base, 6), Month(2016, 7))
        self.assertEqual(Month.offset(self.base, 9), Month(2016, 10))
        self.assertEqual(Month.offset(self.base, 12), Month(2017, 1))
        self.assertEqual(Month.offset(self.base, 15), Month(2017, 4))
        self.assertEqual(Month.offset(self.base, 18), Month(2017, 7))

        self.assertEqual(Month.offset(self.base, 11), Month(2016, 12))
        self.assertEqual(Month.offset(self.base, 12), Month(2017, 1))
        self.assertEqual(Month.offset(self.base, 13), Month(2017, 2))

    def test_negative_offset(self):
        self.assertEqual(Month.offset(self.base, -6), Month(2015, 7))
        self.assertEqual(Month.offset(self.base, -9), Month(2015, 4))
        self.assertEqual(Month.offset(self.base, -12), Month(2015, 1))
        self.assertEqual(Month.offset(self.base, -15), Month(2014, 10))
        self.assertEqual(Month.offset(self.base, -18), Month(2014, 7))

        self.assertEqual(Month.offset(self.base, -11), Month(2015, 2))
        self.assertEqual(Month.offset(self.base, -12), Month(2015, 1))
        self.assertEqual(Month.offset(self.base, -13), Month(2014, 12))

    def test_next(self):
        self.assertEqual(Month.next(self.base), Month(2016, 2))

    def test_prev(self):
        self.assertEqual(Month.prev(self.base), Month(2015, 12))


class FiscalCalendarTestCase(TestCase):
    def test_get_fiscal_year(self):
        self.assertEquals(FiscalCalendar.get_fiscal_year(date(2016, 7, 1)), 2017)
        self.assertEquals(FiscalCalendar.get_fiscal_year(date(2016, 6, 1)), 2016)
        self.assertEquals(FiscalCalendar.get_fiscal_year(date(2016, 1, 1)), 2016)
        self.assertEquals(FiscalCalendar.get_fiscal_year(date(2016, 12, 1)), 2017)
        self.assertEquals(FiscalCalendar.get_fiscal_year(date(2016, 8, 1)), 2017)
