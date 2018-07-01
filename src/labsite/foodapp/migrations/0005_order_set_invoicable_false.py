# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2016-09-27 18:41
from __future__ import unicode_literals

from django.db import migrations


def set_invoicable(apps, schema_editor):

    Order = apps.get_model("foodapp", "Order")
    Order.objects.filter(invoice_item=None).update(is_invoiceable=False)


class Migration(migrations.Migration):

    dependencies = [
        ('foodapp', '0004_order_is_invoiceable'),
    ]

    operations = [
        migrations.RunPython(set_invoicable),
    ]