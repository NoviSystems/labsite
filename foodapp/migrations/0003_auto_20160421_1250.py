# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-04-21 16:50
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodapp', '0002_auto_20160404_1328'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='invoiced',
        ),
        migrations.AddField(
            model_name='order',
            name='invoice_item',
            field=models.CharField(max_length=36, null=True),
        ),
    ]
