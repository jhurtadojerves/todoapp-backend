from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = User.EMAIL_FIELD

    @classmethod
    def get_token(cls, user: User):  # type: ignore
        token = super().get_token(user)
        token["username"] = user.username
        token["email"] = user.email
        return token

    def validate(self, attrs):
        email = attrs.get("email")
        if email:
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                raise ValidationError("Invalid email or password")
            attrs[self.username_field] = email
            attrs["username"] = user.get_username()
            self.user = user
        data = super().validate(attrs)
        data["user"] = {
            "id": self.user.id,
            "username": self.user.username,
            "email": self.user.email,
        }
        data["email"] = self.user.email
        data["username"] = self.user.username
        return data


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()


class DetailResponseSerializer(serializers.Serializer):
    detail = serializers.CharField()


class PasswordValidationSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        password = attrs.get("password")
        user = None
        try:
            validate_password(password, user=user)
        except DjangoValidationError as exc:
            raise serializers.ValidationError({"password": exc.messages})
        return attrs
