# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-04-04 17:52
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('worklog', '0004_auto_20170201_1356'),
    ]

    operations = [
        migrations.RenameField(
            model_name='job',
            old_name='do_not_invoice',
            new_name='invoiceable',
        ),
    ]
