from django.contrib import admin
from .models import PaymentCategory, PaymentSubmission, FinancialLedger

@admin.register(PaymentCategory)
class PaymentCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'default_amount', 'is_mandatory')

@admin.register(PaymentSubmission)
class PaymentSubmissionAdmin(admin.ModelAdmin):
    list_display = ('payment_reference', 'member', 'category', 'amount', 'status', 'submitted_at')
    list_filter = ('status', 'category')
    search_fields = ('payment_reference', 'member__first_name', 'member__last_name')

@admin.register(FinancialLedger)
class FinancialLedgerAdmin(admin.ModelAdmin):
    list_display = ('transaction_type', 'amount', 'description', 'posted_by', 'created_at')
    list_filter = ('transaction_type',)
    readonly_fields = ('id', 'created_at')
