from django.contrib import admin
from accounting import models


admin.site.register(models.BusinessUnit)
admin.site.register(models.UserTeamRole)
admin.site.register(models.Contract)
admin.site.register(models.Invoice)
admin.site.register(models.CashBalance)
admin.site.register(models.Expenses)
admin.site.register(models.FullTimePayroll)
admin.site.register(models.PartTimePayroll)
