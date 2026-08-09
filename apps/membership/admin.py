from django.contrib import admin
from .models import MemberProfile

@admin.register(MemberProfile)
class MemberProfileAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'member_number', 'status', 'approved_at')
    list_filter = ('status',)
    search_fields = ('first_name', 'last_name', 'member_number', 'phone_number')
