from django.urls import path
from . import views

urlpatterns = [
    path('approve/<uuid:member_id>/', views.approve_member_view, name='approve_member'),
    path('reject/<uuid:member_id>/', views.reject_member_view, name='reject_member'),
]
