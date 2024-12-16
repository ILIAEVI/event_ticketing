from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="Event Ticketing API",
        default_version='v1',
        description="Event Ticketing API",
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)
