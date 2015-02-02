from django.db import models
from django.contrib.auth.models import User
import datetime

class Item(models.Model):
    name = models.CharField(max_length=56)
    description = models.CharField(max_length=256)
    once_a_day = models.BooleanField()

    def __unicode__(self):
        return '%s: %s' % (self.name, self.description,)

    class Meta:
        verbose_name = "Item"
        verbose_name_plural = "Items"


class Order(models.Model):
    user = models.ForeignKey(User, related_name='orders')
    date = models.DateField(default=datetime.date.today)
    item = models.ForeignKey(Item)
    QUANTITY_CHOICES = (
        (1, "one"),
        (2, "two"),
        (3, "three"),
        (4, "four"),
        (5, "five"),
    )
    quantity = models.PositiveSmallIntegerField(choices=QUANTITY_CHOICES, default=1)

    def __unicode__(self):
        return "%d %s(s) on %s." % (self.quantity, self.item.name, self.date)

    class Meta:
        verbose_name = "Order"
        verbose_name_plural = "Orders"
        ordering = ["date"]


class RiceCooker(models.Model):
    is_on = models.BooleanField()

    def __unicode__(self):
        return "%s." % (self.is_on)


class MonthlyCost(models.Model):
    cost  = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(default=datetime.date.today)

    def __unicode__(self):
        return "$%3.2f on %s." % (self.cost, self.date)

class AmountPaid(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(default=datetime.date.today)
    user = models.ForeignKey(User)
    def __unicode__(self):
        return "$%3.2f by %s on %s" % (self.amount, self.user, self.date) 
