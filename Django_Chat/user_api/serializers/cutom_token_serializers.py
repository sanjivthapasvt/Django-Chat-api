# myapp/serializers.py
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth import get_user_model

User = get_user_model()

class CustomTokenRefreshSerializer(TokenRefreshSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        
        access = AccessToken(data['access'])
        user_id = access['user_id']
        user = User.objects.get(id=user_id)

        data['username'] = user.username

        return data
