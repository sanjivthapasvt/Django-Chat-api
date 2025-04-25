from rest_framework import serializers
from ..models import FriendRequest, User

class FriendRequestSerializer(serializers.ModelSerializer):
    from_user = serializers.PrimaryKeyRelatedField(read_only=True)
    to_user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    status = serializers.ChoiceField(choices=FriendRequest.STATUS_CHOICES, read_only=True)

    class Meta:
        model = FriendRequest
        fields = ['id', 'from_user', 'to_user', 'status', 'created_at', 'updated_at']
        read_only_fields = ['id', 'from_user', 'status', 'created_at', 'updated_at']

    def validate(self, data):
        request = self.context.get("request")
        if request and request.user == data['to_user']:
            raise serializers.ValidationError({"detail": "Cannot send friend request to yourself"})
        return data

    def create(self, validated_data):
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            validated_data["from_user"] = request.user
        return super().create(validated_data)
