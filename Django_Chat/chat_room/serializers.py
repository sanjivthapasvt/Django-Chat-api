from rest_framework import serializers
from .models import ChatRoom, Message, TypingStatus, MessageReadStatus, Notification
from django.contrib.auth import get_user_model

User = get_user_model()

class BasicUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'profile_pic']
        read_only_fields = ['id', 'username', 'email']


class MessageReadStatusSerializer(serializers.ModelSerializer):
    user = BasicUserSerializer(read_only=True)
    
    class Meta:
        model = MessageReadStatus
        fields = ['id', 'user', 'timestamp']


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'user', 'message', 'timestamp', 'is_read']


class MessageSerializer(serializers.ModelSerializer):
    sender = BasicUserSerializer(read_only=True)
    read_statuses = MessageReadStatusSerializer(many=True, read_only=True)
    
    class Meta:
        model = Message
        fields = ['id', 'room', 'sender', 'content', 'timestamp', 'image', 'read_statuses']
        read_only_fields = ['sender']


class BasicMessageSerializer(serializers.ModelSerializer):
    """message serializer for displaying last message in chat rooms"""
    sender_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Message
        fields = ['id', 'sender_name', 'content', 'timestamp', 'image']
    
    def get_sender_name(self, obj):
        return obj.sender.username if obj.sender else None


class TypingStatusSerializer(serializers.ModelSerializer):
    user = BasicUserSerializer(read_only=True)
    
    class Meta:
        model = TypingStatus
        fields = ['id', 'room', 'user', 'timestamp']
        read_only_fields = ['timestamp']


class ChatRoomSerializer(serializers.ModelSerializer):
    participants = BasicUserSerializer(many=True, read_only=True)
    admins = BasicUserSerializer(many=True, read_only=True)
    creator = BasicUserSerializer(read_only=True)
    last_message = BasicMessageSerializer(read_only=True)
    participants_count = serializers.SerializerMethodField()
    typing_users = serializers.SerializerMethodField()
    
    class Meta:
        model = ChatRoom
        fields = [
            'id', 'room_name', 'is_group', 'created_at', 'creator',
            'participants', 'admins', 'participants_count',
            'sharable_room_id', 'last_message', 'group_image',
            'typing_users'
        ]
        read_only_fields = ['creator', 'sharable_room_id', 'created_at']
    
    def get_participants_count(self, obj):
        return obj.participants.count()
    
    def get_typing_users(self, obj):
        # users currently typing in this room
        typing_statuses = obj.typing_statuses.all()
        return [BasicUserSerializer(status.user).data for status in typing_statuses]


class ChatRoomCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating chat rooms"""
    participant_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = ChatRoom
        fields = ['room_name', 'is_group', 'participant_ids', 'group_image']
    
    def create(self, validated_data):
        participant_ids = validated_data.pop('participant_ids', [])
        creator = self.context['request'].user
        
        # Create the chat room
        chat_room = ChatRoom.objects.create(
            creator=creator,
            **validated_data
        )
        
        # Add creator as participant and admin
        chat_room.participants.add(creator)
        
        if chat_room.is_group:
            chat_room.admins.add(creator)
        
        # Add other participants
        for user_id in participant_ids:
            try:
                user = User.objects.get(id=user_id)
                chat_room.participants.add(user)
            except User.DoesNotExist:
                pass
        
        return chat_room


class MessageCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating messages"""
    
    class Meta:
        model = Message
        fields = ['room', 'content', 'image']
    
    def create(self, validated_data):
        sender = self.context['request'].user
        message = Message.objects.create(
            sender=sender,
            **validated_data
        )
        return message