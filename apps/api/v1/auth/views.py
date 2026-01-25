from drf_spectacular.utils import extend_schema
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView as SimpleJWTTokenRefreshView,
    TokenVerifyView as SimpleJWTTokenVerifyView,
)


@extend_schema(tags=["v1/auth"])
class TokenCreateView(TokenObtainPairView):
    pass


@extend_schema(tags=["v1/auth"])
class TokenRefreshView(SimpleJWTTokenRefreshView):
    pass


@extend_schema(tags=["v1/auth"])
class TokenVerifyView(SimpleJWTTokenVerifyView):
    pass
