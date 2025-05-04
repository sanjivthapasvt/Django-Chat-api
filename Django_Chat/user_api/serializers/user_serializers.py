from ..models import User
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate
from django.core.cache import cache
from django_redis import get_redis_connection


class UserSerializer(serializers.ModelSerializer):
    online_status = serializers.SerializerMethodField()
    last_seen = serializers.SerializerMethodField()
    bio = serializers.CharField()
    friends = serializers.PrimaryKeyRelatedField(
        many=True, read_only=True
    )
    class Meta:
        model = User
        fields = ['id', 'username','bio', 'email', 'first_name', 'last_name','friends', 'profile_pic','online_status', 'last_seen']
        read_only_fields = ['id', 'username', 'email']
    
    def get_online_status(self, obj) -> bool:
        conn = get_redis_connection("default")
        return conn.get(f"user:{obj.id}:online") == b"1"
    

    def get_last_seen(self, obj) -> str:
        conn = get_redis_connection("default")
        last_seen = conn.get(f"user:{obj.id}:last_seen")
        if last_seen:
            import datetime
            return datetime.datetime.fromisoformat(last_seen.decode())
        return None
        
class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'confirm_password']

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
    bio = serializers.CharField()
    class Meta:
        model = User
        fields = ["first_name", 'bio', "last_name", "email", "profile_pic", "old_password", "new_password", "confirm_password"]
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
    
class ListUserSerializer(serializers.ModelSerializer):
    bio = serializers.CharField()
    friends = serializers.PrimaryKeyRelatedField(
        many=True, read_only=True
    )
    class Meta:
        model = User
        fields = ['id', 'username','bio', 'email', 'first_name', 'last_name','friends', 'profile_pic']