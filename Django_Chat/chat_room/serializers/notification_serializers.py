from rest_framework import serializers
from ..models import Notification

class NotificationSerializer(serializers.ModelSerializer):
    sender = serializers.SerializerMethodField()
    room_name = serializers.SerializerMethodField()
    class Meta:
        model = Notification
        fields = ['id', 'sender', 'message','room_name', 'timestamp', 'is_read', 'timestamp']
        
    def get_sender(self, obj):
        return obj.message.sender.username
    
    def get_room_name(self, obj):
        return obj.message.room.name
