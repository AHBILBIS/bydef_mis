from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', lambda request: redirect('login'), name='root'),
    path('auth/', include('apps.users.urls')),
    path('membership/', include('apps.membership.urls')),
    path('finance/', include('apps.finance.urls')),
    path('documents/', include('apps.documents.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
