from drf_spectacular.utils import extend_schema
from rest_framework import generics, permissions

from apps.api.v1.users.serializers import (
    UserListSerializer,
    UserRegistrationSerializer,
)
from apps.users.models import User


@extend_schema(tags=["v1/users"])
class UserRegistrationAPIView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]


@extend_schema(tags=["v1/users"])
class UserListAPIView(generics.ListAPIView):
    serializer_class = UserListSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = User.objects.all()
