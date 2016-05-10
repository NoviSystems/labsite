from django.contrib import admin
from accounting import models

# Register your models here.
admin.site.register(models.BusinessUnit)
admin.site.register(models.FiscalYear)
admin.site.register(models.Month)
admin.site.register(models.LineItem)
admin.site.register(models.Contract)
admin.site.register(models.Invoice)
admin.site.register(models.Personnel)
admin.site.register(models.Salary)
admin.site.register(models.PartTime)
admin.site.register(models.Expense)
admin.site.register(models.Income)
admin.site.register(models.Payroll)
admin.site.register(models.Cash)
admin.site.register(models.AccountingUser)
