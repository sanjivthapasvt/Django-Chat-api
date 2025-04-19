from rest_framework.permissions import BasePermission

class IsRoomParticipant(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user in obj.participants.all()
    
class IsRoomAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user in obj.admins.all()

class IsMessageSender(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.sender == request.user
    
