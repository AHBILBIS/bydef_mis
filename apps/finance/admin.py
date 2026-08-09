from django.contrib import admin
from .models import PaymentCategory, PaymentReceipt

@admin.register(PaymentCategory)
class PaymentCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description')

@admin.register(PaymentReceipt)
class PaymentReceiptAdmin(admin.ModelAdmin):
    list_display = ('id', 'category', 'amount', 'transaction_reference', 'created_at')
