from django.urls import path

from apps.api.v1.auth.views import (
    TokenCreateView,
    TokenRefreshView,
    TokenVerifyView,
)


urlpatterns = [
    path("token/", TokenCreateView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
]
