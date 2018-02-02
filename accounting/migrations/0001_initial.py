# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-28 21:34
from __future__ import unicode_literals

import accounting.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django_fsm


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='BusinessUnit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64)),
                ('account_number', models.CharField(max_length=12)),
            ],
        ),
        migrations.CreateModel(
            name='CashBalance',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('actual_amount', models.DecimalField(blank=True, decimal_places=2, default=None, max_digits=10, null=True)),
                ('month', models.SmallIntegerField(choices=[(1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'), (5, 'May'), (6, 'June'), (7, 'July'), (8, 'August'), (9, 'September'), (10, 'October'), (11, 'November'), (12, 'December')], default=1)),
                ('year', models.SmallIntegerField(default=accounting.models.current_year)),
                ('business_unit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounting.BusinessUnit')),
            ],
            options={
                'abstract': False,
                'ordering': ('-year', '-month'),
            },
        ),
        migrations.CreateModel(
            name='Contract',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('contract_id', models.CharField(max_length=64, unique=True, verbose_name='contract ID')),
                ('name', models.CharField(max_length=255, verbose_name='contract name')),
                ('start_date', models.DateField()),
                ('amount', models.DecimalField(decimal_places=2, default=0, max_digits=10, validators=[accounting.models.validate_positive])),
                ('state', django_fsm.FSMField(choices=[('NEW', 'New'), ('ACTIVE', 'Active'), ('COMPLETE', 'Complete')], default='NEW', max_length=8)),
                ('type', models.CharField(choices=[('FIXED', 'Fixed'), ('HOURLY', 'Hourly')], max_length=8)),
                ('business_unit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounting.BusinessUnit')),
            ],
        ),
        migrations.CreateModel(
            name='Expenses',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('expected_amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('actual_amount', models.DecimalField(blank=True, decimal_places=2, default=None, max_digits=10, null=True)),
                ('month', models.SmallIntegerField(choices=[(1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'), (5, 'May'), (6, 'June'), (7, 'July'), (8, 'August'), (9, 'September'), (10, 'October'), (11, 'November'), (12, 'December')], default=1)),
                ('year', models.SmallIntegerField(default=accounting.models.current_year)),
                ('business_unit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounting.BusinessUnit')),
            ],
            options={
                'abstract': False,
                'ordering': ('-year', '-month'),
            },
        ),
        migrations.CreateModel(
            name='FullTimePayroll',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('expected_amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('actual_amount', models.DecimalField(blank=True, decimal_places=2, default=None, max_digits=10, null=True)),
                ('month', models.SmallIntegerField(choices=[(1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'), (5, 'May'), (6, 'June'), (7, 'July'), (8, 'August'), (9, 'September'), (10, 'October'), (11, 'November'), (12, 'December')], default=1)),
                ('year', models.SmallIntegerField(default=accounting.models.current_year)),
                ('business_unit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounting.BusinessUnit')),
            ],
            options={
                'abstract': False,
                'ordering': ('-year', '-month'),
            },
        ),
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('expected_amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('actual_amount', models.DecimalField(blank=True, decimal_places=2, default=None, max_digits=10, null=True)),
                ('invoice_id', models.CharField(editable=False, max_length=64, null=True, unique=True, verbose_name='invoice ID')),
                ('state', models.CharField(choices=[('NOT_INVOICED', 'Not Invoiced'), ('INVOICED', 'Invoiced'), ('RECEIVED', 'Received')], default='NOT_INVOICED', max_length=15)),
                ('expected_invoice_date', models.DateField()),
                ('expected_payment_date', models.DateField()),
                ('actual_invoice_date', models.DateField(blank=True, null=True)),
                ('actual_payment_date', models.DateField(blank=True, null=True)),
                ('business_unit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounting.BusinessUnit')),
                ('contract', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounting.Contract')),
            ],
        ),
        migrations.CreateModel(
            name='MonthlyReconcile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('month', models.SmallIntegerField(choices=[(1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'), (5, 'May'), (6, 'June'), (7, 'July'), (8, 'August'), (9, 'September'), (10, 'October'), (11, 'November'), (12, 'December')], default=1)),
                ('year', models.SmallIntegerField(default=accounting.models.current_year)),
                ('business_unit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounting.BusinessUnit')),
            ],
            options={
                'ordering': ('-year', '-month'),
            },
        ),
        migrations.CreateModel(
            name='PartTimePayroll',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('expected_amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('actual_amount', models.DecimalField(blank=True, decimal_places=2, default=None, max_digits=10, null=True)),
                ('month', models.SmallIntegerField(choices=[(1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'), (5, 'May'), (6, 'June'), (7, 'July'), (8, 'August'), (9, 'September'), (10, 'October'), (11, 'November'), (12, 'December')], default=1)),
                ('year', models.SmallIntegerField(default=accounting.models.current_year)),
                ('business_unit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounting.BusinessUnit')),
            ],
            options={
                'abstract': False,
                'ordering': ('-year', '-month'),
            },
        ),
        migrations.CreateModel(
            name='UserTeamRole',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(choices=[('MANAGER', 'Manager'), ('VIEWER', 'Viewer')], default='VIEWER', max_length=12)),
                ('business_unit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounting.BusinessUnit')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='businessunit',
            name='users',
            field=models.ManyToManyField(related_name='business_units', through='accounting.UserTeamRole', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name='userteamrole',
            unique_together=set([('user', 'business_unit')]),
        ),
        migrations.AlterUniqueTogether(
            name='parttimepayroll',
            unique_together=set([('month', 'year')]),
        ),
        migrations.AlterUniqueTogether(
            name='monthlyreconcile',
            unique_together=set([('month', 'year')]),
        ),
        migrations.AlterUniqueTogether(
            name='invoice',
            unique_together=set([('contract', 'expected_invoice_date')]),
        ),
        migrations.AlterUniqueTogether(
            name='fulltimepayroll',
            unique_together=set([('month', 'year')]),
        ),
        migrations.AlterUniqueTogether(
            name='expenses',
            unique_together=set([('month', 'year')]),
        ),
        migrations.AlterUniqueTogether(
            name='cashbalance',
            unique_together=set([('month', 'year')]),
        ),
    ]