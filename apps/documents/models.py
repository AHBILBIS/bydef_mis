import uuid
from django.db import models
from django.conf import settings

class Document(models.Model):
    class AccessLevel(models.TextChoices):
        ALL_MEMBERS = 'ALL_MEMBERS', 'All Approved Members'
        EXCO_ONLY = 'EXCO_ONLY', 'Executive Committee Only'
        CHAIRMAN_ONLY = 'CHAIRMAN_ONLY', 'Chairman & Secretary Only'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to='documents/%Y/%m/')
    access_level = models.CharField(max_length=30, choices=AccessLevel.choices, default=AccessLevel.ALL_MEMBERS)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Document'
        verbose_name_plural = 'Documents'
        ordering = ['-uploaded_at']

    def __str__(self):
        return self.title
