from rest_framework import serializers
from ..models import ChatRoom, Message, MessageReadStatus
from django.contrib.auth import get_user_model

User = get_user_model()

# Basic serializer to return limited user info
class BasicUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id']
        read_only_fields = ['id'] 

# Serializer for individual read status records of a message
class MessageReadStatusSerializer(serializers.ModelSerializer):
    user = BasicUserSerializer(read_only=True)  # Serialize the user who read the message

    class Meta:
        model = MessageReadStatus
        fields = ['id', 'user', 'timestamp']


#serializer for displaying message previews (e.g., last message in a chat)
class BasicMessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = ['id', 'sender_name', 'content', 'timestamp']

    def get_sender_name(self, obj) -> str:
        return obj.sender.username if obj.sender else None


# serializer for retrieving message details including read status
class MessageSerializer(serializers.ModelSerializer):
    sender = BasicUserSerializer()
    read_statuses = MessageReadStatusSerializer(many=True, read_only=True) 
    class Meta:
        model = Message
        fields = ['id', 'room', 'sender', 'content', 'timestamp', 'image', 'read_statuses']

# Serializer for creating new messages
class MessageCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'content', 'image'] 

    def create(self, validated_data) -> Message:
        # Automatically assign sender and room based on context
        validated_data['sender'] = self.context['request'].user
        validated_data['room'] = ChatRoom.objects.get(pk=self.context['view'].kwargs['chatroom_pk'])
        return super().create(validated_data)
