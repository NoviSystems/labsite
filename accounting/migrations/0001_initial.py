# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2016-11-02 18:19
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


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
                ('name', models.CharField(max_length=64, verbose_name=b'Name')),
                ('account_number', models.CharField(max_length=12, verbose_name=b'Account Number')),
            ],
        ),
        migrations.CreateModel(
            name='Cash',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('predicted_amount', models.DecimalField(decimal_places=2, default=0.0, max_digits=8, verbose_name=b'Predicted Amount')),
                ('actual_amount', models.DecimalField(decimal_places=2, default=0.0, max_digits=8, verbose_name=b'Actual Amount')),
                ('reconciled', models.BooleanField(default=False, verbose_name=b'Reconciled')),
                ('name', models.CharField(max_length=50, verbose_name=b'Name')),
                ('date_associated', models.DateField(verbose_name=b'Date Associated')),
                ('business_unit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounting.BusinessUnit', verbose_name=b'Business Unit')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Contract',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('department', models.CharField(default=b'CSC', max_length=4, verbose_name=b'Department')),
                ('contract_number', models.IntegerField(verbose_name=b'Contract Number')),
                ('organization_name', models.CharField(max_length=255, verbose_name=b'Contract Name')),
                ('start_date', models.DateField(verbose_name=b'Start Date')),
                ('amount', models.DecimalField(decimal_places=2, default=0.0, max_digits=8, verbose_name=b'Amount')),
                ('contract_state', models.CharField(choices=[(b'ACTIVE', b'Active'), (b'COMPLETE', b'Complete')], max_length=8, verbose_name=b'Contract State')),
                ('contract_type', models.CharField(choices=[(b'HOURLY', b'Hourly'), (b'FIXED', b'Fixed')], max_length=8, verbose_name=b'Contract Type')),
                ('business_unit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounting.BusinessUnit', verbose_name=b'Business Unit')),
            ],
        ),
        migrations.CreateModel(
            name='Expense',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('predicted_amount', models.DecimalField(decimal_places=2, default=0.0, max_digits=8, verbose_name=b'Predicted Amount')),
                ('actual_amount', models.DecimalField(decimal_places=2, default=0.0, max_digits=8, verbose_name=b'Actual Amount')),
                ('reconciled', models.BooleanField(default=False, verbose_name=b'Reconciled')),
                ('expense_type', models.CharField(choices=[(b'PAYROLL', b'Payroll'), (b'GENERAL', b'General')], max_length=7, verbose_name=b'Expense Type')),
                ('name', models.CharField(max_length=50, verbose_name=b'Name')),
                ('date_payable', models.DateField(verbose_name=b'Date Payable')),
                ('date_paid', models.DateField(blank=True, default=None, null=True, verbose_name=b'Date Paid')),
                ('business_unit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounting.BusinessUnit', verbose_name=b'Business Unit')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='FullTime',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=50, verbose_name=b'First Name')),
                ('last_name', models.CharField(max_length=50, verbose_name=b'Last Name')),
                ('employee_id', models.IntegerField(verbose_name=b'Employee ID')),
                ('position', models.CharField(max_length=50, verbose_name=b'Position')),
                ('salary_type', models.CharField(choices=[(b'SPA', b'SPA'), (b'EPA', b'EPA')], max_length=3, verbose_name=b'Salary Type')),
                ('salary_amount', models.DecimalField(decimal_places=2, default=0.0, max_digits=8, verbose_name=b'Salary')),
                ('social_security_amount', models.DecimalField(decimal_places=2, default=0.0, max_digits=8, verbose_name=b'Social Security Amount')),
                ('fed_health_insurance_amount', models.DecimalField(decimal_places=2, default=0.0, max_digits=8, verbose_name=b'Federal Health Insurance Amount')),
                ('retirement_amount', models.DecimalField(decimal_places=2, default=0.0, max_digits=8, verbose_name=b'Retirement Amount')),
                ('medical_insurance_amount', models.DecimalField(decimal_places=2, default=0.0, max_digits=8, verbose_name=b'Medical Insurance Amount')),
                ('staff_benefits_amount', models.DecimalField(decimal_places=2, default=0.0, max_digits=8, verbose_name=b'Staff Benefits Amount')),
                ('fringe_amount', models.DecimalField(decimal_places=2, default=0.0, max_digits=8, verbose_name=b'Fringe Amount')),
                ('business_unit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounting.BusinessUnit', verbose_name=b'Business Unit')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Income',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('predicted_amount', models.DecimalField(decimal_places=2, default=0.0, max_digits=8, verbose_name=b'Predicted Amount')),
                ('actual_amount', models.DecimalField(decimal_places=2, default=0.0, max_digits=8, verbose_name=b'Actual Amount')),
                ('reconciled', models.BooleanField(default=False, verbose_name=b'Reconciled')),
                ('name', models.CharField(max_length=50, verbose_name=b'Name')),
                ('date_payable', models.DateField(verbose_name=b'Date Payable')),
                ('date_paid', models.DateField(blank=True, default=None, null=True, verbose_name=b'Date Paid')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PartTime',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=50, verbose_name=b'First Name')),
                ('last_name', models.CharField(max_length=50, verbose_name=b'Last Name')),
                ('employee_id', models.IntegerField(verbose_name=b'Employee ID')),
                ('position', models.CharField(max_length=50, verbose_name=b'Position')),
                ('hourly_type', models.CharField(choices=[(b'NON_STUDENT', b'Non-Student'), (b'STUDENT', b'Student')], max_length=12, verbose_name=b'Hourly Type')),
                ('hourly_amount', models.DecimalField(decimal_places=2, default=0.0, max_digits=8, verbose_name=b'Hourly Amount')),
                ('hours_work', models.IntegerField(verbose_name=b'Hours Worked')),
                ('business_unit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounting.BusinessUnit', verbose_name=b'Business Unit')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='UserTeamRole',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(choices=[(b'VIEWER', b'Viewer'), (b'MANAGER', b'Manager')], max_length=12, verbose_name=b'Role')),
                ('business_unit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounting.BusinessUnit', verbose_name=b'Business Unit')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name=b'User')),
            ],
        ),
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('income_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='accounting.Income')),
                ('number', models.IntegerField(verbose_name=b'Number')),
                ('transition_state', models.CharField(choices=[(b'NOT_INVOICED', b'Not Invoiced'), (b'RECEIVED', b'Received'), (b'INVOICED', b'Invoiced')], max_length=15, verbose_name=b'Transition State')),
                ('contract', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounting.Contract', verbose_name=b'Contract')),
            ],
            options={
                'abstract': False,
            },
            bases=('accounting.income',),
        ),
        migrations.AddField(
            model_name='income',
            name='business_unit',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounting.BusinessUnit', verbose_name=b'Business Unit'),
        ),
        migrations.AlterUniqueTogether(
            name='userteamrole',
            unique_together=set([('user', 'business_unit')]),
        ),
    ]
