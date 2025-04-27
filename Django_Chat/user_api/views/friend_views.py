from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.core.exceptions import ValidationError
from django.db.models import Q
from ..models import FriendRequest, User
from ..serializers import FriendRequestSerializer, UserSerializer
from chat_room.models import ChatRoom
from rest_framework.filters import SearchFilter, OrderingFilter

class FriendRequestViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = FriendRequestSerializer
    queryset = FriendRequest.objects.all()
    def get_queryset(self):
        user = self.request.user
        return FriendRequest.objects.filter(Q(from_user=user) | Q(to_user=user))

    def perform_create(self, serializer):
        serializer.save(from_user=self.request.user)

    def _validate_request_target(self, request, friend_request):
        if friend_request.to_user != request.user:
            return Response(
                {"error": "You can only modify friend requests sent to you."},
                status=status.HTTP_403_FORBIDDEN
            )
        return None

    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        friend_request = self.get_object()
        permission_error = self._validate_request_target(request, friend_request)
        if permission_error:
            return permission_error

        try:
            friend_request.accept()
            chat_room = ChatRoom.objects.create(
                room_name=f"{request.user.username}_{friend_request.from_user.username}"
            )
            chat_room.participants.set([request.user, friend_request.from_user])
            return Response({"detail": "Friend request accepted."}, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        friend_request = self.get_object()
        permission_error = self._validate_request_target(request, friend_request)
        if permission_error:
            return permission_error

        try:
            friend_request.reject()
            return Response({"detail": "Friend request rejected."}, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        friend_request = self.get_object()
        if friend_request.from_user != request.user:
            return Response({"error": "You can only cancel requests you sent."}, status=status.HTTP_403_FORBIDDEN)

        if friend_request.status != 'pending':
            return Response({"error": "Only pending requests can be cancelled."}, status=status.HTTP_400_BAD_REQUEST)

        friend_request.delete()
        return Response({"detail": "Friend request cancelled."}, status=status.HTTP_200_OK)
    
    
class FriendViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    @action(detail=False, methods=['get'])
    def list_friends(self, request):
        search = request.query_params.get("search")
        friends = request.user.friends.all()
        if search:
            friends = friends.filter(username__icontains=search)

        serialized_friends = self.serializer_class(friends, many=True).data
        return Response(serialized_friends, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path=r'mutual_friends/(?P<user_id>\d+)')
    def mutual_friends(self, request, user_id=None):
        try:
            other_user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        user_friend_ids = set(request.user.friends.values_list('id', flat=True))
        other_friend_ids = set(other_user.friends.values_list('id', flat=True))
        mutual_ids = user_friend_ids & other_friend_ids

        mutual = User.objects.filter(id__in=mutual_ids)
        serialized_mutual = self.serializer_class(mutual, many=True).data
        return Response(serialized_mutual, status=status.HTTP_200_OK)
