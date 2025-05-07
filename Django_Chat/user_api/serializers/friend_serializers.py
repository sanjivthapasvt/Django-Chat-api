from rest_framework import serializers
from ..models import FriendRequest, User

class FriendRequestSerializer(serializers.ModelSerializer):
    from_user = serializers.PrimaryKeyRelatedField(read_only=True)
    to_user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False)
    status = serializers.ChoiceField(choices=FriendRequest.STATUS_CHOICES, read_only=True)

    class Meta:
        model = FriendRequest
        fields = ['id', 'from_user', 'to_user', 'status', 'created_at', 'updated_at']
        read_only_fields = ['id', 'status', 'created_at', 'updated_at']

    def validate(self, data):
        request = self.context.get("request")
        if request and request.path.endswith(('accept/', 'cancel/', 'reject/')):
            return data
        
        if 'to_user' not in data:
            raise serializers.ValidationError({"to_user": "This field is required."})
        
        if request and request.user == data['to_user']:
            raise serializers.ValidationError({"detail": "Cannot send friend request to yourself"})
        return data

    def create(self, validated_data):
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            validated_data["from_user"] = request.user
        return super().create(validated_data)
