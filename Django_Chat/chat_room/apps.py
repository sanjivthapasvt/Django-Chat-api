from django.apps import AppConfig


class ChatRoomConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'chat_room'
    verbose_name = "ChatRoom and Messages"
    

    def ready(self):
        print("ChatRoomIsReady is ready, importing signals...") # <-- Add print for debugging
        try:
            from . import signals
        except ImportError:
            print("Error importing signals!")