# -*- coding: utf-8 -*-
# Generated by Django 1.9.10 on 2016-10-12 18:46
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodapp', '0006_auto_20161012_1446'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='invoiceitem_id',
            field=models.CharField(blank=True, default='', max_length=36),
            preserve_default=False,
        ),
    ]
