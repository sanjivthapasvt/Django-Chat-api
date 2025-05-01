from rest_framework.permissions import BasePermission

# Checks if user is a participant in a room
class IsRoomParticipant(BasePermission):
    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'participants'):
            return request.user in obj.participants.all()
        elif hasattr(obj, 'room'):
            # For message objects that belong to a room
            return request.user in obj.room.participants.all()

# Checks if user is an admin of a room
class IsRoomAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user in obj.admins.all()

# Checks if user is the sender of a message
class IsMessageSender(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.sender == request.user