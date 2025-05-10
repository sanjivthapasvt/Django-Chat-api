from rest_framework import serializers
from typing import Optional
from drf_spectacular.utils import extend_schema_field
from ..models import ChatRoom
from .message_serializers import BasicMessageSerializer
from django.contrib.auth import get_user_model
from user_api.serializers import UserSerializer
User = get_user_model()

class ChatRoomSerializer(serializers.ModelSerializer):
    participants = UserSerializer(many=True, read_only=True)
    admins = UserSerializer(many=True, read_only=True)
    creator = UserSerializer(read_only=True)
    last_message = BasicMessageSerializer(read_only=True)
    participants_count = serializers.SerializerMethodField()
    is_admin = serializers.SerializerMethodField()
    group_image_url = serializers.SerializerMethodField()
    room_type = serializers.SerializerMethodField()
    chat_name = serializers.SerializerMethodField()

    class Meta:
        model = ChatRoom
        fields = [
            'id', 'room_name', 'is_group', 'created_at', 'creator',
            'participants', 'admins', 'participants_count',
            'sharable_room_id', 'last_message', 'group_image',
            'is_admin', 'room_type', 'group_image_url', 'chat_name'
        ]
        read_only_fields = ['creator', 'sharable_room_id', 'created_at']

    @extend_schema_field(int)
    def get_participants_count(self, obj) -> int:
        # Return total number of participants
        return obj.participants.count()

    @extend_schema_field(bool)
    def get_is_admin(self, obj) -> bool:
        # Check if current user is an admin in the room
        request = self.context.get('request')
        return request and request.user in obj.admins.all()

    @extend_schema_field(str)
    def get_room_type(self, obj) -> str:
        # Return 'group' or 'private' based on room type
        return "group" if obj.is_group else "private"

    @extend_schema_field(Optional[str])
    def get_group_image_url(self, obj) -> Optional[str]:
        # Return full URL for group image if it exists
        request = self.context.get('request')
        if obj.group_image:
            return request.build_absolute_uri(obj.group_image.url)
        return None
    
    def get_chat_name(self, obj):
        user = self.context['request'].user
        if obj.is_group or obj.room_name:
            return obj.room_name or 'Nameless Group'
        
        other_participant = obj.participants.exclude(id=user.id).first()
        return other_participant.username if other_participant else "Anoynomos"


class ChatRoomCreateSerializer(serializers.ModelSerializer):
    participant_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=True,
        help_text="List of user IDs to add as participants (excluding the creator)"
    )

    class Meta:
        model = ChatRoom
        fields = ['room_name', 'group_image', 'participant_ids']

    def validate(self, data):
        if len(data['participant_ids']) + 1 > 50:
            raise serializers.ValidationError("A group cannot have more than 50 members.")
        return data

    def create(self, validated_data):
        participant_ids = validated_data.pop('participant_ids', [])
        creator = self.context['request'].user
        total_participants = len(participant_ids) + 1

        validated_data['creator'] = creator
        validated_data['is_group'] = total_participants > 2

        if validated_data['is_group'] and not validated_data.get('room_name'):
            raise serializers.ValidationError({"room_name": "Group chats must have a name."})

        chat_room = ChatRoom.objects.create(**validated_data)

        users = [creator] + list(User.objects.filter(id__in=participant_ids))
        chat_room.participants.set(users)

        if chat_room.is_group:
            chat_room.admins.add(creator)

        return chat_room



class AddMemberSerializer(serializers.Serializer):
    # List of user IDs to add to a group chat
    users = serializers.ListField(child=serializers.IntegerField(), help_text="Id of users to add to gc")


class RemoveMemberSerializer(serializers.Serializer):
    # ID of the user to remove from the group
    user_id = serializers.IntegerField(help_text="ID of the user to remove")
