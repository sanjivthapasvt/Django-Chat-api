from rest_framework import serializers
from typing import List, Dict, Any, Optional
from drf_spectacular.utils import extend_schema_field
from .user_serializers import BasicUserSerializer
from ..models import ChatRoom
from .message_serializers import BasicMessageSerializer
from .typing_serializers import TypingStatusSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

class ChatRoomSerializer(serializers.ModelSerializer):
    participants = BasicUserSerializer(many=True, read_only=True)
    admins = BasicUserSerializer(many=True, read_only=True)
    creator = BasicUserSerializer(read_only=True)
    last_message = BasicMessageSerializer(read_only=True)
    participants_count = serializers.SerializerMethodField()
    typing_users = serializers.SerializerMethodField()
    is_admin = serializers.SerializerMethodField()
    group_image_url = serializers.SerializerMethodField()
    room_type = serializers.SerializerMethodField()

    class Meta:
        model = ChatRoom
        fields = [
            'id', 'room_name', 'is_group', 'created_at', 'creator',
            'participants', 'admins', 'participants_count',
            'sharable_room_id', 'last_message', 'group_image',
            'typing_users', 'is_admin', 'room_type', 'group_image_url'
        ]
        read_only_fields = ['creator', 'sharable_room_id', 'created_at']

    @extend_schema_field(int)
    def get_participants_count(self, obj) -> int:
        return obj.participants.count()

    @extend_schema_field(bool)
    def get_is_admin(self, obj) -> bool:
        request = self.context.get('request')
        return request and request.user in obj.admins.all()

    @extend_schema_field(str)
    def get_room_type(self, obj) -> str:
        return "group" if obj.is_group else "private"

    @extend_schema_field(Optional[str])
    def get_group_image_url(self, obj) -> Optional[str]:
        request = self.context.get('request')
        if obj.group_image:
            return request.build_absolute_uri(obj.group_image.url)
        return None

    @extend_schema_field(List[Dict[str, Any]])
    def get_typing_users(self, obj) -> List[Dict[str, Any]]:
        typing_statuses = obj.typing_statuses.all()
        return [BasicUserSerializer(status.user).data for status in typing_statuses]


class ChatRoomCreateSerializer(serializers.ModelSerializer):
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
        validated_data.pop('creator', None)
        chat_room = ChatRoom.objects.create(creator=creator, **validated_data)
        chat_room.participants.add(creator)
        if chat_room.is_group:
            chat_room.admins.add(creator)
        for user_id in participant_ids:
            user = User.objects.filter(id=user_id).first()
            if user:
                chat_room.participants.add(user)
        return chat_room