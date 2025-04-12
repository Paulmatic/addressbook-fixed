from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Optionally include DRF's built-in docs if in DEBUG mode
urlpatterns = [
    path('admin/', admin.site.urls),

    # App-specific URLs
    path('', include('contacts.urls')),
    path('api/', include('api.urls')),
]

# Serve media files during development
if settings.DEBUG:
    from rest_framework.documentation import include_docs_urls
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += [
        path('docs/', include_docs_urls(title='Address Book API Documentation')),
    ]
