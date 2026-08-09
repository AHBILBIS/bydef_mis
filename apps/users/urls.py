from django.urls import path
from django.views.generic import TemplateView
from . import views
from apps.membership import views as membership_views
from apps.finance import views as finance_views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_redirect_view, name='dashboard_redirect'),
    
    path('dashboard/chairman/', membership_views.chairman_dashboard_view, name='chairman_dashboard'),
    path('dashboard/financial/', finance_views.financial_dashboard_view, name='financial_dashboard'),
    path('dashboard/exco/', TemplateView.as_view(template_name='dashboards/exco.html'), name='exco_dashboard'),
    path('dashboard/member/', TemplateView.as_view(template_name='dashboards/member.html'), name='member_dashboard'),
]
