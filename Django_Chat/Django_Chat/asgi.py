import os
from dotenv import load_dotenv

load_dotenv()

# Set the default Django settings module for the 'asgi' command
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Django_Chat.settings')
django.setup()

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from chat_room import routing
from .middleware import JWTAuthMiddleware


#ASGI application with HTTP and WebSocket protocol support
application = ProtocolTypeRouter({
    "http": get_asgi_application(),  # HTTP support
    "websocket": JWTAuthMiddleware(  # WebSocket with custom JWT middleware
        URLRouter(
            routing.websocket_urlpatterns
        )
    ),
})
