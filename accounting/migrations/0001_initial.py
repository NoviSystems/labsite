# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='BusinessUnit',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('business_unit_name', models.CharField(max_length=64)),
            ],
        ),
        migrations.CreateModel(
            name='Contract',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('contract_number', models.IntegerField()),
                ('organization_name', models.CharField(max_length=255)),
                ('start_date', models.DateField()),
                ('contract_state', models.CharField(max_length=8, choices=[(b'ACTIVE', b'active'), (b'COMPLETE', b'complete')])),
                ('contract_amount', models.DecimalField(default=0.0, max_digits=8, decimal_places=2)),
                ('contract_type', models.CharField(max_length=8, choices=[(b'HOURLY', b'hourly'), (b'FIXED', b'fixed')])),
            ],
        ),
        migrations.CreateModel(
            name='Expense',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('Expense_amount', models.DecimalField(default=0.0, max_digits=8, decimal_places=2)),
                ('data_payable', models.DateField()),
                ('date_payed', models.DateField()),
                ('reoccuring', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='FiscalYear',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('start_month', models.DateField()),
                ('number_of_months', models.IntegerField()),
                ('business_unit', models.ForeignKey(to='accounting.BusinessUnit')),
            ],
        ),
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('invoice_number', models.IntegerField()),
                ('invoice_date', models.DateField()),
                ('invoice_amount', models.DecimalField(default=0.0, max_digits=8, decimal_places=2)),
                ('transation_state', models.CharField(max_length=15, choices=[(b'NOT_INVOICED', b'not invoiced'), (b'RECIEVED', b'recieved'), (b'INVOICED', b'invoiced')])),
            ],
        ),
        migrations.CreateModel(
            name='LineItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('object_id', models.PositiveIntegerField()),
                ('predicted_amount', models.DecimalField(default=0.0, max_digits=8, decimal_places=2)),
                ('actual_amount', models.DecimalField(default=0.0, max_digits=8, decimal_places=2)),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
            ],
        ),
        migrations.CreateModel(
            name='Month',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('month', models.DateField()),
                ('projected_values', models.DecimalField(default=0.0, max_digits=8, decimal_places=2)),
                ('actual_values', models.DecimalField(default=0.0, max_digits=8, decimal_places=2)),
            ],
        ),
        migrations.CreateModel(
            name='PartTime',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('hourly_type', models.CharField(max_length=12, choices=[(b'NON_STUDENT', b'non student'), (b'STUDENT', b'student')])),
                ('hourly_amount', models.DecimalField(default=0.0, max_digits=8, decimal_places=2)),
                ('hours_work', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Personnel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('first_name', models.CharField(max_length=50)),
                ('last_name', models.CharField(max_length=50)),
                ('employee_id', models.IntegerField()),
                ('position', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Salary',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('salary_type', models.CharField(max_length=3, choices=[(b'SPA', b'SPA'), (b'EPA', b'EPA')])),
                ('social_security_amount', models.DecimalField(default=0.0, max_digits=8, decimal_places=2)),
                ('fed_health_insurance_amount', models.DecimalField(default=0.0, max_digits=8, decimal_places=2)),
                ('retirement_amount', models.DecimalField(default=0.0, max_digits=8, decimal_places=2)),
                ('medical_insurance_amount', models.DecimalField(default=0.0, max_digits=8, decimal_places=2)),
                ('staff_benefits_amount', models.DecimalField(default=0.0, max_digits=8, decimal_places=2)),
                ('fringe_amount', models.DecimalField(default=0.0, max_digits=8, decimal_places=2)),
            ],
        ),
        migrations.AddField(
            model_name='lineitem',
            name='month',
            field=models.ForeignKey(to='accounting.Month'),
        ),
    ]
