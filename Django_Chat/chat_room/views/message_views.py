from ..serializers import MessageCreateSerializer, MessageReadStatusSerializer, MessageSerializer, TypingStatusSerializer
from rest_framework.permissions import IsAuthenticated
from ..models import Message
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import viewsets
from ..permissions import IsMessageSender, IsRoomParticipant
class MessageViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsRoomParticipant]
    queryset = Message.objects.all()
    @action(detail=True, methods=["GET"], permission_classes=[IsAuthenticated, IsRoomParticipant])
    def list(self, request):
        message = self.get_object()