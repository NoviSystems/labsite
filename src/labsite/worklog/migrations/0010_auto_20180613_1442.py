# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-06-13 18:42
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('worklog', '0009_auto_20170404_1653'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='githubalias',
            name='user',
        ),
        migrations.RemoveField(
            model_name='issue',
            name='assignee',
        ),
        migrations.RemoveField(
            model_name='issue',
            name='repo',
        ),
        migrations.RemoveField(
            model_name='workitem',
            name='issue',
        ),
        migrations.RemoveField(
            model_name='workitem',
            name='repo',
        ),
        migrations.DeleteModel(
            name='GithubAlias',
        ),
        migrations.DeleteModel(
            name='Issue',
        ),
        migrations.DeleteModel(
            name='Repo',
        ),
    ]
