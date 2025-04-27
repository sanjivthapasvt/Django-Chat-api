from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from ..permissions import IsRoomParticipant
from ..models import Notification
from ..serializers import NotificationSerializer
from rest_framework.filters import OrderingFilter, SearchFilter
class NotificationViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsRoomParticipant]
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    filter_backends = (OrderingFilter, SearchFilter)
    search_fields = ['notification_type']
    odering_fields = ['timestamp']
    ordering = ['-timestamp']
    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by('-timestamp')
    
    @action(detail=False, methods=['get'])
    def unread(self, request):
        unread_notifications = Notification.objects.filter(
            user = self.request.user,
            is_read = False
        ).order_by('-timestamp')
        serializer = self.get_serializer(unread_notifications, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return Response(status=status.HTTP_204_NO_CONTENT)