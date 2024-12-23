from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from event_ticketing.swagger import schema_view
from debug_toolbar.toolbar import debug_toolbar_urls

urlpatterns = [
    path('api/', include('event.urls')),
    path('api/', include('contact.urls')),
    path('api/auth/', include('authentication.urls')),
    path('admin/', admin.site.urls),
    path('api/swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

urlpatterns += [
    path('api-auth/', include('rest_framework.urls')),
]

if not settings.TESTING:
    urlpatterns = [
        *urlpatterns,
    ] + debug_toolbar_urls()
