from django.urls import re_path
from .consumers import ChatConsumer, NotificationConsumer

# Routes for WebSocket connections
websocket_urlpatterns = [
    # Route for chat connections with room ID parameter
    re_path(r'ws/chat/(?P<chatroom_id>\d+)/$', ChatConsumer.as_asgi()),
    
    # Route for user notifications
    re_path(r'ws/notifications/$', NotificationConsumer.as_asgi()),
]