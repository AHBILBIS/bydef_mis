from django.contrib import admin
from .models import Document

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'access_level', 'uploaded_by', 'uploaded_at')
    list_filter = ('access_level',)
    search_fields = ('title', 'description')
