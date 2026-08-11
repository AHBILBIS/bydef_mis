from django.urls import path
from .views import (
    submit_payment_view,
    verify_payment_view,
    reject_payment_view,
    export_ledger_csv_view,
    export_payments_csv_view
)

urlpatterns = [
    path('submit/', submit_payment_view, name='submit_payment'),
    path('verify/<uuid:payment_id>/', verify_payment_view, name='verify_payment'),
    path('reject/<uuid:payment_id>/', reject_payment_view, name='reject_payment'),
    path('export/ledger/csv/', export_ledger_csv_view, name='export_ledger_csv'),
    path('export/payments/csv/', export_payments_csv_view, name='export_payments_csv'),
]
