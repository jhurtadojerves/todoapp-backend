from django.urls import include, path

urlpatterns = [
    path("auth/", include("apps.api.v1.auth.urls")),
    path("users/", include("apps.api.v1.users.urls")),
    path("", include("apps.api.v1.todos.urls")),
]
