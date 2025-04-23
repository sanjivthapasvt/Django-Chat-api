from ..serializers import MessageSerializer
from rest_framework.permissions import IsAuthenticated
from ..models import Message

from rest_framework import viewsets
from ..permissions import IsMessageSender, IsRoomParticipant
class MessageViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsRoomParticipant]
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    
    def get_permissions(self):
        if self.action in['update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsMessageSender()]
        return super().get_permissions()
    
    
    def get_queryset(self):
        room_id = self.request.query_params.get("room_id")
        return Message.objects.filter(room_id=room_id).order_by('timestamp')