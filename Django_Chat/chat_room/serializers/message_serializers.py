from rest_framework import serializers
from ..models import Message, MessageReadStatus
from .user_serializers import BasicUserSerializer

class MessageReadStatusSerializer(serializers.ModelSerializer):
    user = BasicUserSerializer(read_only=True)
    
    class Meta:
        model = MessageReadStatus
        fields = ['id', 'user', 'timestamp']

class BasicMessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Message
        fields = ['id', 'sender_name', 'content', 'timestamp', 'image']
    
    def get_sender_name(self, obj) -> str:
        return obj.sender.username if obj.sender else None

class MessageSerializer(serializers.ModelSerializer):
    sender = BasicUserSerializer(read_only=True)
    read_statuses = MessageReadStatusSerializer(many=True, read_only=True)
    
    class Meta:
        model = Message
        fields = ['id', 'room', 'sender', 'content', 'timestamp', 'image', 'read_statuses']
        read_only_fields = ['sender']

class MessageCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['room', 'content', 'image']
    
    def create(self, validated_data) -> Message:
        sender = self.context['request'].user
        return Message.objects.create(sender=sender, **validated_data)
