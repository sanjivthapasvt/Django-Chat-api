from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from ..models import ChatRoom, User
from django.db.models import F
from ..permissions import IsRoomAdmin, IsRoomParticipant
from ..serializers import ChatRoomCreateSerializer, ChatRoomSerializer, AddMemberSerializer, RemoveMemberSerializer
from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.filters import SearchFilter, OrderingFilter
from ..pagination import ChatCursorPagination
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json
from django.core.serializers.json import DjangoJSONEncoder


class ChatRoomViewSet(viewsets.ModelViewSet):
    # Only authenticated users can access chat rooms
    permission_classes = [IsAuthenticated]
    # Order chat rooms by last message timestamp
    queryset = ChatRoom.objects.all().order_by(F('last_message__timestamp').desc(nulls_last=True))
    # Enable search and ordering
    filter_backends = {SearchFilter, OrderingFilter}
    search_fields = ['room_name', 'participants__username']
    ordering_fields = ['room_name', 'last_message']
    ordering = ['-last_message__timestamp']
    # Use cursor pagination
    pagination_class = ChatCursorPagination

    def get_queryset(self):
        # Return chat rooms the user participates in
        return ChatRoom.objects.filter(participants=self.request.user)

    def get_serializer_class(self):
        # Use different serializer for creation
        if self.action == 'create':
            return ChatRoomCreateSerializer
        return ChatRoomSerializer

    def perform_create(self, serializer):
        # Set the creator when creating a room
        chatroom = serializer.save(creator=self.request.user)
        serialized_data = ChatRoomSerializer(chatroom, context=self.get_serializer_context()).data
        
        json_data = json.dumps(serialized_data, cls=DjangoJSONEncoder)
        safe_data = json.loads(json_data)
        # Notify all connected sidebar clients
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "sidebar",
            {
                "type": "group.update",
                "data": {
                    "type": "group_created",
                    "group": safe_data
                }
            }
        )
    @extend_schema(
        request=AddMemberSerializer,
        responses={200: ChatRoomCreateSerializer}
    )
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsRoomParticipant])
    def add_members(self, request, pk=None):
        # Add members to a group or convert private chat to group
        room = self.get_object()
        new_user_ids = request.data.get("users", [])
        user_to_add = User.objects.filter(id__in=new_user_ids)

        if not room.is_group:
            # Convert private chat to group chat
            existing_user_ids = room.participants.values_list("id", flat=True)
            duplicate_users = set(existing_user_ids).intersection(user_to_add.values_list("id", flat=True))
            
            if duplicate_users:
                return Response({"detail": "One or more users are already in the room"}, status=400)

            group_chat = ChatRoom.objects.create(
                room_name=None,
                is_group=True,
                creator=self.request.user,
            )
            group_chat.participants.set([*room.participants.all(), *user_to_add])
            group_chat.admins.set([*room.participants.all()])
            group_chat.save()
            return Response(
                ChatRoomSerializer(group_chat, context=self.get_serializer_context()).data,
                status=201
            )

        # Only admins can add members
        if request.user not in room.admins.all():
            return Response({"detail": "Only admins can add members"}, status=403)

        existing_ids = room.participants.values_list("id", flat=True)
        new_users_to_add = user_to_add.exclude(id__in=existing_ids)

        if not new_users_to_add:
            return Response({"detail": "Users are already in the room"}, status=400)

        room.participants.add(*new_users_to_add)
        return Response(ChatRoomSerializer(room, context=self.get_serializer_context()).data)

    @extend_schema(
        request=RemoveMemberSerializer,
        responses={200: ChatRoomSerializer,
                   405: OpenApiResponse(description="Cannot remove member from private chat")
                   })
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsRoomAdmin])
    def remove_member(self, request, pk=None):
        # Remove a member from a group chat
        room = self.get_object()

        if not room.is_group:
            raise MethodNotAllowed(method='POST', detail="Cannot remove members in private chat.")

        user_id = request.data.get("user_id")
        if not user_id:
            return Response({"detail": "User ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        if user_id == request.user.id:
            return Response({"detail": "You cannot remove yourself from the room."},
                            status=status.HTTP_400_BAD_REQUEST)

        user = get_object_or_404(User, id=user_id)

        if user not in room.participants.all():
            return Response({"detail": "User is not a participant in this room."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Prevent removing the last admin
        if user in room.admins.all() and room.admins.count() == 1:
            return Response({"detail": "You cannot remove the last admin."},
                            status=status.HTTP_400_BAD_REQUEST)

        room.participants.remove(user)
        room.admins.remove(user)

        return Response({"detail": "User removed successfully."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated, IsRoomParticipant])
    def participants(self, request, pk=None):
        # List participants with admin status
        room = self.get_object()
        data = []
        for user in room.participants.all():
            data.append({
                "id": user.id,
                "username": user.username,
                "is_admin": user in room.admins.all(),
            })
        return Response(data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsRoomParticipant])
    def leave_room(self, request, pk=None):
        # Allow a user to leave a group chat
        room = self.get_object()
        
        user = request.user
        
        if user not in room.participants.all():
            return Response({"detail": "You are not a participant of this room."}, status=status.HTTP_400_BAD_REQUEST)

        # Prevent last admin from leaving
        if user in room.admins.all() and room.admins.count() == 1:
            return Response({"detail": "Please assign a new admin before leaving."}, status=status.HTTP_400_BAD_REQUEST)
            
        room.participants.remove(user)
        room.admins.remove(user)
        return Response({"detail": "Successfully left the room"}, status=status.HTTP_200_OK)

    @extend_schema(
        request=RemoveMemberSerializer,
        responses={200: ChatRoomSerializer,
                   405: OpenApiResponse(description="Cannot assign admin in private chat")
                   }
    )
    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated, IsRoomAdmin])
    def assign_admin(self, request, pk=None):
        # Assign a new admin in group chat
        room = self.get_object()
        if not room.is_group:
            raise MethodNotAllowed(detail="Cannot assign admin in private chat")
        
        user_id = request.data.get("user_id")
        user = get_object_or_404(User, id=user_id)

        if user not in room.participants.all():
            return Response({"detail": "User is not a participant."}, status=400)

        room.admins.add(user)
        return Response({"detail": f"{user.username} is now an admin."})

    @action(detail=True, methods=["get"], permission_classes=[IsAuthenticated, IsRoomParticipant])
    def shareable_link(self, request, pk=None):
        # Get the room's shareable link ID
        room = self.get_object()
        return Response({"room_id": room.sharable_room_id})
