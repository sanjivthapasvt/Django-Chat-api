import os
from django.core.asgi import get_asgi_application
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Django_Chat.settings')
django.setup()

from channels.routing import ProtocolTypeRouter, URLRouter
from chat_room import routing

from .middleware import JWTAuthMiddleware

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": JWTAuthMiddleware(
        URLRouter(
            routing.websocket_urlpatterns
        )
    ),
})