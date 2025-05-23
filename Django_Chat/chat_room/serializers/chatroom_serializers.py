from rest_framework import serializers
from typing import Optional
from drf_spectacular.utils import extend_schema_field
from ..models import ChatRoom
from .message_serializers import BasicMessageSerializer, BasicUserSerializer
from django.contrib.auth import get_user_model
from user_api.serializers import UserSerializer
User = get_user_model()
from django_redis import get_redis_connection


class ParticipantUserSerializer(serializers.ModelSerializer):
    is_admin = serializers.SerializerMethodField()
    online_status = serializers.SerializerMethodField()
    last_seen = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ['id', 'username','full_name', 'is_admin' ,'profile_pic','online_status', 'last_seen']
        read_only_fields = ['id', 'username', 'email']
    
    def get_online_status(self, obj) -> bool:
        conn = get_redis_connection("default")
        return conn.get(f"user:{obj.id}:online") == b"1"
    

    def get_last_seen(self, obj) -> str:
        conn = get_redis_connection("default")
        last_seen = conn.get(f"user:{obj.id}:last_seen")
        if last_seen:
            import datetime
            return datetime.datetime.fromisoformat(last_seen.decode())
        return None
    
    def get_is_admin(self, obj) -> bool:
        admin_ids = self.context.get('chatroom_admin_ids', [])
        return obj.id in admin_ids
    
    def get_full_name(self, obj) -> str:
        if obj.first_name or obj.last_name:
            return f"{obj.first_name} {obj.last_name}"
        return None

class ChatRoomListSerializer(serializers.ModelSerializer):
    chat_name = serializers.SerializerMethodField()
    group_image = serializers.SerializerMethodField()
    last_message = BasicMessageSerializer(read_only=True)

    class Meta:
        model = ChatRoom
        fields = ['id','group_image', 'chat_name', 'is_group', 'last_message']

    @extend_schema_field(str)
    def get_chat_name(self, obj):
        if obj.is_group:
            return obj.room_name
        
        user = self.context.get('request').user
        other_participants = obj.participants.exclude(id=user.id)
        
        if other_participants.exists():
            participant = other_participants.first()
            return (participant.first_name and participant.last_name and f"{participant.first_name} {participant.last_name}") or participant.username
        
        return None

    @extend_schema_field(str)
    def get_group_image(self, obj):
        request = self.context.get('request')
        
        def build_absolute_url(relative_url):
            return request.build_absolute_uri(relative_url) if request and relative_url else None

        if obj.is_group:
            return build_absolute_url(obj.group_image.url if obj.group_image else None)

        user = request.user
        other_participants = obj.participants.exclude(id=user.id)
        if other_participants.exists():
            participant = other_participants.first()
            return build_absolute_url(participant.profile_pic.url if participant.profile_pic else None)

        return None

        
class ChatRoomSerializer(serializers.ModelSerializer):
    participants = serializers.SerializerMethodField()
    admins = BasicUserSerializer(many=True, read_only=True)
    chat_name = serializers.SerializerMethodField()
    group_image = serializers.SerializerMethodField()
    class Meta:
        model = ChatRoom
        fields = [
            'id', 'is_group', 'participants',
            'admins', 'group_image','chat_name'
        ]

    @extend_schema_field(int)
    def get_participants_count(self, obj) -> int:
        # Return total number of participants
        return obj.participants.count()


    @extend_schema_field(str)
    def get_chat_name(self, obj):
        if obj.is_group:
            return obj.room_name
        
        user = self.context.get('request').user
        other_participants = obj.participants.exclude(id=user.id)
        
        if other_participants.exists():
            participant = other_participants.first()
            return (participant.first_name and participant.last_name and f"{participant.first_name} {participant.last_name}") or participant.username

        return None

    @extend_schema_field(str)
    def get_group_image(self, obj):
        request = self.context.get('request')
        
        def build_absolute_url(relative_url):
            return request.build_absolute_uri(relative_url) if request and relative_url else None

        if obj.is_group:
            return build_absolute_url(obj.group_image.url if obj.group_image else None)

        user = request.user
        other_participants = obj.participants.exclude(id=user.id)
        if other_participants.exists():
            participant = other_participants.first()
            return build_absolute_url(participant.profile_pic.url if participant.profile_pic else None)

        return None

    
    @extend_schema_field(UserSerializer(many=True))
    def get_participants(self, obj):
        admin_ids = list(obj.admins.values_list('id', flat=True))
        serializer = ParticipantUserSerializer(
            obj.participants.all(),
            many=True,
            context={**self.context, 'chatroom_admin_ids': admin_ids}
        )
        return serializer.data


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
        if len(data['participant_ids']) < 2:
            raise serializers.ValidationError("You cannot include only yourself in the chat")
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
