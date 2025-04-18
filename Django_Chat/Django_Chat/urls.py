from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from django.conf import settings
from django.conf.urls.static import static
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="API",
        default_version='v1',
        description="Interactive API docs with JWT Auth",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    authentication_classes=[],
)


urlpatterns = [
    # Schema Generation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    # Swagger UI
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    # Redoc
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    #admin urls
    path('admin/', admin.site.urls),
    #for user_api
    path('api/', include('user_api.urls'), name="authentication"),
    #for chat_room
    path('api/',include('chat_room.urls'), name='chat_room')
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)