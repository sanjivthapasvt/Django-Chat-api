import os
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
import chat_room.routing

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Django_chat.settings")

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            chat_room.websocket_urlpatterns
        )
    ),
})
