from django.contrib import admin
from .models import PaymentSubmission, FinancialLedger

@admin.register(PaymentSubmission)
class PaymentSubmissionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'amount', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'transaction_reference')

@admin.register(FinancialLedger)
class FinancialLedgerAdmin(admin.ModelAdmin):
    list_display = ('id', 'payment', 'amount', 'transaction_type', 'created_at')
    list_filter = ('transaction_type', 'created_at')
