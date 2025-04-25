from rest_framework import serializers
from ..models import Notification

class NotificationSerializer(serializers.ModelSerializer):
    sender = serializers.SerializerMethodField()
    room_name = serializers.SerializerMethodField()
    message = serializers.SerializerMethodField()
    class Meta:
        model = Notification
        fields = ['id', 'sender', 'message','room_name', 'timestamp', 'is_read', 'timestamp']
        
    def get_sender(self, obj) -> str:
        return obj.message.sender.username
    
    def get_room_name(self, obj) -> str:
        return obj.message.room.room_name
    
    def get_message(self, obj) -> str:
        return obj.message.content