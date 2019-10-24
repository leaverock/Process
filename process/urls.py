from django.contrib import admin
from django.urls import path
from django.conf.urls import url
from . import views
from django.views.generic import RedirectView
from django.contrib.auth.views import LoginView, LogoutView


urlpatterns = [
    path('', RedirectView.as_view(url='/process/info/', permanent=True)),
    path('getid/<id>/', views.getid, name = "getid"),
    path('info/', views.ProcessView.as_view(), name = "info"),
    path('member/', views.Memberview.as_view(), name = "members"),
    path('specification/', views.SpecificationView.as_view(), name = "specification"),
    path('expence/', views.ExpensesView.as_view(), name = "expenses"),
    path('indicator/', views.IndicatorView.as_view(), name = "indicator"),
    path('risk/', views.RiskView.as_view(), name = "risk"),
    path('allrisk/', views.AllRiskView.as_view(), name = "allrisk"),
    path('event/', views.EventView.as_view(), name = "event"),
    path('graphic/', views.GraphicView.as_view(), name = "graphic"),
    path('risk/scen/<id>/', views.ScenarioView.as_view(), name = "scenar"),
    path('addevent/editscen/<id>/', views.edit_riskevent, name = "edit_riskevent"),
    #path('calculate_preority/', views.calculate_preority, name = "calculate_preority"),
    path('addprocess/', views.add_process, name = 'addprocess'),
    path('addmember/', views.add_memeber, name = 'addmember'),
    path('addexpence/', views.add_expense, name = 'addexpence'),
    path('addindicator/', views.add_indicator, name = 'addindicator'),
    path('addevent/', views.add_event, name = 'addevent'),
    path('coppy/', views.create_coppy, name = 'coppy'),
    path('delete/', views.delete, name = 'delete'),
    path('edit/', views.edit_proces, name = 'edit'),
    path('editexpence/', views.edit_expense, name = 'editexpence'),
    path('editindicator/', views.edit_indicator, name = 'edit_indicator'),
    path('editscen/', views.edit_scen, name = 'edit_scen'),
    path('editscen_event/<id>/', views.edit_scen_event, name = 'edit_scen_event'),
    path('create-risk', views.create_risk, name = "create_risk"),
    path('create-scenario', views.create_scenario, name = "create_scenario"),
    path('calculate', views.calculate, name = "calculate"),
    path('calculateallrisk', views.calculate_all_risk, name = "calculateallrisk"),
    path('accounts/login/',  LoginView.as_view(), name = 'login'),
    path('accounts/logout/',  LogoutView.as_view(), name = 'logout'),
    path('addgroup/',  views.add_group, name = 'addgroup'),
    path('addunit/',  views.add_unit, name = 'addunit'),
    path('addposition/',  views.add_position, name = 'addposition'),
    path('sumallexpense/',views.calculate_all_for_process, name="sum_all_expense"),
    path('choise_process',views.choise_process, name = "choise_process"),
    path('create_coppy',views.coppy_process, name = "create_coppy"),
    path('riskevent/<id>',views.risk_event, name = "risk_event"),
    path('change_expense/<id>',views.change_expense, name = "change_expense"),
    path('export_xls', views.export_xls, name='export_xls'),
]
