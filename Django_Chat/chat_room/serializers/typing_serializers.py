from rest_framework import serializers
from ..models import TypingStatus
from .user_serializers import BasicUserSerializer

class TypingStatusSerializer(serializers.ModelSerializer):
    user = BasicUserSerializer(read_only=True)
    
    class Meta:
        model = TypingStatus
        fields = ['id', 'room', 'user', 'timestamp']
        read_only_fields = ['timestamp']
