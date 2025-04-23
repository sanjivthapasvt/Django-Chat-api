from rest_framework.permissions import BasePermission

class IsRoomParticipant(BasePermission):
    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'participants'):
            return request.user in obj.participants.all()
        elif hasattr(obj, 'room'):
            #check if user is participant in the message room
            return request.user in obj.room.participants.all()
        
class IsRoomAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user in obj.admins.all()

class IsMessageSender(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.sender == request.user
    