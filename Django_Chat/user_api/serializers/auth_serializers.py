from ..models import User
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate


class UserSerializer(serializers.ModelSerializer):
    """Serializer for basic user information"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'profile_pic']
        read_only_fields = ['id', 'username', 'email']
        
class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password', 'confirm_password']

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username is already taken.")
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email is already in use.")
        return value

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user



class UserLoginSerializer(serializers.Serializer):
    identifier = serializers.CharField()  # username or email
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        identifier = data.get('identifier')
        password = data.get('password')

        user = authenticate(username=identifier, password=password)
        if not user:
            raise serializers.ValidationError("Invalid login credentials.")

        data['user'] = user
        return data



class LogoutSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()



class UserProfileUpdateSerializer(serializers.ModelSerializer):
    old_password = serializers.CharField(write_only=True, required=False)
    new_password = serializers.CharField(write_only=True, required=False)
    confirm_password = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "profile_pic", "old_password", "new_password", "confirm_password"]

    def validate(self, data):
            # Check if any password field is provided
            if any(field in data for field in ['old_password', 'new_password', 'confirm_password']):
                user = self.instance

                if not user.check_password(data.get('old_password', '')):
                    raise serializers.ValidationError({'old_password': 'Old password is incorrect.'})

                if data.get('new_password') != data.get('confirm_password'):
                    raise serializers.ValidationError({'confirm_password': 'New passwords do not match.'})

                validate_password(data['new_password'], user)

            return data

    def update(self, instance, validated_data):
        # Remove password fields from the update
        validated_data.pop('old_password', None)
        new_password = validated_data.pop('new_password', None)
        validated_data.pop('confirm_password', None)

        # Update basic fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # Update password if provided
        if new_password:
            instance.set_password(new_password)

        instance.save()
        return instance