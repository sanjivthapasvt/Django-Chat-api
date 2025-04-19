from rest_framework import viewsets
from .models import ChatRoom
from .serializers import ChatRoomSerializer, ChatRoomCreateSerializer
from rest_framework.permissions import IsAuthenticated
from .permissions import IsRoomAdmin, IsRoomParticipant, IsMessageSender
class ChatRoomViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # only return rooms the current user is a participant in
        return ChatRoom.objects.filter(participants=self.request.user)

    def get_serializer_class(self):
        if self.action == 'create':
            return ChatRoomCreateSerializer
        return ChatRoomSerializer

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)
