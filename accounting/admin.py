from django.contrib import admin
from accounting import models

# Register your models here.
admin.site.register(models.BusinessUnit)
admin.site.register(models.Contract)
admin.site.register(models.Invoice)
admin.site.register(models.FullTime)
admin.site.register(models.PartTime)
admin.site.register(models.Expense)
admin.site.register(models.Income)
admin.site.register(models.Payroll)
admin.site.register(models.UserTeamRole)
