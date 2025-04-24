from ..serializers import MessageSerializer, MessageCreateSerializer
from rest_framework.permissions import IsAuthenticated
from ..models import Message
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets
from ..permissions import IsMessageSender, IsRoomParticipant
from drf_spectacular.utils import extend_schema, OpenApiParameter

#for drf_spectacular documentation
@extend_schema(
    parameters=[
        OpenApiParameter(
            name='chatroom_pk',
            description='ID of the chatroom',
            required=True,
            type=int,
            location=OpenApiParameter.PATH
        )
    ]
)
class MessageViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsRoomParticipant]
    queryset = Message.objects.all()
    def get_serializer_class(self):
        if self.action == 'create':
            return MessageCreateSerializer
        return MessageSerializer
    
    def get_permissions(self):
        if self.action in['update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsMessageSender()]
        return super().get_permissions()
    
    def get_queryset(self):
        chatroom_id = self.kwargs['chatroom_pk']
        return Message.objects.filter(room_id=chatroom_id).order_by('-timestamp')

    
    def perform_create(self, serializer):
        message = serializer.save()
        
        #for communicating with websocket
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync
        
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"chat_{message.room.id}",
            {
                "type": "chat.message",
                "message": MessageSerializer(message).data
            }
        )