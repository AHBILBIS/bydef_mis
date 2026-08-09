from django.contrib import admin
from .models import PaymentCategory, PaymentSubmission, FinancialLedger

@admin.register(PaymentCategory)
class PaymentCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description')

@admin.register(PaymentSubmission)
class PaymentSubmissionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'category', 'amount', 'transaction_reference', 'status', 'created_at')

@admin.register(FinancialLedger)
class FinancialLedgerAdmin(admin.ModelAdmin):
    list_display = ('id', 'payment', 'amount', 'created_at')
