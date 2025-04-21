from django.apps import AppConfig


class ChatRoomConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'chat_room'
    verbose_name = "ChatRoom and Messages"
    

    def ready(self):
        from . import signals