from drf_spectacular.utils import extend_schema
from rest_framework import permissions, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView as SimpleJWTTokenRefreshView
from rest_framework_simplejwt.views import TokenVerifyView as SimpleJWTTokenVerifyView

from apps.api.v1.auth.serializers import (
    DetailResponseSerializer,
    LogoutSerializer,
    PasswordValidationSerializer,
)


@extend_schema(tags=["v1/auth"])
class TokenCreateView(TokenObtainPairView):
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "login"


@extend_schema(tags=["v1/auth"])
class TokenRefreshView(SimpleJWTTokenRefreshView):
    pass


@extend_schema(tags=["v1/auth"])
class TokenVerifyView(SimpleJWTTokenVerifyView):
    pass


@extend_schema(tags=["v1/auth"], request=LogoutSerializer, responses={205: None})
class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            token = RefreshToken(serializer.validated_data["refresh"])
            token.blacklist()
        except TokenError:
            raise ValidationError({"refresh": "Invalid or expired token."})
        return Response(status=status.HTTP_205_RESET_CONTENT)


@extend_schema(
    tags=["v1/auth"],
    request=PasswordValidationSerializer,
    responses={200: DetailResponseSerializer},
)
class PasswordValidationView(APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = PasswordValidationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(
            {"detail": "Password meets the requirements."}, status=status.HTTP_200_OK
        )
