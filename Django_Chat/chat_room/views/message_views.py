from ..serializers import MessageSerializer, MessageCreateSerializer, MessageReadStatusSerializer
from rest_framework.permissions import IsAuthenticated
from ..models import Message, MessageReadStatus
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets
from ..permissions import IsMessageSender, IsRoomParticipant
from rest_framework.decorators import action
from rest_framework.response import Response
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from rest_framework.filters import SearchFilter, OrderingFilter
from ..pagination import MessageCursorPagination

# Add chatroom ID parameter for API docs
@extend_schema(
    parameters=[
        OpenApiParameter(
            name='chatroom_pk',
            description='ID of the chatroom',
            type=int,
            location=OpenApiParameter.PATH
        )
    ]
)
class MessageViewSet(viewsets.ModelViewSet):
    # Only authenticated room participants can access messages
    permission_classes = [IsAuthenticated, IsRoomParticipant]
    queryset = Message.objects.all()
    filter_backends = (SearchFilter, OrderingFilter)
    search_fields = ['content', 'sender']
    ordering_fields = ['timestamp', 'id']
    ordering = ['-timestamp', '-id']
    pagination_class = MessageCursorPagination

    def get_serializer_class(self):
        # Use create serializer when creating message
        if self.action == 'create':
            return MessageCreateSerializer
        return MessageSerializer

    def get_permissions(self):
        # Only sender can update/delete their messages
        if self.action in ['update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsMessageSender()]
        return super().get_permissions()

    def get_queryset(self):
        # Return messages for a specific chatroom
        chatroom_id = self.kwargs['chatroom_pk']
        return Message.objects.filter(room_id=chatroom_id).order_by('-timestamp')

    def perform_create(self, serializer):
        # Save message and send it via WebSocket
        message = serializer.save()
        channel_layer = get_channel_layer()

        # Notify room for message
        async_to_sync(channel_layer.group_send)(
            f"chat_{message.room.id}",
            {
                "type": "chat.message",
                "message": MessageSerializer(message).data
            }
        )

        # Notify sidebar to update last message preview
        async_to_sync(channel_layer.group_send)(
            "sidebar",
            {
                "type": "group.update",
                "data": {
                    "type": "group_message_updated",
                    "group_id": message.room.id,
                    "last_message": {
                        "id": message.id,
                        "text": message.content,
                        "sender": message.sender.username,
                        "timestamp": message.timestamp.isoformat()
                    }
                }
            }
        )

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsRoomParticipant])
    def mark_as_read(self, request, pk=None):
        # Mark a message as read by a user (excluding sender)
        message = self.get_object()
        
        if message.sender == request.user:
            return Response({"detail": "Sender cannot mark own message as read"})

        read_status, created = MessageReadStatus.objects.get_or_create(
            message=message,
            user=request.user
        )

        # Send read status over WebSocket if newly created
        if created:
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"chatroom_{message.room.id}",
                {
                    "type": "message.read",
                    "message_id": message.id,
                    "reader": {
                        "id": request.user.id,
                        "username": request.user.username,
                    },
                    "read_at": read_status.timestamp.isoformat()
                }
            )
        serializer = MessageReadStatusSerializer(read_status)
        return Response(serializer.data, status=201 if created else 200)

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated, IsRoomParticipant])
    def message_read_status(self, request, pk=None):
        # Get list of users who read the message
        message = self.get_object()
        read_statuses = message.readstatuses.select_related('user')
        serializer = MessageReadStatusSerializer(read_statuses, many=True)
        return Response(serializer.data)
