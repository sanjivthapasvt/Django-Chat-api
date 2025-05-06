from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.db import transaction, IntegrityError
from ..models import FriendRequest, User
from ..serializers import FriendRequestSerializer, UserSerializer
from chat_room.models import ChatRoom


class FriendRequestViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = FriendRequestSerializer
    http_method_names = ["post", "get"]
    queryset = FriendRequest.objects.all()

    def get_queryset(self):
        user = self.request.user
        return FriendRequest.objects.filter(Q(from_user=user) | Q(to_user=user))

    def create(self, request, *args, **kwargs):
        # checking if the to_user exists
        to_user_id = request.data.get('to_user')
        try:
            to_user = User.objects.get(id=to_user_id)
        except User.DoesNotExist:
            return Response(
                {"error": "Recipient user not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if request.user.id == to_user.id:
            return Response(
                {"error": "You cannot send a friend request to yourself."},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # checking if already friends
        if request.user.friends.filter(id=to_user.id).exists():
            return Response(
                {"error": "You are already friends with this user."},
                status=status.HTTP_409_CONFLICT
            )
            
        # Check if the request is already pending
        if FriendRequest.objects.filter(
            from_user=request.user,
            to_user=to_user,
            status='pending'
        ).exists():
            return Response(
                {"error": "You already have a pending request to this user."},
                status=status.HTTP_409_CONFLICT
            )
            
        # Check if there's a pending request from the other user
        existing_request = FriendRequest.objects.filter(
            from_user=to_user,
            to_user=request.user,
            status='pending'
        ).first()
        
        if existing_request:
            return Response(
                {"error": "This user has already sent you a friend request. Please accept or reject it instead."},
                status=status.HTTP_409_CONFLICT
            )
            
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        try:
            serializer.save(from_user=self.request.user)
        except IntegrityError:
            raise ValidationError("Friend request could not be created due to database constraints.")

    def _validate_request_target(self, request, friend_request):
        # Checking if request exists
        if not friend_request:
            return Response(
                {"error": "Friend request not found."},
                status=status.HTTP_404_NOT_FOUND
            )
            
        # Checking if the request is pending
        if friend_request.status != 'pending':
            status_text = 'accepted' if friend_request.status == 'accepted' else 'rejected'
            return Response(
                {"error": f"This friend request has already been {status_text}."},
                status=status.HTTP_410_GONE
            )
            
        if friend_request.to_user != request.user:
            return Response(
                {"error": "You can only modify friend requests sent to you."},
                status=status.HTTP_403_FORBIDDEN
            )
        return None

    @action(detail=True, methods=['POST'])
    def accept(self, request, pk=None):
        try:
            friend_request = self.get_object()
        except Exception:
            return Response(
                {"error": "Friend request not found."},
                status=status.HTTP_404_NOT_FOUND
            )
            
        permission_error = self._validate_request_target(request, friend_request)
        if permission_error:
            return permission_error

        try:
            with transaction.atomic():
                friend_request.accept()
                chat_room = ChatRoom.objects.create(
                    room_name=f"{request.user.username}_{friend_request.from_user.username}"
                )
                chat_room.participants.set([request.user, friend_request.from_user])
            return Response({"detail": "Friend request accepted."}, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"error": f"An unexpected error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['POST'])
    def reject(self, request, pk=None):
        try:
            friend_request = self.get_object()
        except Exception:
            return Response(
                {"error": "Friend request not found."},
                status=status.HTTP_404_NOT_FOUND
            )
            
        permission_error = self._validate_request_target(request, friend_request)
        if permission_error:
            return permission_error

        try:
            friend_request.reject()
            return Response({"detail": "Friend request rejected."}, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"error": f"An unexpected error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['POST'])
    def cancel(self, request, pk=None):
        try:
            friend_request = self.get_object()
        except Exception:
            return Response(
                {"error": "Friend request not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        if friend_request.from_user != request.user:
            return Response(
                {"error": "You can only cancel requests you sent."},
                status=status.HTTP_403_FORBIDDEN
            )

        if friend_request.status != 'pending':
            status_text = 'accepted' if friend_request.status == 'accepted' else 'rejected'
            return Response(
                {"error": f"This request has already been {status_text} and cannot be cancelled."},
                status=status.HTTP_410_GONE
            )

        try:
            friend_request.delete()
            return Response({"detail": "Friend request cancelled."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": f"An unexpected error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    
class FriendViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer
    
    @action(detail=False, methods=['get'])
    def list_friends(self, request):
        try:
            search = request.query_params.get("search")
            friends = request.user.friends.all()
            if search:
                friends = friends.filter(username__icontains=search)

            serialized_friends = self.serializer_class(friends, many=True).data
            return Response(serialized_friends, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": f"An unexpected error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def retrieve(self, request, pk=None):
        try:
            friend = request.user.friends.filter(pk=pk).first()
            if not friend:
                return Response({"error": "Friend not found."}, status=status.HTTP_404_NOT_FOUND)

            serialized_friend = self.serializer_class(friend).data
            return Response(serialized_friend, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": f"An unexpected error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
    @action(detail=True, methods=['post'])
    def remove_friend(self, request, pk=None):
        try:
            friend = User.objects.get(id=pk)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found."},
                status=status.HTTP_404_NOT_FOUND
            )            
        # Checking if they are actually friends
        if not request.user.friends.filter(id=friend.id).exists():
            return Response(
                {"error": "This user is not in your friends list."},
                status=status.HTTP_400_BAD_REQUEST
            )
                
        # Remove the friends
        with transaction.atomic():
            request.user.friends.remove(friend)
            friend.friends.remove(request.user)
        #to delete the relation with friend
        FriendRequest.objects.filter(
            from_user=request.user, to_user=friend, status='accepted'
        ).delete()

        FriendRequest.objects.filter(
            from_user=friend, to_user=request.user, status='accepted'
        ).delete()
        return Response(
            {"detail": f"Successfully removed {friend.username} from your friends list."},
            status=status.HTTP_200_OK
        )