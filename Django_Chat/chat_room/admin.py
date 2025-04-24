# In your app's admin.py file
from django.contrib import admin
from .models import ChatRoom, Message, MessageReadStatus, Notification

@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ('id', 'room_name', 'is_group', 'created_at', 'creator')
    list_filter = ('is_group', 'created_at')
    search_fields = ('room_name',)
    filter_horizontal = ('participants', 'admins')
    readonly_fields = ('sharable_room_id',)

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'room', 'sender', 'content', 'timestamp')
    list_filter = ('timestamp', 'sender')
    search_fields = ('content',)
    date_hierarchy = 'timestamp'


@admin.register(MessageReadStatus)
class MessageReadStatusAdmin(admin.ModelAdmin):
    list_display = ('id', 'message', 'user', 'timestamp')
    list_filter = ('timestamp',)

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'message', 'timestamp', 'is_read')
    list_filter = ('timestamp', 'is_read')