# myapp/serializers.py
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth import get_user_model

User = get_user_model()

# serializers.py
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class MyTokenRefreshSerializer(TokenRefreshSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        refresh = RefreshToken(attrs['refresh'])
        user_id = refresh['user_id']
        
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise InvalidToken("User not found")

        access = AccessToken.for_user(user)
        access['username'] = user.username

        data['access'] = str(access)
        return data
