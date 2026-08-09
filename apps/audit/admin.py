from django.contrib import admin
from .models import AuditLog

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'user', 'action', 'ip_address')
    list_filter = ('timestamp',)
    search_fields = ('action', 'user__email', 'ip_address')
    readonly_fields = ('id', 'timestamp', 'user', 'action', 'ip_address')
