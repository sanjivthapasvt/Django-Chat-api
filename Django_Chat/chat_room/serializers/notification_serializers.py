from rest_framework import serializers
from ..models import Notification

# Serializer for Notification model with additional derived fields
class NotificationSerializer(serializers.ModelSerializer):
    sender = serializers.SerializerMethodField()
    room_name = serializers.SerializerMethodField()
    message = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = ['id', 'sender', 'message', 'room_name', 'timestamp', 'is_read']

    def get_sender(self, obj) -> str:
        # Return sender's username from the related message
        return obj.message.sender.username

    def get_room_name(self, obj) -> str:
        # Return the chat room name from the related message
        return obj.message.room.room_name

    def get_message(self, obj) -> str:
        # Return message content
        return obj.message.content
