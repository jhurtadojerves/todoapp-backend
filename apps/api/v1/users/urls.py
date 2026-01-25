from django.urls import path

from apps.api.v1.users.views import UserListAPIView, UserRegistrationAPIView


urlpatterns = [
    path("register/", UserRegistrationAPIView.as_view(), name="user_register"),
    path("", UserListAPIView.as_view(), name="user_list"),
]
