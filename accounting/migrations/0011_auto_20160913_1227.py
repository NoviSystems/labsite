# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2016-09-13 16:27
from __future__ import unicode_literals

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0010_auto_20160912_1516'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='expense',
            name='date_payed',
        ),
        migrations.AddField(
            model_name='expense',
            name='date_paid',
            field=models.DateField(default=None, null=True, verbose_name=b'Date Paid'),
        ),
        migrations.AlterField(
            model_name='businessunit',
            name='account_number',
            field=models.CharField(max_length=12, verbose_name=b'Account Number'),
        ),
        migrations.AlterField(
            model_name='businessunit',
            name='name',
            field=models.CharField(max_length=64, verbose_name=b'Name'),
        ),
        migrations.AlterField(
            model_name='cash',
            name='name',
            field=models.CharField(max_length=50, verbose_name=b'Name'),
        ),
        migrations.AlterField(
            model_name='contract',
            name='amount',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=8, verbose_name=b'Amount'),
        ),
        migrations.AlterField(
            model_name='contract',
            name='business_unit',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounting.BusinessUnit', verbose_name=b'Business Unit'),
        ),
        migrations.AlterField(
            model_name='contract',
            name='contract_number',
            field=models.IntegerField(verbose_name=b'Contract Number'),
        ),
        migrations.AlterField(
            model_name='contract',
            name='contract_state',
            field=models.CharField(choices=[(b'ACTIVE', b'active'), (b'COMPLETE', b'complete')], max_length=8, verbose_name=b'Contract State'),
        ),
        migrations.AlterField(
            model_name='contract',
            name='contract_type',
            field=models.CharField(choices=[(b'HOURLY', b'hourly'), (b'FIXED', b'fixed')], max_length=8, verbose_name=b'Contract Type'),
        ),
        migrations.AlterField(
            model_name='contract',
            name='department',
            field=models.CharField(default=b'CSC', max_length=4, verbose_name=b'Department'),
        ),
        migrations.AlterField(
            model_name='contract',
            name='organization_name',
            field=models.CharField(max_length=255, verbose_name=b'Organization Name'),
        ),
        migrations.AlterField(
            model_name='contract',
            name='start_date',
            field=models.DateField(verbose_name=b'Start Date'),
        ),
        migrations.AlterField(
            model_name='expense',
            name='date_payable',
            field=models.DateField(verbose_name=b'Date Payable'),
        ),
        migrations.AlterField(
            model_name='expense',
            name='name',
            field=models.CharField(max_length=50, verbose_name=b'Name'),
        ),
        migrations.AlterField(
            model_name='fiscalyear',
            name='business_unit',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounting.BusinessUnit', verbose_name=b'Business Unit'),
        ),
        migrations.AlterField(
            model_name='fiscalyear',
            name='cash_amount',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=8, verbose_name=b'Cash Amount'),
        ),
        migrations.AlterField(
            model_name='fiscalyear',
            name='end_date',
            field=models.DateField(blank=True, default=datetime.datetime.now, verbose_name=b'End Date'),
        ),
        migrations.AlterField(
            model_name='fiscalyear',
            name='start_date',
            field=models.DateField(verbose_name=b'Start Date'),
        ),
        migrations.AlterField(
            model_name='income',
            name='date_payable',
            field=models.DateField(verbose_name=b'Date Payable'),
        ),
        migrations.AlterField(
            model_name='income',
            name='date_payed',
            field=models.DateField(default=None, null=True, verbose_name=b'Date Payed'),
        ),
        migrations.AlterField(
            model_name='income',
            name='name',
            field=models.CharField(max_length=50, verbose_name=b'Name'),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='contract',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounting.Contract', verbose_name=b'Contract'),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='number',
            field=models.IntegerField(verbose_name=b'Number'),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='transition_state',
            field=models.CharField(choices=[(b'NOT_INVOICED', b'not invoiced'), (b'RECIEVED', b'recieved'), (b'INVOICED', b'invoiced')], max_length=15, verbose_name=b'Transition State'),
        ),
        migrations.AlterField(
            model_name='lineitem',
            name='actual_amount',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=8, verbose_name=b'Actual Amount'),
        ),
        migrations.AlterField(
            model_name='lineitem',
            name='business_unit',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounting.BusinessUnit', verbose_name=b'Business Unit'),
        ),
        migrations.AlterField(
            model_name='lineitem',
            name='month',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounting.Month', verbose_name=b'Month'),
        ),
        migrations.AlterField(
            model_name='lineitem',
            name='predicted_amount',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=8, verbose_name=b'Predicted Amount'),
        ),
        migrations.AlterField(
            model_name='lineitem',
            name='reconciled',
            field=models.BooleanField(default=False, verbose_name=b'Reconciled'),
        ),
        migrations.AlterField(
            model_name='month',
            name='actual_values',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=8, verbose_name=b'Actual Values'),
        ),
        migrations.AlterField(
            model_name='month',
            name='fiscal_year',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='accounting.FiscalYear', verbose_name=b'Fiscal Year'),
        ),
        migrations.AlterField(
            model_name='month',
            name='month',
            field=models.DateField(verbose_name=b'Month'),
        ),
        migrations.AlterField(
            model_name='month',
            name='projected_values',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=8, verbose_name=b'Projected Values'),
        ),
        migrations.AlterField(
            model_name='parttime',
            name='hourly_amount',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=8, verbose_name=b'Hourly Amount'),
        ),
        migrations.AlterField(
            model_name='parttime',
            name='hourly_type',
            field=models.CharField(choices=[(b'NON_STUDENT', b'non student'), (b'STUDENT', b'student')], max_length=12, verbose_name=b'Hourly Type'),
        ),
        migrations.AlterField(
            model_name='parttime',
            name='hours_work',
            field=models.IntegerField(verbose_name=b'Hours Worked'),
        ),
        migrations.AlterField(
            model_name='payroll',
            name='expense',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='accounting.Expense', verbose_name=b'Expense'),
        ),
        migrations.AlterField(
            model_name='payroll',
            name='month',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='accounting.Month', verbose_name=b'Payroll'),
        ),
        migrations.AlterField(
            model_name='personnel',
            name='business_unit',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounting.BusinessUnit', verbose_name=b'Business Unit'),
        ),
        migrations.AlterField(
            model_name='personnel',
            name='employee_id',
            field=models.IntegerField(verbose_name=b'Employee ID'),
        ),
        migrations.AlterField(
            model_name='personnel',
            name='first_name',
            field=models.CharField(max_length=50, verbose_name=b'First Name'),
        ),
        migrations.AlterField(
            model_name='personnel',
            name='last_name',
            field=models.CharField(max_length=50, verbose_name=b'Last Name'),
        ),
        migrations.AlterField(
            model_name='personnel',
            name='position',
            field=models.CharField(max_length=50, verbose_name=b'Position'),
        ),
        migrations.AlterField(
            model_name='salary',
            name='fed_health_insurance_amount',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=8, verbose_name=b'Federal health Insurance Amount'),
        ),
        migrations.AlterField(
            model_name='salary',
            name='fringe_amount',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=8, verbose_name=b'Fringe Amount'),
        ),
        migrations.AlterField(
            model_name='salary',
            name='medical_insurance_amount',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=8, verbose_name=b'Medical Insurance Amount'),
        ),
        migrations.AlterField(
            model_name='salary',
            name='retirement_amount',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=8, verbose_name=b'retirement_amount'),
        ),
        migrations.AlterField(
            model_name='salary',
            name='salary_amount',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=8, verbose_name=b'Salary'),
        ),
        migrations.AlterField(
            model_name='salary',
            name='salary_type',
            field=models.CharField(choices=[(b'SPA', b'SPA'), (b'EPA', b'EPA')], max_length=3, verbose_name=b'Salary Type'),
        ),
        migrations.AlterField(
            model_name='salary',
            name='social_security_amount',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=8, verbose_name=b'Social Security Amount'),
        ),
        migrations.AlterField(
            model_name='salary',
            name='staff_benefits_amount',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=8, verbose_name=b'Staff Benefits Amount'),
        ),
        migrations.AlterField(
            model_name='userteamrole',
            name='business_unit',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounting.BusinessUnit', verbose_name=b'Business Unit'),
        ),
        migrations.AlterField(
            model_name='userteamrole',
            name='role',
            field=models.CharField(choices=[(b'VIEWER', b'viewer'), (b'MANAGER', b'manager')], max_length=12, verbose_name=b'Role'),
        ),
        migrations.AlterField(
            model_name='userteamrole',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name=b'User'),
        ),
    ]
