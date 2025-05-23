from rest_framework import serializers
from ..models import Notification

# Serializer for Notification model with additional derived fields
class NotificationSerializer(serializers.ModelSerializer):
    sender = serializers.SerializerMethodField()
    message = serializers.SerializerMethodField()
    chat_name = serializers.SerializerMethodField()
    class Meta:
        model = Notification
        fields = ['id', 'sender', 'message', 'chat_name', 'timestamp', 'is_read']

    def get_sender(self, obj) -> str:
        # Return sender's username from the related message
        return obj.message.sender.username

    def get_room_name(self, obj) -> str:
        # Return the chat room name from the related message
        return obj.message.room.room_name

    def get_message(self, obj) -> str:
        # Return message content
        return obj.message.content
    
    def get_chat_name(self, obj):
        if not obj.message or not obj.message.room:
            return None
        
        if obj.message.room.is_group:
            return obj.message.room.room_name
        
        user = self.context.get('request').user
        other_participants = obj.message.room.participants.exclude(id=user.id)
        
        if other_participants.exists():
            participant = other_participants.first()
            return (participant.first_name and participant.last_name and f"{participant.first_name} {participant.last_name}") or participant.username
        
        return None