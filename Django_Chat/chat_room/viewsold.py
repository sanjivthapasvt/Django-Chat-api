from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from .models import ChatRoom, User
from .permissions import IsRoomAdmin, IsRoomParticipant
from .serializers import (
    ChatRoomCreateSerializer,
    ChatRoomSerializer,
    BasicMessageSerializer,
    TypingStatusSerializer,
    MessageReadStatusSerializer,
    NotificationSerializer,
    MessageSerializer,
    MessageCreateSerializer
)

class ChatRoomViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ChatRoom.objects.filter(participants=self.request.user)

    def get_serializer_class(self):
        if self.action == 'create':
            return ChatRoomCreateSerializer
        return ChatRoomSerializer

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)

    @action(detail=True, methods=['POST'], permission_classes=[IsAuthenticated, IsRoomParticipant])
    def add_members(self, request, pk=None):
        room = self.get_object()
        new_users = request.data.get("users", [])
        user_to_add = User.objects.filter(id__in=new_users)

        if not room.is_group:
            group_chat = ChatRoom.objects.create(
                room_name=None,
                is_group=True,
                creator=self.request.user,
            )
            group_chat.participants.set([*room.participants.all(), *user_to_add])
            group_chat.admins.set([*room.participants.all()])
            group_chat.save()
            return Response(ChatRoomCreateSerializer(group_chat, context=self.get_serializer_context()).data)

        if self.request.user not in room.admins.all():
            return Response({"detail": "Only admins can add members"}, status=403)

        room.participants.add(*user_to_add)
        return Response({"detail": "User(s) added successfully"})

    @action(detail=True, methods=['POST'], permission_classes=[IsAuthenticated, IsRoomAdmin])
    def remove_member(self, request, pk=None):
        room = self.get_object()
        user_id = request.data.get("user_id")

        if user_id == self.request.user.id:
            return Response({"detail": "Cannot remove yourself"})

        user = get_object_or_404(User, id=user_id)
        room.participants.remove(user)
        room.admins.remove(user)
        return Response({"detail": "User removed successfully"})

    @action(detail=True, methods=['GET'], permission_classes=[IsAuthenticated, IsRoomParticipant])
    def participants(self, request, pk=None):
        room = self.get_object()
        data = []
        for user in room.participants.all():
            data.append({
                "id": user.id,
                "username": user.username,
                "is_admin": user in room.admins.all(),
            })
        return Response(data)

    @action(detail=True, methods=["POST"], permission_classes=[IsAuthenticated, IsRoomAdmin])
    def assign_admin(self, request, pk=None):
        room = self.get_object()
        user_id = request.data.get("user_id")
        user = get_object_or_404(User, id=user_id)

        if user not in room.participants.all():
            return Response({"detail": "User is not a participant."}, status=400)

        room.admins.add(user)
        return Response({"detail": f"{user.username} is now an admin."})

    @action(detail=True, methods=["GET"], permission_classes=[IsAuthenticated, IsRoomParticipant])
    def shareable_link(self, request, pk=None):
        room = self.get_object()
        return Response({"room_id": room.id})
