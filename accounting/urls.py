from django.conf.urls import url, include, patterns
from accounting import views

urlpatterns = [

    # Accounting HomePage
    url(r'^$', views.HomePageView.as_view(), name='home'),

    # Dashboard Views
    url(r'^(?P<business_unit>\d+)/dashboard/$', views.DashboardView.as_view(), name='dashboard'),
    url(r'^(?P<business_unit>\d+)/dashboard/(?P<start_year>\d+)-(?P<end_year>\d+)/$', views.DashboardView.as_view(), name='dashboard'),

    # Expense Views
    url(r'^(?P<business_unit>\d+)/expenses/$', views.ExpensesView.as_view(), name='expenses'),
    url(r'^(?P<business_unit>\d+)/expenses/(?P<month>\d+)/$', views.ExpensesView.as_view(), name='expenses'),
    url(r'^(?P<business_unit>\d+)/expenses/(?P<start_year>\d+)-(?P<end_year>\d+)/$', views.ExpensesView.as_view(), name='expenses'),
    url(r'^(?P<business_unit>\d+)/expenses/(?P<start_year>\d+)-(?P<end_year>\d+)/(?P<month>\d+)$', views.ExpensesView.as_view(), name='expenses'),

    # Revenue Views
    url(r'^(?P<business_unit>\d+)/revenue/$', views.RevenueView.as_view(), name='revenue'),

    # Contracts View
    url(r'^(?P<business_unit>\d+)/contracts/$', views.ContractsView.as_view(), name='contracts'),

    # Personnel Views
    url(r'^(?P<business_unit>\d+)/personnel/$', views.PersonnelView.as_view(), name='personnel'),

    # Settings Views
    url(r'^(?P<business_unit>\d+)/settings/business_unit/$', views.BusinessUnitSettingsPageView.as_view(), name='business_unit_settings'),
    url(r'^(?P<business_unit>\d+)/settings/user_team_roles/$', views.UserTeamRolesSettingsPageView.as_view(), name='user_team_roles_settings'),

    # Business Unit Forms
    url(r'^create/$', views.BusinessUnitCreateView.as_view(), name='create_business_unit'),
    url(r'^(?P<business_unit>\d+)/update/$', views.BusinessUnitUpdateView.as_view(), name='update_business_unit'),
    url(r'^(?P<business_unit>\d+)/delete/$', views.BusinessUnitDeleteView.as_view(), name='delete_business_unit'),

    # Expense Forms
    url(r'^(?P<business_unit>\d+)/expenses/create/$', views.ExpenseCreateView.as_view(), name='create_expense'),
    url(r'^(?P<business_unit>\d+)/expenses/(?P<expense>\d+)/update/$', views.ExpenseUpdateView.as_view(), name='update_expense'),
    url(r'^(?P<business_unit>\d+)/expenses/(?P<expense>\d+)/delete/$', views.ExpenseDeleteView.as_view(), name='delete_expense'),

    # Cash Forms
    url(r'^(?P<business_unit>\d+)/cash/(?P<month>\d+)-(?P<year>\d+)/$', views.CashCreateView.as_view(), name='create_cash'),
    url(r'^(?P<business_unit>\d+)/cash/(?P<cash>\d+)/update/$', views.CashUpdateView.as_view(), name='update_cash'),

    # Payroll Forms
    url(r'^(?P<business_unit>\d+)/expense/(?P<month>\d+)-(?P<year>\d+)/create/$', views.PayrollExpenseCreateView.as_view(), name='create_payroll_expense'),

    # Income Forms
    url(r'^(?P<business_unit>\d+)/income/create/$', views.IncomeCreateView.as_view(), name='create_income'),
    url(r'^(?P<business_unit>\d+)/income/(?P<income>\d+)/update/$', views.IncomeUpdateView.as_view(), name='update_income'),
    url(r'^(?P<business_unit>\d+)/income/(?P<income>\d+)/delete/$', views.IncomeDeleteView.as_view(), name='delete_income'),

    # Contracts Forms
    url(r'^(?P<business_unit>\d+)/contracts/create/$', views.ContractCreateView.as_view(), name='create_contract'),
    url(r'^(?P<business_unit>\d+)/contracts/(?P<contract>\d+)/update/$', views.ContractUpdateView.as_view(), name='update_contract'),
    url(r'^(?P<business_unit>\d+)/contracts/(?P<contract>\d+)/delete/$', views.ContractDeleteView.as_view(), name='delete_contract'),

    # Invoice Forms
    url(r'^(?P<business_unit>\d+)/contracts/(?P<contract>\d+)/invoice/create/$', views.InvoiceCreateView.as_view(), name='create_invoice'),
    url(r'^(?P<business_unit>\d+)/contracts/(?P<contract>\d+)/invoice/(?P<invoice>\d+)/update/$', views.InvoiceUpdateView.as_view(), name='update_invoice'),
    url(r'^(?P<business_unit>\d+)/contracts/(?P<contract>\d+)/invoice/(?P<invoice>\d+)/delete/$', views.InvoiceDeleteView.as_view(), name='delete_invoice'),

    # Full Time Forms
    url(r'^(?P<business_unit>\d+)/full_time/create/$', views.FullTimeCreateView.as_view(), name='create_full_time'),
    url(r'^(?P<business_unit>\d+)/full_time/(?P<full_time>\d+)/update/$', views.FullTimeUpdateView.as_view(), name='update_full_time'),
    url(r'^(?P<business_unit>\d+)/full_time/(?P<full_time>\d+)/delete/$', views.FullTimeDeleteView.as_view(), name='delete_full_time'),

    # Part Time Forms
    url(r'^(?P<business_unit>\d+)/part_time/create/$', views.PartTimeCreateView.as_view(), name='create_part_time'),
    url(r'^(?P<business_unit>\d+)/part_time/(?P<part_time>\d+)/update/$', views.PartTimeUpdateView.as_view(), name='update_part_time'),
    url(r'^(?P<business_unit>\d+)/part_time/(?P<part_time>\d+)/delete/$', views.PartTimeDeleteView.as_view(), name='delete_part_time'),

    # User Team Role Forms
    url(r'^(?P<business_unit>\d+)/user_team_role/create/$', views.UserTeamRoleCreateView.as_view(), name='create_user_team_role'),
    url(r'^(?P<business_unit>\d+)/user_team_role/(?P<user_team_role>\d+)/update/$', views.UserTeamRoleUpdateView.as_view(), name='update_user_team_role'),
    url(r'^(?P<business_unit>\d+)/user_team_role/(?P<user_team_role>\d+)/delete/$', views.UserTeamRoleDeleteView.as_view(), name='delete_user_team_role'),
]
