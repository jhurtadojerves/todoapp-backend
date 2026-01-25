from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.users.dtos.user import UserData
from apps.users.models import Profile
from apps.users.dtos.profile import ProfileData
from apps.users.services.user import UserService


User = get_user_model()


class ProfileInputSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ["bio"]
        extra_kwargs = {
            "bio": {
                "required": False,
                "allow_blank": True,
            },
        }


class ProfileOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ["bio"]
        read_only_fields = fields


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    profile = ProfileInputSerializer(required=False)

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "first_name",
            "last_name",
            "password",
            "profile",
        ]

    def create(self, validated_data):
        profile_data = validated_data.pop("profile", None)
        profile_payload = ProfileData(**profile_data) if profile_data else None
        user_data = UserData(**validated_data)

        return UserService.register(user_data=user_data, profile_data=profile_payload)


class UserListSerializer(serializers.ModelSerializer):
    profile = ProfileOutputSerializer(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "date_joined",
            "profile",
        ]
