"""User model."""

# Django
from typing import Optional
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    created = models.DateTimeField(
        verbose_name="created at",
        auto_now_add=True,
        help_text="Datetime on which the user was created",
    )
    modified = models.DateTimeField(
        verbose_name="modified at",
        auto_now=True,
        help_text="Datetime on which the user was last modified",
    )
    email = models.EmailField(verbose_name="email address", unique=True)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    @property
    def profile(self) -> Optional["Profile"]:
        if hasattr(self, "set_profile"):
            return self.set_profile
        return None


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)

    def __str__(self) -> str:
        return f"Profile of {self.user.username}"
