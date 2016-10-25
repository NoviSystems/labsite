from django.conf.urls import url, include, patterns
from accounting.views import *

urlpatterns = [
    
    # Accounting HomePage
    url(r'^$', HomePageView.as_view(), name='home'),

    # Dashboard Views
    url(r'^(?P<business_unit>\d+)/dashboard/$', DashboardView.as_view(), name='dashboard'),

    # Expense Views
    url(r'^(?P<business_unit>\d+)/expenses/$', ExpensesView.as_view(), name='expenses'),

    # Revenue Views
    url(r'^(?P<business_unit>\d+)/revenue/$', RevenueView.as_view(), name='revenue'),

    # Contracts View
    url(r'^(?P<business_unit>\d+)/contracts/$', ContractsView.as_view(), name='contracts'),

    # Personnel Views
    url(r'^(?P<business_unit>\d+)/personnel/$', PersonnelView.as_view(), name='personnel'),

    # Settings Views
    url(r'^(?P<business_unit>\d+)/settings/business_unit/$', BusinessUnitSettingsPageView.as_view(), name='business_unit_settings'),
    url(r'^(?P<business_unit>\d+)/settings/user_team_roles/$', UserTeamRolesSettingsPageView.as_view(), name='user_team_roles_settings'),

    # Business Unit Forms
    url(r'^create/$', BusinessUnitCreateView.as_view(), name='create_business_unit'),
    url(r'^(?P<business_unit>\d+)/update/$', BusinessUnitUpdateView.as_view(), name='update_business_unit'),
    url(r'^(?P<business_unit>\d+)/delete/$', BusinessUnitDeleteView.as_view(), name='delete_business_unit'),

    # Expense Forms
    url(r'^(?P<business_unit>\d+)/expenses/create/$', ExpenseCreateView.as_view(), name='create_expense'),
    url(r'^(?P<business_unit>\d+)/expenses/(?P<expense>\d+)/update/$', ExpenseUpdateView.as_view(), name='update_expense'),
    url(r'^(?P<business_unit>\d+)/expenses/(?P<expense>\d+)/delete/$', ExpenseDeleteView.as_view(), name='delete_expense'),

    # Income Forms
    url(r'^(?P<business_unit>\d+)/income/create/$', IncomeCreateView.as_view(), name='create_income'),
    url(r'^(?P<business_unit>\d+)/income/(?P<income>\d+)/update/$', IncomeUpdateView.as_view(), name='update_income'),
    url(r'^(?P<business_unit>\d+)/income/(?P<income>\d+)/delete/$', IncomeDeleteView.as_view(), name='delete_income'),

    # Contracts Forms
    url(r'^(?P<business_unit>\d+)/contracts/create/$', ContractCreateView.as_view(), name='create_contract'),
    url(r'^(?P<business_unit>\d+)/contracts/(?P<contract>\d+)/update/$', ContractUpdateView.as_view(), name='update_contract'),
    url(r'^(?P<business_unit>\d+)/contracts/(?P<contract>\d+)/delete/$', ContractDeleteView.as_view(), name='delete_contract'),

    # Invoice Forms
    url(r'^(?P<business_unit>\d+)/contracts/(?P<contract>\d+)/invoice/create/$', InvoiceCreateView.as_view(), name='create_invoice'),
    url(r'^(?P<business_unit>\d+)/contracts/(?P<contract>\d+)/invoice/(?P<invoice>\d+)/update/$', InvoiceUpdateView.as_view(), name='update_invoice'),
    url(r'^(?P<business_unit>\d+)/contracts/(?P<contract>\d+)/invoice/(?P<invoice>\d+)/delete/$', InvoiceDeleteView.as_view(), name='delete_invoice'),

    # Full Time Forms
    url(r'^(?P<business_unit>\d+)/full_time/create/$', FullTimeCreateView.as_view(), name='create_full_time'),
    url(r'^(?P<business_unit>\d+)/full_time/(?P<full_time>\d+)/update/$', FullTimeUpdateView.as_view(), name='update_full_time'),
    url(r'^(?P<business_unit>\d+)/full_time/(?P<full_time>\d+)/delete/$', FullTimeDeleteView.as_view(), name='delete_full_time'),

    # Part Time Forms
    url(r'^(?P<business_unit>\d+)/part_time/create/$', PartTimeCreateView.as_view(), name='create_part_time'),
    url(r'^(?P<business_unit>\d+)/part_time/(?P<part_time>\d+)/update/$', PartTimeUpdateView.as_view(), name='update_part_time'),
    url(r'^(?P<business_unit>\d+)/part_time/(?P<part_time>\d+)/delete/$', PartTimeDeleteView.as_view(), name='delete_part_time'),

    # User Team Role Forms
    url(r'^(?P<business_unit>\d+)/user_team_role/create/$', UserTeamRoleCreateView.as_view(), name='create_user_team_role'),
    url(r'^(?P<business_unit>\d+)/user_team_role/(?P<user_team_role>\d+)/update/$', UserTeamRoleUpdateView.as_view(), name='update_user_team_role'),
    url(r'^(?P<business_unit>\d+)/user_team_role/(?P<user_team_role>\d+)/delete/$', UserTeamRoleDeleteView.as_view(), name='delete_user_team_role'),
]
