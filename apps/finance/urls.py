from django.urls import path
from . import views

urlpatterns = [
    path('submit/', views.submit_payment_view, name='submit_payment'),
    path('verify/<uuid:payment_id>/', views.verify_payment_view, name='verify_payment'),
    path('reject/<uuid:payment_id>/', views.reject_payment_view, name='reject_payment'),
    path('export/ledger/csv/', export_ledger_csv_view, name='export_ledger_csv'),
    path('export/payments/csv/', export_payments_csv_view, name='export_payments_csv'),
]