from django.conf.urls import url
from accounting import views


app_name = 'accounting'

urlpatterns = [

    # Accounting HomePage
    url(r'^$', views.HomePageView.as_view(), name='home'),

    # Dashboard Views
    url(r'^(?P<business_unit>\d+)/dashboard/$', views.DashboardView.as_view(), name='dashboard'),
    url(r'^(?P<business_unit>\d+)/dashboard/fy-(?P<fiscal_year>\d+)/$', views.DashboardView.as_view(), name='dashboard'),

    # Expense Views
    url(r'^(?P<business_unit>\d+)/reconcile/$', views.MonthlyReconcileView.as_view(), name='reconcile'),
    url(r'^(?P<business_unit>\d+)/reconcile/fy-(?P<fiscal_year>\d+)/$', views.MonthlyReconcileView.as_view(), name='reconcile'),

    # Revenue Views
    url(r'^(?P<business_unit>\d+)/revenue/$', views.RevenueView.as_view(), name='revenue'),

    # Contracts View
    url(r'^(?P<business_unit>\d+)/contracts/$', views.ContractsView.as_view(), name='contracts'),

    # Settings Views
    url(r'^(?P<business_unit>\d+)/settings/business_unit/$', views.BusinessUnitSettingsPageView.as_view(), name='business_unit_settings'),
    url(r'^(?P<business_unit>\d+)/settings/user_team_roles/$', views.UserTeamRolesSettingsPageView.as_view(), name='user_team_roles_settings'),

    # Business Unit Forms
    url(r'^create/$', views.BusinessUnitCreateView.as_view(), name='create_business_unit'),
    url(r'^(?P<business_unit>\d+)/update/$', views.BusinessUnitUpdateView.as_view(), name='update_business_unit'),
    url(r'^(?P<business_unit>\d+)/delete/$', views.BusinessUnitDeleteView.as_view(), name='delete_business_unit'),

    # Contracts Forms
    url(r'^(?P<business_unit>\d+)/contracts/create/$', views.ContractCreateView.as_view(), name='create_contract'),
    url(r'^(?P<business_unit>\d+)/contracts/(?P<contract>\d+)/update/$', views.ContractUpdateView.as_view(), name='update_contract'),
    url(r'^(?P<business_unit>\d+)/contracts/(?P<contract>\d+)/delete/$', views.ContractDeleteView.as_view(), name='delete_contract'),

    # Invoice Forms
    url(r'^(?P<business_unit>\d+)/contracts/(?P<contract>\d+)/invoice/create/$', views.InvoiceCreateView.as_view(), name='create_invoice'),
    url(r'^(?P<business_unit>\d+)/contracts/(?P<contract>\d+)/invoice/(?P<invoice>\d+)/update/$', views.InvoiceUpdateView.as_view(), name='update_invoice'),
    url(r'^(?P<business_unit>\d+)/contracts/(?P<contract>\d+)/invoice/(?P<invoice>\d+)/delete/$', views.InvoiceDeleteView.as_view(), name='delete_invoice'),

    # User Team Role Forms
    url(r'^(?P<business_unit>\d+)/user_team_role/create/$', views.UserTeamRoleCreateView.as_view(), name='create_user_team_role'),
    url(r'^(?P<business_unit>\d+)/user_team_role/(?P<user_team_role>\d+)/update/$', views.UserTeamRoleUpdateView.as_view(), name='update_user_team_role'),
    url(r'^(?P<business_unit>\d+)/user_team_role/(?P<user_team_role>\d+)/delete/$', views.UserTeamRoleDeleteView.as_view(), name='delete_user_team_role'),
]
